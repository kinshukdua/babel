# -*- coding: utf-8 -*-
#
# Copyright (C) 2007 Edgewall Software
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://babel.edgewall.org/wiki/License.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://babel.edgewall.org/log/.

"""Locale dependent formatting and parsing of numeric data.

The default locale for the functions in this module is determined by the
following environment variables, in that order:

 * ``LC_NUMERIC``,
 * ``LC_ALL``, and
 * ``LANG``
"""
# TODO: percent and scientific formatting

import re

from babel.core import default_locale, Locale

__all__ = ['format_number', 'format_decimal', 'format_currency',
           'format_percent', 'format_scientific', 'parse_number',
           'parse_decimal', 'NumberFormatError']
__docformat__ = 'restructuredtext en'

LC_NUMERIC = default_locale('LC_NUMERIC')

def get_currency_symbol(currency, locale=LC_NUMERIC):
    """Return the symbol used by the locale for the specified currency.
    
    >>> get_currency_symbol('USD', 'en_US')
    u'$'
    
    :param currency: the currency code
    :param locale: the `Locale` object or locale identifier
    :return: the currency symbol
    :rtype: `unicode`
    """
    return Locale.parse(locale).currency_symbols.get(currency, currency)

def get_decimal_symbol(locale=LC_NUMERIC):
    """Return the symbol used by the locale to separate decimal fractions.
    
    >>> get_decimal_symbol('en_US')
    u'.'
    
    :param locale: the `Locale` object or locale identifier
    :return: the decimal symbol
    :rtype: `unicode`
    """
    return Locale.parse(locale).number_symbols.get('decimal', u'.')

def get_group_symbol(locale=LC_NUMERIC):
    """Return the symbol used by the locale to separate groups of thousands.
    
    >>> get_group_symbol('en_US')
    u','
    
    :param locale: the `Locale` object or locale identifier
    :return: the group symbol
    :rtype: `unicode`
    """
    return Locale.parse(locale).number_symbols.get('group', u',')

def format_number(number, locale=LC_NUMERIC):
    """Return the given number formatted for a specific locale.
    
    >>> format_number(1099, locale='en_US')
    u'1,099'
    
    :param number: the number to format
    :param locale: the `Locale` object or locale identifier
    :return: the formatted number
    :rtype: `unicode`
    """
    # Do we really need this one?
    return format_decimal(number, locale=locale)

def format_decimal(number, format=None, locale=LC_NUMERIC):
    """Return the given decimal number formatted for a specific locale.
    
    >>> format_decimal(1.2345, locale='en_US')
    u'1.234'
    >>> format_decimal(1.2346, locale='en_US')
    u'1.235'
    >>> format_decimal(-1.2346, locale='en_US')
    u'-1.235'
    >>> format_decimal(1.2345, locale='sv_SE')
    u'1,234'
    >>> format_decimal(12345, locale='de')
    u'12.345'

    The appropriate thousands grouping and the decimal separator are used for
    each locale:
    
    >>> format_decimal(12345.5, locale='en_US')
    u'12,345.5'

    :param number: the number to format
    :param format: 
    :param locale: the `Locale` object or locale identifier
    :return: the formatted decimal number
    :rtype: `unicode`
    """
    locale = Locale.parse(locale)
    if not format:
        format = locale.decimal_formats.get(format)
    pattern = parse_pattern(format)
    return pattern.apply(number, locale)

def format_currency(number, currency, format=None, locale=LC_NUMERIC):
    """Return formatted currency value.
    
    >>> format_currency(1099.98, 'USD', locale='en_US')
    u'$1,099.98'
    >>> format_currency(1099.98, 'USD', locale='es_CO')
    u'US$1.099,98'
    >>> format_currency(1099.98, 'EUR', locale='de_DE')
    u'1.099,98 \\u20ac'
    
    The pattern can also be specified explicitly:
    
    >>> format_currency(1099.98, 'EUR', u'\xa4\xa4 #,##0.00', locale='en_US')
    u'EUR 1,099.98'
    
    :param number: the number to format
    :param currency: the currency code
    :param locale: the `Locale` object or locale identifier
    :return: the formatted currency value
    :rtype: `unicode`
    """
    locale = Locale.parse(locale)
    if not format:
        format = locale.currency_formats.get(format)
    pattern = parse_pattern(format)
    return pattern.apply(number, locale, currency=currency)

def format_percent(number, format=None, locale=LC_NUMERIC):
    """Return formatted percent value for a specific locale.
    
    >>> format_percent(0.34, locale='en_US')
    u'34%'
    >>> format_percent(25.1234, locale='en_US')
    u'2,512%'
    >>> format_percent(25.1234, locale='sv_SE')
    u'2\\xa0512 %'

    The format pattern can also be specified explicitly:
    
    >>> format_percent(25.1234, u'#,##0\u2030', locale='en_US')
    u'25,123\u2030'

    :param number: the percent number to format
    :param format: 
    :param locale: the `Locale` object or locale identifier
    :return: the formatted percent number
    :rtype: `unicode`
    """
    locale = Locale.parse(locale)
    if not format:
        format = locale.percent_formats.get(format)
    pattern = parse_pattern(format)
    return pattern.apply(number, locale)

def format_scientific(number, locale=LC_NUMERIC):
    # TODO: implement
    raise NotImplementedError


class NumberFormatError(ValueError):
    """Exception raised when a string cannot be parsed into a number."""


def parse_number(string, locale=LC_NUMERIC):
    """Parse localized number string into a long integer.
    
    >>> parse_number('1,099', locale='en_US')
    1099L
    >>> parse_number('1.099', locale='de_DE')
    1099L
    
    When the given string cannot be parsed, an exception is raised:
    
    >>> parse_number('1.099,98', locale='de')
    Traceback (most recent call last):
        ...
    NumberFormatError: '1.099,98' is not a valid number
    
    :param string: the string to parse
    :param locale: the `Locale` object or locale identifier
    :return: the parsed number
    :rtype: `long`
    :raise `NumberFormatError`: if the string can not be converted to a number
    """
    try:
        return long(string.replace(get_group_symbol(locale), ''))
    except ValueError:
        raise NumberFormatError('%r is not a valid number' % string)

def parse_decimal(string, locale=LC_NUMERIC):
    """Parse localized decimal string into a float.
    
    >>> parse_decimal('1,099.98', locale='en_US')
    1099.98
    >>> parse_decimal('1.099,98', locale='de')
    1099.98
    
    When the given string cannot be parsed, an exception is raised:
    
    >>> parse_decimal('2,109,998', locale='de')
    Traceback (most recent call last):
        ...
    NumberFormatError: '2,109,998' is not a valid decimal number
    
    :param string: the string to parse
    :param locale: the `Locale` object or locale identifier
    :return: the parsed decimal number
    :rtype: `float`
    :raise `NumberFormatError`: if the string can not be converted to a
                                decimal number
    """
    locale = Locale.parse(locale)
    try:
        return float(string.replace(get_group_symbol(locale), '')
                           .replace(get_decimal_symbol(locale), '.'))
    except ValueError:
        raise NumberFormatError('%r is not a valid decimal number' % string)


PREFIX_END = r'[^0-9@#.,]'
NUMBER_TOKEN = r'[0-9@#.\-,E]'

PREFIX_PATTERN = r"(?P<prefix>(?:'[^']*'|%s)*)" % PREFIX_END
NUMBER_PATTERN = r"(?P<number>%s+)" % NUMBER_TOKEN
SUFFIX_PATTERN = r"(?P<suffix>.*)"

number_re = re.compile(r"%s%s%s" % (PREFIX_PATTERN, NUMBER_PATTERN, 
                                    SUFFIX_PATTERN))

# TODO:
#  Filling
#  Rounding increment in pattern
#  Scientific notation
#  Significant Digits
def parse_pattern(pattern):
    """Parse number format patterns"""
    if isinstance(pattern, NumberPattern):
        return pattern

    # Do we have a negative subpattern?
    if ';' in pattern:
        pattern, neg_pattern = pattern.split(';', 1)
        pos_prefix, number, pos_suffix = number_re.search(pattern).groups()
        neg_prefix, _, neg_suffix = number_re.search(neg_pattern).groups()
    else:
        pos_prefix, number, pos_suffix = number_re.search(pattern).groups()
        neg_prefix = '-' + pos_prefix
        neg_suffix = pos_suffix
    if '.' in number:
        integer, fraction = number.rsplit('.', 1)
    else:
        integer = number
        fraction = ''
    min_frac = max_frac = 0

    def parse_precision(p):
        """Calculate the min and max allowed digits"""
        min = max = 0
        for c in p:
            if c == '0':
                min += 1
                max += 1
            elif c == '#':
                max += 1
            else:
                break
        return min, max

    def parse_grouping(p):
        """Parse primary and secondary digit grouping

        >>> parse_grouping('##')
        0, 0
        >>> parse_grouping('#,###')
        3, 3
        >>> parse_grouping('#,####,###')
        3, 4
        """
        width = len(p)
        g1 = p.rfind(',')
        if g1 == -1:
            return 1000, 1000
        g1 = width - g1 - 1
        g2 = p[:-g1 - 1].rfind(',')
        if g2 == -1:
            return g1, g1
        g2 = width - g1 - g2 - 2
        return g1, g2

    int_precision = parse_precision(integer)
    frac_precision = parse_precision(fraction)
    grouping = parse_grouping(integer)
    int_precision = (int_precision[0], 1000) # Unlimited
    return NumberPattern(pattern, (pos_prefix, neg_prefix), 
                         (pos_suffix, neg_suffix), grouping,
                         int_precision, frac_precision)


class NumberPattern(object):

    def __init__(self, pattern, prefix, suffix, grouping,
                 int_precision, frac_precision):
        self.pattern = pattern
        self.prefix = prefix
        self.suffix = suffix
        self.grouping = grouping
        self.int_precision = int_precision
        self.frac_precision = frac_precision
        self.format = '%%.%df' % self.frac_precision[1]
        if '%' in ''.join(self.prefix + self.suffix):
            self.scale = 100.0
        elif u'‰' in ''.join(self.prefix + self.suffix):
            self.scale = 1000.0
        else:
            self.scale = 1.0

    def __repr__(self):
        return '<%s %r>' % (type(self).__name__, self.pattern)

    def apply(self, value, locale, currency=None):
        value *= self.scale
        negative = int(value < 0)
        a = self.format % value
        if self.frac_precision[1] > 0:
            a, b = a.split('.')
        else:
            b = ''
        a = a.lstrip('-')
        retval = u'%s%s%s%s' % (self.prefix[negative],
                                self._format_int(a, locale),
                                self._format_frac(b, locale),
                                self.suffix[negative])
        if u'¤' in retval:
            retval = retval.replace(u'¤¤', currency.upper())
            retval = retval.replace(u'¤', get_currency_symbol(currency, locale))
        return retval

    def _format_int(self, value, locale):
        min, max = self.int_precision
        width = len(value)
        if width < min:
            value += '0' * (min - width)
        gsize = self.grouping[0]
        ret = ''
        symbol = get_group_symbol(locale)
        while len(value) > gsize:
            ret = symbol + value[-gsize:] + ret
            value = value[:-gsize]
            gsize = self.grouping[1]
        return value + ret

    def _format_frac(self, value, locale):
        min, max = self.frac_precision
        if max == 0 or (min == 0 and int(value) == 0):
            return ''
        width = len(value)
        while len(value) > min and value[-1] == '0':
            value = value[:-1]
        return get_decimal_symbol(locale) + value
