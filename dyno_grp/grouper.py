import csv


class Grouper:
    def __init__(self, data_stream, definitions, result_file) -> None:
        super().__init__()
        self._data_stream = data_stream
        self._definitions = definitions
        self._result_file = result_file

    def _process_definitions(self):
        pass

    def __call__(self, *args, **kwargs):
        pass