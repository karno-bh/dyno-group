"""
This module aggregates the "grammar" definitions for the clauses of a definition for grouper
"""
from collections import OrderedDict
from typing import Optional, Dict

from dyno_grp.errors import ClauseException


class Column:
    def __init__(self, name, alias=None) -> None:
        super().__init__()
        if not isinstance(name, str) or not name:
            raise ClauseException("Column Name should be non-empty string")
        if alias and not isinstance(alias, str):
            raise ClauseException("If Column Alias is defined it should be non-empty string")
        self._column_name: str = name
        self._column_alias: Optional[str] = alias

    @property
    def name(self):
        return self._column_name

    @property
    def alias(self):
        if self._column_alias:
            return self._column_alias
        else:
            return self._column_name

    def __repr__(self):
        return f"Column('{self._column_name}', '{self._column_alias}')"


class SelectClause:
    def __init__(self, columns: [Column]) -> None:
        super().__init__()
        self._validate_columns(columns=columns)
        self._columns = columns
        self._columns_cache = {col.name: col for col in columns}

    def __len__(self):
        return len(self._columns)

    def __getitem__(self, item) -> Column:
        if isinstance(item, int):
            return self._columns[item]
        if isinstance(item, str):
            return self._columns_cache[item]
        raise KeyError(f"Cannot retrieve {item}")

    def __iter__(self):
        return self._columns.__iter__()

    def __repr__(self):
        return f"SelectClause({repr(self._columns)})"

    @staticmethod
    def _validate_columns(columns):
        if not columns:
            raise ClauseException("Columns must not be empty")
        column_names = set()
        column_aliases = set()
        duplicated_names = set()
        duplicated_aliases = set()
        for i, col in enumerate(columns):
            if not isinstance(col, Column):
                raise ClauseException(f"Column at index {i} is not of type column")
            if col.name in column_names:
                duplicated_names.add(col.name)
            if col.alias in column_aliases:
                duplicated_aliases.add(col.alias)
            column_names.add(col.name)
            column_aliases.add(col.alias)
        if duplicated_aliases or duplicated_names:
            res_exception_str = "There are duplications in column definitions."
            if duplicated_names:
                res_exception_str += f" Duplicated Names: {duplicated_names}."
            if duplicated_aliases:
                res_exception_str += f" Duplicated Aliases: {duplicated_aliases}."
            raise ClauseException(res_exception_str)


class WhereClause:
    def __init__(self) -> None:
        super().__init__()


class GroupDef:
    def __init__(self,
                 group_name: str,
                 collect_similar: bool = False,
                 aggregated_property: str = None) -> None:
        super().__init__()
        if not group_name or not isinstance(group_name, str):
            raise ClauseException("Group Name must be non empty string")
        if not isinstance(collect_similar, bool):
            raise ClauseException("Collect Similar must be boolean")
        if collect_similar and not aggregated_property:
            raise ClauseException("IF collect_similar is defined THEN aggregate_property must be defined")
        self._group_name = group_name
        self._collect_similar = collect_similar
        self._aggregated_property = aggregated_property

    def __repr__(self):
        return f"{self.__class__.__name__}({self._group_name}, {self._collect_similar}, {self._aggregated_property})"

    @property
    def group_name(self) -> str:
        return self._group_name

    @property
    def collect_similar(self) -> bool:
        return self._collect_similar

    @property
    def aggregated_property(self):
        return self._aggregated_property


GroupName = str


class GroupsClause:
    def __init__(self, groups: Dict[GroupName, GroupDef]) -> None:
        super().__init__()
        self._validate_groups(groups)
        self._groups = groups

    def __getitem__(self, item):
        return self._groups[item]

    def __iter__(self):
        return self._groups.__iter__()

    def items(self):
        return self._groups.items()

    def __repr__(self):
        return f"{self.__class__.__name__}({self._groups})"

    @staticmethod
    def _validate_groups(groups: Dict[GroupName, GroupDef]):
        if not groups:
            raise ClauseException("Groups cannot be empty")
        if not isinstance(groups, OrderedDict):
            raise ClauseException("Groups must be an OrderedDict (explicitly!)")

        for group_name, group_def in groups.items():
            if not isinstance(group_name, str):
                raise ClauseException("Group Key must be only string")
            if not isinstance(group_def, GroupDef):
                raise ClauseException("Group Definition must be of type GroupDef")

    @staticmethod
    def from_raw(groups_definition: OrderedDict):
        if not isinstance(groups_definition, OrderedDict):
            raise ClauseException("Groups must be an OrderedDict (explicitly!)")
        groups = OrderedDict()
        for group_name, group_def in groups_definition.items():
            groups[group_name] = GroupDef(group_name=group_name, **group_def)
        return GroupsClause(groups)


class GroupRule:
    def __init__(self,
                 select_clause: SelectClause,
                 where_clause: Optional[WhereClause],
                 groups_clause: GroupsClause) -> None:
        super().__init__()
        self._validate_group_relations(select_clause,
                                       where_clause,
                                       groups_clause)
        self._select_clause = select_clause
        self._where_clause = where_clause
        self._group_clause = groups_clause

    @property
    def select_clause(self):
        return self._select_clause

    @property
    def where_clause(self):
        return self._where_clause

    @property
    def group_clause(self):
        return self._group_clause

    @staticmethod
    def _validate_group_relations(select_clause: SelectClause,
                                  where_clause: WhereClause,
                                  groups_clause: GroupsClause):
        select_clause_aliases = set(col.alias for col in select_clause)
        for group, group_def in groups_clause.items():
            if group not in select_clause_aliases:
                raise ClauseException(f"Group {group} does not exist in select clause")

    @staticmethod
    def from_raw(rule_definition: dict):
        select = rule_definition["select"]
        columns = []
        for i, column in enumerate(select):
            if isinstance(column, str):
                column_def = Column(column)
            elif isinstance(column, dict):
                if len(column) > 1:
                    raise ClauseException(f"Column at index {i} must contain only one column definition")
                column_name = next(iter(column))
                alias = column[column_name].get("as")
                if not alias:
                    raise ClauseException(f"Alias must be defined for column name {column_name} at index {i}")
                column_def = Column(column_name, alias)
            else:
                raise ClauseException(f"Unknown column definition at index {i}")
            columns.append(column_def)
        select_clause = SelectClause(columns)
        where = rule_definition["where"]
        groups = OrderedDict(rule_definition["groups"])
        groups_clause = GroupsClause.from_raw(groups)
        return GroupRule(
            select_clause=select_clause,
            where_clause=None,
            groups_clause=groups_clause
        )




