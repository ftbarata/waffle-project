
from unicodedata import normalize


class UnicodeToAscii:

    def __init__(self, unicode):
        self.unicode = unicode

    def unicode_to_ascii(self):
            return normalize('NFKD', self.unicode).encode('ascii', 'ignore')
