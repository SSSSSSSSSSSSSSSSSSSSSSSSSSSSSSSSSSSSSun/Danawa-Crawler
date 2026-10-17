import unittest
from pathlib import Path

from danawa_parser import parse_product_rows


class ProductParserTests(unittest.TestCase):
    def setUp(self):
        self.source = (Path(__file__).parent / 'tests/fixtures/product_list.html').read_text(encoding='utf-8')

    def test_real_new_markup_preserves_variants(self):
        rows = parse_product_rows(self.source)
        self.assertEqual([row[0] for row in rows], ['108424286', '124012222', '108463445'])
        self.assertEqual(rows[0][2:], ['정품', '473750', '165몰', ''])
        self.assertIn('270K Plus', rows[0][1])

    def test_advertisements_outside_main_list_are_excluded(self):
        rows = parse_product_rows('<div>' + self.source + self.source.replace('id="productListArea"', 'id="advertisement"') + '</div>')
        self.assertEqual(len(rows), 3)

    def test_placeholder_is_not_a_product(self):
        self.assertEqual(parse_product_rows('<section id="productListArea"><div class="dnw-product-list-item animate-pulse"></div></section>'), [])

    def test_zero_price_offer_is_excluded(self):
        rows = parse_product_rows(self.source.replace('>473,750<', '>0<'))
        self.assertNotIn('108424286', [row[0] for row in rows])

    def test_ram_unit_price_link_is_not_the_sale_price(self):
        source = (Path(__file__).parent / 'tests/fixtures/ram_list.html').read_text(encoding='utf-8')
        rows = {row[0]: row for row in parse_product_rows(source)}
        self.assertEqual(rows['124527565'][2:], ['128GB', '9300000', '6몰', '72,656원/1GB'])
        # The popularity badge must not become the capacity/type column.
        self.assertEqual(rows['124527583'][2], '64GB')


if __name__ == '__main__':
    unittest.main()
