import json
import unittest

from dyno_grp.grouper import Grouper


class TestGrouping(unittest.TestCase):
    def test_file_loading(self):
        rule_file = "rule_test001.json"
        data_file = "test_data001.csv"
        with open(rule_file) as f:
            rules = json.load(f)
        grouper = Grouper.csv_to_json_grouper(data_file, rules)
        grouped_data = grouper()

    def test_file_loading_2(self):
        rule_file = "rule_test002.json"
        data_file = "test_data002.csv"
        with open(rule_file) as f:
            rules = json.load(f)
        grouper = Grouper.csv_to_json_grouper(data_file, rules)
        grouped_data = grouper()




if __name__ == '__main__':
    unittest.main()
