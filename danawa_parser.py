"""Parse the public product list markup introduced in Danawa's new UI."""
import re
from urllib.parse import parse_qs, urlsplit

from lxml import html


def parse_product_rows(source):
    document = html.fromstring(source)
    rows = {}
    # The main list excludes the advertising and recommendation sections.
    for product in document.xpath('//*[@id="productListArea"]//*[contains(concat(" ", normalize-space(@class), " "), " dnw-product-list-item ")]'):
        titles = product.xpath('.//*[@data-testid="ProductListTitle"]/a')
        if not titles:
            continue  # Loading placeholder.
        name = titles[0].text_content().strip()
        for offer in product.xpath('.//*[@data-testid="ProductListPriceCompare"]//ul/li'):
            links = offer.xpath('./div/div[2]//a[contains(@href,"pcode=")]')
            if not links:
                continue  # Discontinued or no current price.
            link = links[0]
            code = parse_qs(urlsplit(link.get('href')).query).get('pcode', [''])[0]
            price_nodes = link.xpath('./span[1]')
            price = re.sub(r'[^0-9]', '', price_nodes[0].text_content()) if price_nodes else ''
            if not code.isdigit() or not price or int(price) <= 0:
                continue
            # Variant label and optional per-unit price occupy the first column.
            labels = offer.xpath('./div/div[1]/span[contains(concat(" ", normalize-space(@class), " "), " truncate ")]')
            parts = [node.text_content().strip() for node in labels if node.text_content().strip()]
            units = offer.xpath('./div/div[1]/a')
            unit = units[0].text_content().strip() if units else ''
            malls = offer.xpath('./div/div[last()]/span')
            mall = malls[0].text_content().strip() if malls else ''
            rows[code] = [code, name, parts[0] if parts else '', price, mall, unit]
    return list(rows.values())
