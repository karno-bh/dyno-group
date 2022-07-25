from collections import defaultdict


def filter_dict(d: dict, *keys, include=True):
    keys_set = set(keys)

    def predicate(v):
        return v in keys_set if include else v not in keys_set
    return {k: v for k, v in d.items() if predicate(k)}


def group_by(_list: list, key: str, res: defaultdict):
    res = defaultdict(list)
    for item in _list:
        res[item[key]].append(filter_dict(item, key, include=False))
    return res

