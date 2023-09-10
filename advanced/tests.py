from datetime import datetime, timedelta
from unittest.mock import patch
import unittest

from url_shortener import UrlShortener


class ShortenTest(unittest.TestCase):

    def test_has_lock_expired_unlocked(self):
        shortener = UrlShortener('mydomain')
        self.assertTrue(shortener._has_lock_expired())

    def test_has_lock_expired_locked_recently(self):
        shortener = UrlShortener('mydomain')
        shortener._acquire_lock()
        self.assertIsNotNone(shortener._lock_datetime)
        self.assertFalse(shortener._has_lock_expired())

    @patch('url_shortener.datetime')
    def test_has_lock_expired_locked_not_recently(self, mock_dt):
        mock_dt.utcnow.side_effect = [
            datetime.utcnow(),  # set lock with now
            datetime.utcnow() + timedelta(seconds=10)  # check lock with future dt
        ]
        shortener = UrlShortener('mydomain')
        shortener._acquire_lock()
        self.assertIsNotNone(shortener._lock_datetime)
        self.assertTrue(shortener._has_lock_expired())

    def test_acquire_lock_when_unlocked(self):
        shortener = UrlShortener('mydomain')
        shortener._acquire_lock()
        self.assertIsNotNone(shortener._lock)
        self.assertIsNotNone(shortener._lock_datetime)

    def test_acquire_lock_when_locked(self):
        shortener = UrlShortener('mydomain')
        shortener._acquire_lock()
        self.assertIsNone(shortener._acquire_lock())

    def test_release_lock_when_unlocked(self):
        shortener = UrlShortener('mydomain')
        self.assertFalse(shortener._release_lock(''))
        self.assertIsNone(shortener._lock)
        self.assertIsNone(shortener._lock_datetime)

    def test_release_lock_when_locked(self):
        shortener = UrlShortener('mydomain')
        lock = shortener._acquire_lock()
        self.assertTrue(shortener._release_lock(lock))
        self.assertIsNone(shortener._lock)
        self.assertIsNone(shortener._lock_datetime)

    def test_add_to_db(self):
        shortener = UrlShortener('mydomain')
        lock = shortener._acquire_lock()
        shortener._add_to_db('some_url', 'shortened', lock)
        self.assertIn('shortened', shortener._db)
        self.assertEqual(shortener._db['shortened'], 'some_url')
        self.assertIsNone(shortener._lock)
        self.assertIsNone(shortener._lock_datetime)

    def test_shorten_url_not_string(self):
        shortener = UrlShortener('mydomain')
        with self.assertRaises(TypeError):
            shortener.shorten('my_url', 123)

    def test_shorten_seo_too_long(self):
        shortener = UrlShortener('mydomain')
        with self.assertRaises(ValueError):
            shortener.shorten('my_url', 'A'*21)

    def test_shorten_retry_count_too_high(self):
        shortener = UrlShortener('mydomain')
        with self.assertRaises(ValueError):
            shortener.shorten('my_url', 'A'*21, 4)

    @patch('url_shortener.UrlShortener._acquire_lock')
    def test_shorten_while_locked(self, mock_acquire):
        mock_acquire.side_effect = [False, False, True]

        shortener = UrlShortener('mydomain')
        shortener.shorten('my_url', 'AAA')
        self.assertEqual(mock_acquire.call_count, 3)

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
