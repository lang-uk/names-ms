import re
import unicodedata
from translitua import translit, RussianInternationalPassport
from string import capwords

APOSTROPHES = "'’ʼ`\"*"  # All kind of used apostrophes, including weird ones
DASHES = "-–—‒―"  # Commonly used dashes (full list can be found here http://www.fileformat.info/info/unicode/category/Pd/list.htm)
BRACKETS = "[](){}"
YO_CHARACTER = "Ёё"

CYR_SPECIFIC_CHARSET = "а-яіїєґё"
CYR_CHARSET = CYR_SPECIFIC_CHARSET + re.escape(APOSTROPHES) + re.escape(DASHES)
UKR_SPECIFIC_CHARSET = "іїєґ"
ENG_SPECIFIC_CHARSET = "a-z"
ENG_CHARSET = ENG_SPECIFIC_CHARSET + re.escape(APOSTROPHES) + re.escape(DASHES)

HAS_CYR_RX = re.compile("[%s+]" % CYR_SPECIFIC_CHARSET, re.UNICODE)
HAS_UKR_RX = re.compile("[%s]+" % UKR_SPECIFIC_CHARSET, re.UNICODE)
HAS_ENG_RX = re.compile("[%s]+" % ENG_SPECIFIC_CHARSET, re.UNICODE)

IS_ENG_RX = re.compile("^[%s]+$" % ENG_CHARSET, re.UNICODE)
IS_ENG_AND_SPACES_RX = re.compile("^[%s\s]+$" % ENG_CHARSET, re.UNICODE)
IS_CYR_RX = re.compile("^[%s]+$" % CYR_CHARSET, re.UNICODE)
IS_CYR_AND_SPACES_RX = re.compile("^[%s\s]+$" % CYR_CHARSET, re.UNICODE)

APOSTROPHE_RX = re.compile("[%s]" % re.escape(APOSTROPHES), re.UNICODE)
TOKENIZE_RX = re.compile("[\s%s]+" % re.escape(DASHES + BRACKETS), re.UNICODE)


def convert_table(table):
    """
    Prepare table for str.translate method.

    Borrowed from https://github.com/dchaplinsky/translit-ua project
    >>> print(1072 in convert_table({"а": "a"}))
    True
    >>> print(1073 in convert_table({"а": "a"}))
    False
    >>> print(convert_table({"а": "a"})[1072] == "a")
    True
    >>> print(len(convert_table({"а": "a"}).keys()) == 1)
    True
    """
    return dict((ord(k), v) for k, v in table.items())


def add_uppercase(table):
    """
    Extend the table with uppercase options.

    Again, borrowed from https://github.com/dchaplinsky/translit-ua project
    >>> print("а" in add_uppercase({"а": "a"}))
    True
    >>> print(add_uppercase({"а": "a"})["а"] == "a")
    True
    >>> print("А" in add_uppercase({"а": "a"}))
    True
    >>> print(add_uppercase({"а": "a"})["А"] == "A")
    True
    >>> print(len(add_uppercase({"а": "a"}).keys()))
    2
    >>> print("Аа" in add_uppercase({"аа": "aa"}))
    True
    >>> print(add_uppercase({"аа": "aa"})["Аа"] == "Aa")
    True
    """
    orig = table.copy()
    orig.update(
        dict((k.capitalize(), v.capitalize()) for k, v in table.items()))

    return orig

SPECIAL_TO_CYR = convert_table({
    "1": "і",
    "|": "і",
    "3": "з",
    "0": "о",
    "4": "ч"
})

SPECIAL_TO_ENG = convert_table({
    "1": "l",
    "|": "l",
    "0": "o"
})

ENG_TO_CYR = convert_table(add_uppercase({
    "a": "а",
    "i": "і",
    "e": "е",
    "o": "о",
    "y": "у",
    "p": "р",
    "k": "к",
    "b": "в",
    "m": "м",
    "c": "с",
    "u": "и",
    "t": "т",
    "h": "н",
    "l": "і",
    "х": "х",
}))

CYR_TO_ENG = convert_table(add_uppercase({
    "а": "a",
    "і": "i",
    "е": "e",
    "о": "o",
    "у": "y",
    "р": "p",
    "к": "k",
    "в": "b",
    "м": "m",
    "с": "c",
    "и": "u",
    "т": "t",
    "н": "h",
    "і": "l",
    "х": "х",
}))

YO_TO_E = convert_table(add_uppercase({
    "ё": "е",
}))


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
        HAS_CYR_RX,
        name.lower()) is not None


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
        HAS_UKR_RX,
        name.lower()) is not None


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
        HAS_ENG_RX,
        name.lower()) is not None


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
        rgx = IS_CYR_AND_SPACES_RX
    else:
        rgx = IS_CYR_RX

    return re.search(
        rgx,
        name.lower()) is not None


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
        rgx = IS_ENG_AND_SPACES_RX
    else:
        rgx = IS_ENG_RX

    return re.search(
        rgx,
        deaccent(name.lower())) is not None


def convert_eng_to_cyr(name):
    """
    Try to convert latin characters to cyrilic that looks similar.

    >>> convert_eng_to_cyr("PomaH")
    'РомаН'
    """
    return convert_special_chars_to_cyr(name).translate(ENG_TO_CYR)


def convert_cyr_to_eng(name):
    """
    Try to convert cyrillic characters to latin that looks similar.

    >>> convert_cyr_to_eng("Аdам")
    'Adam'
    """
    return convert_special_chars_to_eng(name).translate(CYR_TO_ENG)


def convert_special_chars_to_cyr(name):
    """
    Try to convert special characters to cyrillic that looks similar.

    >>> convert_special_chars_to_cyr("3оя")
    'зоя'
    """
    return name.translate(SPECIAL_TO_CYR)


def convert_special_chars_to_eng(name):
    """
    Try to convert special characters to cyrillic that looks similar.

    >>> convert_special_chars_to_eng("e11i0t")
    'elliot'
    """
    return name.translate(SPECIAL_TO_ENG)


def tranliterate_all_the_things(name):
    """
    Transliterate both russian and Ukrainian characters to latin.

    This is our last hope to deal with mixed alphabets
    >>> tranliterate_all_the_things("bэdtєd і тыква")
    'bedtied i tykva'
    """
    return translit(translit(name), RussianInternationalPassport)


def normalize_alphabets(chunk):
    """
    Try to normalize names written in mixed alphabets (cyr+eng+special chars).

    For example, 01eg

    >>> normalize_alphabets("Adam")
    'Adam'
    >>> normalize_alphabets("Петро")
    'Петро'
    >>> normalize_alphabets("0leg")
    'oleg'
    >>> normalize_alphabets("3оя")  # 3 (number) instead of З
    'зоя'
    >>> normalize_alphabets("3oя")  # latin o
    'зоя'
    >>> normalize_alphabets("3oя")  # 3 and latin o
    'зоя'
    >>> normalize_alphabets("E11iot")  # numbers instead of l
    'Elliot'
    >>> normalize_alphabets("Elliоt")  # cyrilic o
    'Elliot'
    >>> normalize_alphabets("E||iоt")  # cyrilic o and special characters
    'Elliot'
    >>> normalize_alphabets("Pетro")  # Weird mix — transliterate!
    'Petro'
    """
    # Massage data a bit: replace numbers and special characters with look
    # alike characters from alphabet
    cyr_candidate = convert_special_chars_to_cyr(chunk)

    # if chunk contains only characters of one alphabet — return it as it.
    if is_cyr(cyr_candidate):
        return cyr_candidate

    eng_candidate = convert_special_chars_to_eng(chunk)
    if is_eng(eng_candidate):
        return eng_candidate

    # if chunk contains mixed alphabets
    if has_eng(chunk) and has_cyr(chunk):
        # Try to replace cyr characters with similar eng
        eng_candidate = convert_cyr_to_eng(chunk)
        if is_eng(eng_candidate):
            return eng_candidate

        # Try to replace eng characters with similar cyr
        cyr_candidate = convert_eng_to_cyr(chunk)

        # Did it help?
        if is_cyr(cyr_candidate):
            return cyr_candidate

    # No more chances? Transliterate everything to latin
    return tranliterate_all_the_things(chunk)


def normalize_charset(term):
    """
    Basic normalisation of the input data.

    Convert various kinds of apostrophes to common one
    Convert ё to е

    >>> normalize_charset("a'b’vʼg`d\\"e*yo") == "a\'b\'v\'g\'d\'e\'yo"
    True
    >>> normalize_charset("ЕЁиеё") == "ЕЕиее"
    True

    """
    return re.sub(APOSTROPHE_RX, "'",
                  term.translate(YO_TO_E))


def parse_fullname(person_name):
    """
    Parse input name and return a list of normalized tokens.

    >>> parse_fullname("іванна орестівна климпуш-цинцадзе")
    ['Іванна', 'Орестівна', 'Климпуш', 'Цинцадзе']

    >>> parse_fullname("Ёвлamпій Ті`хії")
    ['Евлампій', "Ті\'хії"]
    >>> parse_fullname("Нездимовська (Медушевська) Анна Олексіївна")
    ['Нездимовська', 'Медушевська', 'Анна', 'Олексіївна']
    >>> parse_fullname("П. Д. Петренко")
    ['П', 'Д', 'Петренко']
    """
    # Extra care for initials (especialy those without space)
    person_name = re.sub("\s+", " ",
                         person_name.
                         replace(".", " ").
                         replace("\xa0", " ").
                         replace(",", " "))

    chunks = re.split(
        TOKENIZE_RX,
        person_name.strip().lower())

    chunks = map(normalize_charset, chunks)
    chunks = map(normalize_alphabets, chunks)
    chunks = map(title, chunks)
    return list(chunks)
