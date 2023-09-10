# Shorten URL "SEO"
# Given as input a URL and a SEO keyword with a max length of 20 characters, chosen by the user, generate a SEO URL.

# Examples:

# Input:
# URL: http://looooong.com/somepath 
# SEO keyword: MY-NEW-WS
# Output: 
# URL: http://short.com/MY-NEW-WS

# Input:
# URL: http://looooong.com/somepath 
# SEO keyword: POTATO
# Output: 
# URL: http://short.com/POTATO

import uuid
from datetime import datetime
from time import sleep


class UrlShortener:

    def __init__(self, domain):
        self.domain = domain
        self._db = {}
        self._lock = None
        self._lock_datetime = None

    def _has_lock_expired(self):
        # in case a process dies, we cannot leave the lock in-place forever
        if not self._lock_datetime:
            self._lock = None
            return True
        elif (datetime.utcnow() - self._lock_datetime).total_seconds() > 3:
            self._release_lock(self._lock)
            return True
        return False

    def _acquire_lock(self):
        self._has_lock_expired()
        if self._lock:
            return None
        self._lock = uuid.uuid4()
        self._lock_datetime = datetime.utcnow()
        return self._lock
    
    def _release_lock(self, lock_id):
        if self._lock and self._lock == lock_id:
            self._lock = None
            self._lock_datetime = None
            return True
        return False
    
    def _add_to_db(self, url, url_shortened, lock):
        self._db[url_shortened] = url
        self._release_lock(lock)
        return url_shortened

    def shorten(self, url, seo, retry_count=0):

        if retry_count > 3:
            raise ValueError('Exceeded max retries')

        if not isinstance(seo, str):
            raise TypeError('SEO is not string')

        if len(seo) > 20:
            raise ValueError('SEO too long - max of 20 chars')
        
        url_shortened = f'{self.domain}/{seo}'

        # acquire lock before read - otherwise, concurrent requests might both not be 
        # in the DB and might assume they can update the DB with their keyword
        lock = self._acquire_lock()
        if not lock:
            sleep(0.1 * 2 ** retry_count)
            self.shorten(url, seo, retry_count=retry_count+1)

        db_hit = self._db.get(url_shortened)
        if db_hit:
            self._release_lock(lock)
            if url == db_hit:
                return url_shortened
            else:
                raise ValueError('This URL has already been taken')

        return self._add_to_db(url, url_shortened, lock)
    
    def unshorten(self, url_shortened):
        unshortened = self._db.get(url_shortened)
        if not unshortened:
            raise KeyError('We have not shortened this URL before')
        return unshortened
