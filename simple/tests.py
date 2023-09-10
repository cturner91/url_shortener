import unittest

from url_shortener import UrlShortener


class ShortenTest(unittest.TestCase):

    def test_add_to_db(self):
        shortener = UrlShortener('mydomain')
        shortener._add_to_db('some_url', 'shortened')
        self.assertIn('shortened', shortener._db)
        self.assertEqual(shortener._db['shortened'], 'some_url')

    def test_shorten_url_not_string(self):
        shortener = UrlShortener('mydomain')
        with self.assertRaises(TypeError):
            shortener.shorten('my_url', 123)

    def test_shorten_seo_too_long(self):
        shortener = UrlShortener('mydomain')
        with self.assertRaises(ValueError):
            shortener.shorten('my_url', 'A'*21)

    def test_db_hit(self):
        shortener = UrlShortener('mydomain')
        shortener.shorten('my_url', 'my_seo')
        self.assertIn('mydomain/my_seo', shortener._db)

    def test_db_but_url_not_same(self):
        shortener = UrlShortener('mydomain')
        shortener.shorten('my_url', 'my_seo')
        with self.assertRaises(ValueError):
            shortener.shorten('different_url', 'my_seo')
        
    def test_happy_path(self):
        shortener = UrlShortener('mydomain')
        result = shortener.shorten('my_url', 'my_seo')
        self.assertEqual(result, 'mydomain/my_seo')

    def test_unshorten_hit(self):
        shortener = UrlShortener('mydomain')
        shortened = shortener.shorten('my_url', 'my_seo')
        unshortened = shortener.unshorten(shortened)
        self.assertEqual(unshortened, 'my_url')

    def test_unshorten_miss(self):
        shortener = UrlShortener('mydomain')
        with self.assertRaises(KeyError):
            shortener.unshorten('random_new_string')


if __name__ == '__main__':
    unittest.main()
