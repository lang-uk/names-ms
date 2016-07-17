import re
import unicodedata
from string import capwords

APOSTROPHES = "'’ʼ`""*"  # All kind of used apostrophes, including weird ones
DASHES = "-–—‒―"  # Commonly used dashes (full list can be found here http://www.fileformat.info/info/unicode/category/Pd/list.htm)

CYR_SPECIFIC_CHARSET = "а-яіїєґ"
CYR_CHARSET = CYR_SPECIFIC_CHARSET + re.escape(APOSTROPHES) + re.escape(DASHES)
UKR_SPECIFIC_CHARSET = "іїєґ"
ENG_SPECIFIC_CHARSET = "a-z"
ENG_CHARSET = ENG_SPECIFIC_CHARSET + re.escape(APOSTROPHES) + re.escape(DASHES)


def title(s):
    """
    Return properly capitalized names.

    >>> title("ALEXEY PETRENKO")
    'Alexey Petrenko'

    >>> title("іванна орестівна климпуш-цинцадзе")
    'Іванна Орестівна Климпуш-Цинцадзе'
    """
    chunks = s.split()
    chunks = map(lambda x: capwords(x, "-"), chunks)
    return " ".join(chunks)


def deaccent(text):
    """
    Remove accentuation from the given string. Input text is either a unicode string or utf8 encoded bytestring.

    Return input string with accents removed, as unicode.
    Kindly borrowed from https://github.com/RaRe-Technologies/gensim/blob/develop/gensim/utils.py
    by Radim Rehurek and Petr Sojka

    >>> deaccent("Šéf chomutovských komunistů dostal poštou bílý prášek")
    'Sef chomutovskych komunistu dostal postou bily prasek'
    """
    if not isinstance(text, str):
        # assume utf8 for byte strings, use default (strict) error handling
        text = text.decode('utf8')

    norm = unicodedata.normalize("NFD", text)
    result = ''.join(ch for ch in norm if unicodedata.category(ch) != 'Mn')
    return unicodedata.normalize("NFC", result)


def has_cyr(name):
    """
    Check if string contains latin characters only.

    >>> has_cyr("John")
    False
    >>> has_cyr("Ірина") and has_cyr("Євген")
    True
    >>> has_cyr("Poмaн")
    True
    """
    return re.search(
        "[%s+]" % CYR_SPECIFIC_CHARSET,
        deaccent(name.lower()),
        re.UNICODE) is not None


def has_ukr(name):
    """
    Check if string contains latin characters only.

    >>> has_ukr("John")
    False
    >>> has_ukr("Ірина") and has_ukr("Євген")
    True
    >>> has_ukr("Poмaн")
    False
    """
    return re.search(
        "[%s]+" % UKR_SPECIFIC_CHARSET,
        name.lower(),
        re.UNICODE) is not None


def has_eng(name):
    """
    Check if string contains latin characters only.

    >>> has_eng("John")
    True
    >>> has_eng("Ірина") or has_eng("Євген")
    False
    >>> has_eng("Poмaн")
    True
    >>> has_eng("Radim Řehůřek")
    True
    """
    return re.search(
        "[%s]+" % ENG_SPECIFIC_CHARSET,
        name.lower(),
        re.UNICODE) is not None


def is_cyr(name, include_spaces=False):
    """
    Check if string contains cyrillic characters only.

    include_spaces=False means that functions will return false if it contains
    spaces
    >>> is_cyr("John")
    False
    >>> is_cyr("Петро")
    True
    >>> is_cyr("Квітка-Основ'яненко")
    True
    >>> is_cyr("Poмaн")
    False
    >>> is_cyr("0лександр") or is_cyr("1рина") or is_cyr("Д|ана")
    False
    >>> is_cyr("Іванна Орестівна Климпуш-Цинцадзе", include_spaces=False)
    False
    >>> is_cyr("Іванна Орестівна Климпуш-Цинцадзе", include_spaces=True)
    True
    """
    if include_spaces:
        rgx = "^[%s\s]+$" % CYR_CHARSET
    else:
        rgx = "^[%s]+$" % CYR_CHARSET

    return re.search(
        rgx,
        name.lower(),
        re.UNICODE) is not None


def is_eng(name, include_spaces=False):
    """
    Check if string contains latin characters only.

    include_spaces=False means that functions will return false if it contains
    spaces
    >>> is_eng("John")
    True
    >>> is_eng("Петро")
    False
    >>> is_eng("O'briens")
    True
    >>> is_eng("Poмaн")
    False
    >>> is_eng("T0m")
    False
    >>> is_eng("Pau1") or is_eng("Pau|")
    False
    >>> is_eng("Řehůřek")
    True
    >>> is_eng("Radim Řehůřek", include_spaces=False)
    False
    >>> is_eng("Radim Řehůřek", include_spaces=True)
    True
    """
    if include_spaces:
        rgx = "^[%s\s]+$" % ENG_CHARSET
    else:
        rgx = "^[%s]+$" % ENG_CHARSET

    return re.search(
        rgx,
        deaccent(name.lower()),
        re.UNICODE) is not None


def normalize_alphabets(chunk):
    """
    Try to normalize names written in mixed alphabets (cyr+eng+special chars).

    For example, 01eg
    """
    # TODO: implement
    return chunk


def parse_fullname(person_name):
    """
    Parse input name and return a list of normalized tokens.

    >>> parse_fullname("іванна орестівна климпуш-цинцадзе")
    ['Іванна', 'Орестівна', 'Климпуш', 'Цинцадзе']
    """
    # Extra care for initials (especialy those without space)
    person_name = re.sub("\s+", " ",
                         person_name.
                         replace(".", ". ").
                         replace("\xa0", " ").
                         replace(",", ". "))

    chunks = re.split("[\s%s]+" % re.escape(DASHES), person_name.strip())
    chunks = map(normalize_alphabets, chunks)
    chunks = map(title, chunks)
    return list(chunks)
