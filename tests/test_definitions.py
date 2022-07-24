import unittest

from collections import OrderedDict

from dyno_grp.definitions import Column, SelectClause, GroupDef, GroupsClause
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
        self.assertEqual(False, grp1.collect_similar)
        self.assertEqual(None, grp1.aggregated_property)

        grp2 = GroupDef(group_name="alpha", collect_similar=True, aggregated_property="alphas_group")
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

    def data_gen(self):
        return OrderedDict([
            ("column2", {"collect_similar": True, "aggregated_property": "second_column_values"}),
            ("column3", dict()),
        ])

    def test_valid_groups(self):
        gen = self.data_gen()
        grp_clause = GroupsClause.from_raw(gen)
        f = grp_clause["column2"]
        print(f)

if __name__ == '__main__':
    unittest.main()
