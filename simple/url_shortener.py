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


class UrlShortener:

    def __init__(self, domain):
        self.domain = domain
        self._db = {}
        
    def _add_to_db(self, url, url_shortened):
        self._db[url_shortened] = url
        return url_shortened

    def shorten(self, url, seo):

        if not isinstance(seo, str):
            raise TypeError('SEO is not string')

        if len(seo) > 20:
            raise ValueError('SEO too long - max of 20 chars')
        
        url_shortened = f'{self.domain}/{seo}'

        db_hit = self._db.get(url_shortened)
        if db_hit:
            if url == db_hit:
                return url_shortened
            else:
                raise ValueError('This URL has already been taken')

        return self._add_to_db(url, url_shortened)
    
    def unshorten(self, url_shortened):
        unshortened = self._db.get(url_shortened)
        if not unshortened:
            raise KeyError('We have not shortened this URL before')
        return unshortened
