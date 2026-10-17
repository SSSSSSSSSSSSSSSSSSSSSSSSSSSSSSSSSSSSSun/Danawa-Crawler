import ast
import csv
import os
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
source = (ROOT / 'danawa_crawler.py').read_text(encoding='utf-8')
tree = ast.parse(source)
cls = next(node for node in tree.body if isinstance(node, ast.ClassDef))
namespace = {'csv': csv, 'os': os, 'STR_NAME': 'name'}
exec(compile(ast.Module(body=[cls], type_ignores=[]), 'danawa_crawler.py', 'exec'), namespace)
Crawler = namespace['DanawaCrawler']

class DataSafetyTests(unittest.TestCase):
    def check_data(self, raw, expected_ids=None):
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            previous = os.getcwd()
            try:
                os.chdir(folder)
                namespace['DATA_PATH'] = 'saved'
                Path('saved').mkdir()
                Path('saved/CPU.csv').write_text('previous data')
                if raw is not None:
                    Path('CPU.csv').write_text(raw)
                crawler = Crawler.__new__(Crawler)
                crawler.crawlingCategory = [{'name': 'CPU'}]
                if expected_ids is None:
                    with self.assertRaises(RuntimeError):
                        crawler.DataSort()
                    self.assertEqual(Path('saved/CPU.csv').read_text(), 'previous data')
                else:
                    crawler.DataSort()
                    with open('saved/CPU.csv', newline='') as file:
                        rows = list(csv.reader(file))
                    self.assertEqual([r[0] for r in rows[1:]], expected_ids)
                    self.assertFalse(Path('CPU.csv').exists())
            finally:
                os.chdir(previous)

    def test_empty_preserves_existing_data(self):
        self.check_data('2026-10-18\n')

    def test_invalid_ids_preserve_existing_data(self):
        self.check_data('2026-10-18\ninvalid,CPU,type,100,mall,unit\n')

    def test_missing_data_preserves_existing_data(self):
        self.check_data(None)

    def test_valid_rows_are_sorted(self):
        self.check_data('2026-10-18\n2,B,type,200,mall,unit\n1,A,type,100,mall,unit\n', ['1', '2'])

if __name__ == '__main__':
    unittest.main()
