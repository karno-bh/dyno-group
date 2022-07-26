import unittest
import json

from collections import OrderedDict

from dyno_grp.definitions import Column, SelectClause, GroupDef, GroupsClause, GroupRule
from dyno_grp.errors import ClauseException


class TestColumn(unittest.TestCase):
    def test_valid_settings(self):
        col1 = Column(name="Hello", alias="World")
        self.assertEqual("Hello", col1.name)
        self.assertEqual("World", col1.alias)
        col2 = Column(name="this_is_column1")
        self.assertEqual("this_is_column1", col2.alias)

    def test_invalid_column_name(self):
        with self.assertRaises(ClauseException):
            Column(123, "hello")
        with self.assertRaises(ClauseException):
            Column(None, None)

    def test_invalid_alias(self):
        with self.assertRaises(ClauseException):
            Column("col", 123)


class TestSelectClause(unittest.TestCase):
    def test_valid_pass(self):
        col1 = Column("Name")
        col2 = Column("Second_Name")
        cols = [col1, col2]
        select_clause = SelectClause(columns=cols)
        self.assertEqual(select_clause[0], col1)
        self.assertEqual(select_clause[1], col2)
        self.assertEqual(len(select_clause), len(cols))
        self.assertEqual(select_clause["Name"], col1)

    def test_invalid_length(self):
        with self.assertRaises(ClauseException):
            SelectClause(None)
        with self.assertRaises(ClauseException):
            SelectClause([])

    def test_wrong_types(self):
        with self.assertRaises(ClauseException):
            SelectClause({"alpha": "beta"})

    def test_name_collisions(self):
        with self.assertRaises(ClauseException):
            col1 = Column("Name")
            col2 = Column("Name")
            cols = [col1, col2]
            SelectClause(cols)
        with self.assertRaises(ClauseException):
            col1 = Column("First_Name", "Name")
            col2 = Column("Second Name", "Name")
            cols = [col1, col2]
            SelectClause(cols)


class TestGroupDefinition(unittest.TestCase):
    def test_group_defined_properly(self):
        grp1 = GroupDef(group_name="alpha")
        self.assertEqual("alpha", grp1.group_name)
        self.assertEqual(set(), grp1.similar_items)
        self.assertEqual(None, grp1.aggregated_property)

        grp2 = GroupDef(group_name="alpha", similar_items=['beta'], aggregated_property="alphas_group")
        self.assertEqual("alphas_group", grp2.aggregated_property)

    def test_group_name_undefined(self):
        with self.assertRaises(ClauseException):
            grp1 = GroupDef(group_name="")
        with self.assertRaises(ClauseException):
            grp1 = GroupDef(123)

    def test_exception_when_collect_similar_and_not_aggregated_property(self):
        with self.assertRaises(ClauseException):
            GroupDef("alpha", True)


class TestGroup(unittest.TestCase):

    def test_valid_groups(self):
        gen = OrderedDict([
            ("column2", {"similar_items": ['column1'], "aggregated_property": "second_column_values"}),
            ("column3", dict()),
        ])
        grp_clause = GroupsClause.from_raw(gen)
        self.assertEqual(grp_clause["column2"].group_name, GroupDef("column2", **gen["column2"]).group_name)
        self.assertEqual(grp_clause["column2"].similar_items, GroupDef("column2", **gen["column2"]).similar_items)
        self.assertEqual(grp_clause["column2"].aggregated_property,
                          GroupDef("column2", **gen["column2"]).aggregated_property)

    def test_invalid_length(self):
        gen = OrderedDict()
        with self.assertRaises(ClauseException):
            GroupsClause(gen)

    def test_invalid_dict_type(self):
        gen = dict([
            ("column2", {"similar_items": ['column1'], "aggregated_property": "second_column_values"}),
            ("column3", dict()),
        ])
        with self.assertRaises(ClauseException):
            GroupsClause.from_raw(gen)
        gen2 = dict(
            column2=GroupDef("column2", ['column1'], "second_column_values")
        )
        with self.assertRaises(ClauseException):
            GroupsClause(gen2)

    def test_invalid_value_type(self):
        gen2 = OrderedDict(
            column2=GroupDef("column2", ['column1'], "second_column_values"),
            column=dict()
        )
        with self.assertRaises(ClauseException):
            GroupsClause(gen2)

    def test_same_group_in_similar_items(self):
        gen2 = OrderedDict(
            column2=GroupDef("column2", ['column'], "second_column_values"),
            column=GroupDef("column")
        )
        with self.assertRaises(ClauseException):
            GroupsClause(gen2)


class TestGroupRule(unittest.TestCase):
    def test_group_select_correlation(self):
        select_clause = SelectClause([
            Column("column1", "first_name"),
            Column("column2", "second_name"),
            Column("column3")
        ])
        groups_clause = GroupsClause.from_raw(OrderedDict([
            ("first_name", {"similar_items": ['column3'], "aggregated_property": "second_column_values"}),
            ("second_name", dict()),
        ]))
        group_rule = GroupRule(select_clause=select_clause, where_clause=None, groups_clause=groups_clause)
        self.assertEqual(group_rule.select_clause["column1"].alias, "first_name")
        self.assertEqual(group_rule.group_clause["first_name"].group_name, "first_name")

    def test_group_clause_should_use_aliases(self):
        select_clause = SelectClause([
            Column("column1", "first_name"),
            Column("column2", "second_name"),
            Column("column3", "third_name")
        ])
        groups_clause = GroupsClause.from_raw(OrderedDict([
            ("column1", {"similar_items": ['third_name'], "aggregated_property": "second_column_values"}),
            ("second_name", dict()),
        ]))
        with self.assertRaises(ClauseException):
            group_rule = GroupRule(select_clause=select_clause, where_clause=None, groups_clause=groups_clause)

    def test_group_def_similar_items_should_be_in_select(self):
        select_clause = SelectClause([
            Column("column1", "first_name"),
            Column("column2", "second_name"),
            Column("column3", "third_name")
        ])
        groups_clause = GroupsClause.from_raw(OrderedDict([
            ("first_name", {"similar_items": ['column4'], "aggregated_property": "second_column_values"}),
            ("second_name", dict()),
        ]))
        with self.assertRaises(ClauseException):
            group_rule = GroupRule(select_clause=select_clause, where_clause=None, groups_clause=groups_clause)

    def test_group_def_similar_items_should_relate_to_aliases_in_select(self):
        select_clause = SelectClause([
            Column("column1", "first_name"),
            Column("column2", "second_name"),
            Column("column3", "third_name")
        ])
        groups_clause = GroupsClause.from_raw(OrderedDict([
            ("first_name", {"similar_items": ['column3'], "aggregated_property": "second_column_values"}),
            ("second_name", dict()),
        ]))
        with self.assertRaises(ClauseException):
            group_rule = GroupRule(select_clause=select_clause, where_clause=None, groups_clause=groups_clause)

    def test_group_rule_load(self):
        with open("rule_example_no_lang.json") as f:
            definitions = json.load(f)
        GroupRule.from_raw(definitions)


if __name__ == '__main__':
    unittest.main()
