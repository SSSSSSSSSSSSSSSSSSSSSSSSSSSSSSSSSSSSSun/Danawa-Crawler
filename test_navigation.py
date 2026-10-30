"""Exercise navigation recovery without a browser or network requests."""

import unittest
from unittest.mock import Mock, patch

from test_data_safety import Crawler, namespace


class FakeTimeout(Exception):
    pass


class ImmediateWait:
    def __init__(self, browser, timeout):
        self.browser = browser

    def until(self, predicate):
        if not predicate(self.browser):
            raise FakeTimeout('Still blank')


class NavigationTests(unittest.TestCase):
    url = 'https://prod.danawa.com/list/?cate=112753'

    def navigate(self, destinations):
        browser = Mock()
        states = iter(destinations)
        browser.get.side_effect = lambda url: setattr(browser, 'current_url', next(states))
        return browser

    def setUp(self):
        self.context = patch.dict(namespace, WebDriverWait=ImmediateWait,
                                  TimeoutException=FakeTimeout)
        self.context.start()
        self.addCleanup(self.context.stop)
        self.crawler = Crawler.__new__(Crawler)

    def test_success_does_not_repeat_navigation(self):
        browser = self.navigate([self.url])
        self.crawler.OpenCategory(browser, self.url)
        browser.get.assert_called_once_with(self.url)

    def test_blank_startup_recovers_in_same_browser(self):
        browser = self.navigate(['data:,', 'about:blank', self.url])
        self.crawler.OpenCategory(browser, self.url)
        self.assertEqual(browser.get.call_count, 3)

    def test_persistent_blank_fails_with_requested_and_actual_url(self):
        browser = self.navigate(['data:,'] * 3)
        with self.assertRaises(RuntimeError) as caught:
            self.crawler.OpenCategory(browser, self.url)
        self.assertIn(self.url, str(caught.exception))
        self.assertIn('data:,', str(caught.exception))
        self.assertEqual(browser.get.call_count, 3)

    def test_nonblank_error_page_is_not_retried_as_blank(self):
        browser = self.navigate(['chrome-error://chromewebdata/'])
        self.crawler.OpenCategory(browser, self.url)
        browser.get.assert_called_once_with(self.url)


if __name__ == '__main__':
    unittest.main()
