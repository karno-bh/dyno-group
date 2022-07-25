import csv
import io

from typing import Optional


class CsvDictStream:
    def __init__(self, file_name) -> None:
        super().__init__()
        self._file_name = file_name
        self._fp: Optional[io.TextIOWrapper] = None
        self._csv_dict_reader: Optional[csv.DictReader] = None

    def __enter__(self):
        self._fp = open(self._file_name)
        self._csv_dict_reader = csv.DictReader(self._fp)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __iter__(self):
        return self._data()

    def _data(self):
        for row in self._csv_dict_reader:
            yield row

    def close(self):
        fp = self._fp
        self._fp = None
        self._csv_dict_reader = None
        if fp:
            fp.close()
