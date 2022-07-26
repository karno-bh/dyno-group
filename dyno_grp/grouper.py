from typing import Optional

import dyno_grp.utils as utils

from dyno_grp.streams import CsvDictStream
from dyno_grp.definitions import GroupRule
from dyno_grp.errors import ProcessException


class Grouper:
    def __init__(self, data_stream, group_rule: GroupRule) -> None:
        super().__init__()
        self._data_stream = data_stream
        self._group_rule: GroupRule = group_rule
        self._result: Optional[dict] = None

    def _validate_row_correlation(self, row: dict):
        self._group_rule.select_clause.validate_correlation(row.keys())

    def _filter_row(self, row):
        return row

    def _rename_row_keys(self, row:dict):
        renamed_row = dict()
        for k, v in row.items():
            column = self._group_rule.select_clause.get(k)
            k = column.alias if column else k
            renamed_row[k] = v
        return renamed_row

    def _group_by(self, item, item_key, receiver):
        result_columns = self._group_rule.select_clause.alias_set - {item_key}
        group_key = item[item_key]
        if receiver.get(group_key, None) is None:
            receiver[group_key] = []
        receiver[group_key].append(utils.filter_dict(item, *result_columns, include=True))

    def _process_row_first_pass(self, row: dict):
        first_group, first_group_def = next(iter(self._group_rule.group_clause.items()))
        row = self._rename_row_keys(row)
        self._group_by(row, first_group, self._result)

    def _process_group(self, level, groups, bucket_path):
        if level == len(groups):
            return
        items_in_group = None
        upset_group = None
        for i, bucket in enumerate(bucket_path):
            upset_group = self._result if i == 0 else items_in_group
            items_in_group = upset_group[bucket]
        new_group = upset_group[bucket_path[-1]] = dict()
        upset_group_rules = groups[level - 1]
        if upset_group_rules.aggregated_property:
            non_similar_items = new_group[upset_group_rules.aggregated_property] = list()
            for item_idx, item in enumerate(items_in_group):
                aggregated_property_item = dict()
                for k, v in item.items():
                    if k in upset_group_rules.similar_items:
                        if item_idx == 0:
                            new_group[k] = v
                        elif new_group[k] != v:
                            raise ProcessException(f"Cannot combine similar items for Column Alias {k}. "
                                                   f"Found different values '{new_group[k]}' and '{v}'")
                    else:
                        aggregated_property_item[k] = v
                non_similar_items.append(aggregated_property_item)
            bucket_path += [upset_group_rules.aggregated_property]
            items_in_group = new_group[upset_group_rules.aggregated_property]
            new_group = new_group[upset_group_rules.aggregated_property] = dict()
        group_name = groups[level].group_name
        for item in items_in_group:
            self._group_by(item, group_name, new_group)
        for group in new_group:
            self._process_group(level + 1, groups, bucket_path + [group])

    def _process_non_first_passes(self):
        groups = [group for _, group in self._group_rule.group_clause.items()]
        for bucket_path in self._result:
            self._process_group(1, groups, [bucket_path])

    def __call__(self, *args, **kwargs):
        self._result = dict()
        with self._data_stream:
            data_stream_iter = iter(self._data_stream)
            row = next(data_stream_iter, None)
            if row is None:
                raise ProcessException("There is no data in the stream")
            self._validate_row_correlation(row)
            self._process_row_first_pass(row)
            while True:
                try:
                    row = next(data_stream_iter)
                    self._process_row_first_pass(row)
                except StopIteration:
                    break
        self._process_non_first_passes()
        print(self._result)

    @staticmethod
    def csv_to_json_grouper(csv_file, definitions):
        stream = CsvDictStream(csv_file)
        group_rule = GroupRule.from_raw(definitions)
        return Grouper(stream, group_rule)
