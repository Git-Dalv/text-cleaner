"""
Universal Text Cleaner
A comprehensive text cleaning module for web scraping projects.
Handles HTML entities, Unicode artifacts, special characters, and formatting issues.
"""

import re
import html
import unicodedata
from typing import Optional, Set


class TextCleaner:
    """
    Universal text cleaner that handles common web scraping text issues.

    Usage:
        # Simple
        from text_cleaner import clean
        text = clean('"Dirty"  text   here')

        # With options
        from text_cleaner import TextCleaner
        cleaner = TextCleaner(preserve_newlines=True)
        text = cleaner.clean(html_content)
    """

    # ===========================================
    # Character patterns
    # ===========================================

    # All quote variations
    QUOTES = (
        '\"'      # Standard double quote
        "\'"      # Standard single quote
        '«»'     # French quotes
        '„"'     # German quotes
        '‟"'     # Double high quotes
        '\''      # Single curly quotes
        '‛'      # Single high quote
        '`´'     # Backtick and acute
        '″′'     # Prime marks
        '〝〞'   # Japanese quotes
        '＂'     # Fullwidth quote
    )

    # Special space characters
    SPECIAL_SPACES = {
        '\xa0',      # NBSP (non-breaking space)
        '\u00a0',    # NBSP (alternative)
        '\u2000',    # En quad
        '\u2001',    # Em quad
        '\u2002',    # En space
        '\u2003',    # Em space
        '\u2004',    # Three-per-em space
        '\u2005',    # Four-per-em space
        '\u2006',    # Six-per-em space
        '\u2007',    # Figure space
        '\u2008',    # Punctuation space
        '\u2009',    # Thin space
        '\u200a',    # Hair space
        '\u200b',    # Zero-width space
        '\u202f',    # Narrow NBSP
        '\u205f',    # Medium mathematical space
        '\u3000',    # Ideographic space
        '\ufeff',    # BOM / Zero-width NBSP
    }

    # Dash variations -> standard hyphen
    DASHES = {
        '–': '-',    # En dash
        '—': '-',    # Em dash
        '―': '-',    # Horizontal bar
        '‐': '-',    # Hyphen
        '‑': '-',    # Non-breaking hyphen
        '‒': '-',    # Figure dash
        '−': '-',    # Minus sign
        '⁃': '-',    # Hyphen bullet
        '﹣': '-',   # Small hyphen-minus
        '－': '-',   # Fullwidth hyphen-minus
    }

    # Common HTML entities (text representations)
    HTML_ENTITIES = {
        '&nbsp;': ' ',
        '&amp;': '&',
        '&lt;': '<',
        '&gt;': '>',
        '&quot;': '"',
        '&apos;': "'",
        '&#39;': "'",
        '&#34;': '"',
        '&mdash;': '-',
        '&ndash;': '-',
        '&bull;': '•',
        '&copy;': '©',
        '&reg;': '®',
        '&trade;': '™',
        '&euro;': '€',
        '&pound;': '£',
        '&yen;': '¥',
        '&cent;': '¢',
        '&deg;': '°',
        '&plusmn;': '±',
        '&times;': '×',
        '&divide;': '÷',
        '&frac12;': '½',
        '&frac14;': '¼',
        '&frac34;': '¾',
    }

    # Invisible/control characters to remove
    INVISIBLE_CHARS = set(
        chr(i) for i in range(32) if chr(i) not in '\t\n\r'
    ) | {
        '\u200c',    # Zero-width non-joiner
        '\u200d',    # Zero-width joiner
        '\u2060',    # Word joiner
        '\u2063',    # Invisible separator
        '\u2064',    # Invisible plus
        '\ufffe',    # Invalid Unicode
        '\uffff',    # Invalid Unicode
        '\ufffd',    # Replacement character
    }

    # ===========================================
    # Initialization
    # ===========================================

    def __init__(
        self,
        remove_quotes: bool = True,
        normalize_dashes: bool = True,
        normalize_spaces: bool = True,
        remove_html_tags: bool = True,
        decode_html_entities: bool = True,
        remove_invisible: bool = True,
        preserve_newlines: bool = False,
        lowercase: bool = False,
        max_length: Optional[int] = None,
        allowed_chars: Optional[str] = None,
        extra_remove: Optional[str] = None,
    ):
        """
        Initialize TextCleaner with options.

        Args:
            remove_quotes: Remove all quote characters
            normalize_dashes: Convert all dash types to standard hyphen
            normalize_spaces: Convert special spaces to regular space
            remove_html_tags: Strip HTML tags
            decode_html_entities: Decode &amp; &nbsp; etc.
            remove_invisible: Remove zero-width and control characters
            preserve_newlines: Keep newlines (False = single line output)
            lowercase: Convert to lowercase
            max_length: Truncate to max length (None = no limit)
            allowed_chars: Regex pattern of allowed chars (None = default)
            extra_remove: Additional characters to remove
        """
        self.remove_quotes = remove_quotes
        self.normalize_dashes = normalize_dashes
        self.normalize_spaces = normalize_spaces
        self.remove_html_tags = remove_html_tags
        self.decode_html_entities = decode_html_entities
        self.remove_invisible = remove_invisible
        self.preserve_newlines = preserve_newlines
        self.lowercase = lowercase
        self.max_length = max_length
        self.allowed_chars = allowed_chars
        self.extra_remove = extra_remove or ''

        # Precompile patterns
        self._compile_patterns()

    def _compile_patterns(self):
        """Precompile regex patterns for performance."""
        # Quote pattern
        self._quote_pattern = re.compile(f'[{re.escape(self.QUOTES)}]')

        # HTML tag pattern
        self._html_tag_pattern = re.compile(r'<[^>]+>')

        # Multiple spaces
        self._multi_space_pattern = re.compile(r'[ \t]+')

        # Multiple newlines
        self._multi_newline_pattern = re.compile(r'\n\s*\n+')

        # Special spaces pattern
        self._special_space_pattern = re.compile(
            '[' + ''.join(re.escape(c) for c in self.SPECIAL_SPACES) + ']'
        )

        # Invisible chars pattern
        self._invisible_pattern = re.compile(
            '[' + ''.join(re.escape(c) for c in self.INVISIBLE_CHARS) + ']'
        )

    # ===========================================
    # Main cleaning method
    # ===========================================

    def clean(self, text) -> str:
        """
        Clean text with all configured options.

        Args:
            text: Input text (str or any type)

        Returns:
            Cleaned string
        """
        # Handle None and non-string
        if text is None:
            return ''

        if not isinstance(text, str):
            text = str(text)

        if not text:
            return ''

        # 1. Decode HTML entities first
        if self.decode_html_entities:
            text = html.unescape(text)
            # Also handle text entity patterns like &nbsp;
            for entity, replacement in self.HTML_ENTITIES.items():
                text = text.replace(entity, replacement)

        # 2. Remove HTML tags
        if self.remove_html_tags:
            # Convert <br> to newlines before removing tags
            text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
            text = re.sub(r'</?p\s*/?>', '\n', text, flags=re.IGNORECASE)
            text = re.sub(r'<li[^>]*>', '\n• ', text, flags=re.IGNORECASE)
            text = self._html_tag_pattern.sub('', text)

        # 3. Remove invisible characters
        if self.remove_invisible:
            text = self._invisible_pattern.sub('', text)

        # 4. Normalize special spaces
        if self.normalize_spaces:
            text = self._special_space_pattern.sub(' ', text)

        # 5. Normalize dashes
        if self.normalize_dashes:
            for dash, replacement in self.DASHES.items():
                text = text.replace(dash, replacement)

        # 6. Remove quotes (replace with space to preserve word boundaries)
        if self.remove_quotes:
            text = self._quote_pattern.sub(' ', text)

        # 7. Remove extra characters
        if self.extra_remove:
            text = re.sub(f'[{re.escape(self.extra_remove)}]', '', text)

        # 8. Filter to allowed characters only
        if self.allowed_chars:
            text = re.sub(f'[^{self.allowed_chars}]', '', text)

        # 9. Handle whitespace (must be after all replacements)
        if self.preserve_newlines:
            # Normalize spaces but keep newlines
            text = self._multi_space_pattern.sub(' ', text)
            text = self._multi_newline_pattern.sub('\n\n', text)
            # Clean each line
            lines = [line.strip() for line in text.split('\n')]
            text = '\n'.join(lines)
        else:
            # Everything to single line
            text = text.replace('\n', ' ').replace('\r', ' ')
            text = self._multi_space_pattern.sub(' ', text)

        # 10. Lowercase
        if self.lowercase:
            text = text.lower()

        # 11. Strip
        text = text.strip()

        # 12. Truncate
        if self.max_length and len(text) > self.max_length:
            text = text[:self.max_length].rsplit(' ', 1)[0] + '...'

        return text

    # ===========================================
    # Specialized cleaning methods
    # ===========================================

    def clean_product_name(self, text) -> str:
        """Clean product name - removes quotes, normalizes spaces."""
        return self.clean(text)

    def clean_brand(self, text) -> str:
        """Clean brand/vendor name."""
        return self.clean(text)

    def clean_sku(self, text) -> str:
        """Clean SKU - keeps alphanumeric and basic punctuation."""
        if not text:
            return ''
        text = self.clean(text)
        # SKU typically alphanumeric with dashes/underscores
        text = re.sub(r'[^\w\-.]', '', text)
        return text.upper()

    def clean_description(self, text) -> str:
        """Clean product description - preserves newlines."""
        cleaner = TextCleaner(
            remove_quotes=False,
            preserve_newlines=True,
        )
        return cleaner.clean(text)

    def clean_price_text(self, text) -> str:
        """Extract price string - keeps digits, dots, commas."""
        if not text:
            return ''
        text = html.unescape(str(text))
        # Keep only digits and decimal separators
        text = re.sub(r'[^\d.,]', '', text)
        return text.strip()

    def clean_url(self, text) -> str:
        """Clean URL - minimal cleaning."""
        if not text:
            return ''
        text = str(text).strip()
        # Remove invisible characters only
        text = self._invisible_pattern.sub('', text)
        return text

    def clean_email(self, text) -> str:
        """Clean email address."""
        if not text:
            return ''
        text = str(text).strip().lower()
        text = self._invisible_pattern.sub('', text)
        text = self._special_space_pattern.sub('', text)
        return text

    # ===========================================
    # Utility methods
    # ===========================================

    def normalize_unicode(self, text: str, form: str = 'NFKC') -> str:
        """
        Normalize Unicode text.

        Forms:
            NFC: Canonical composition
            NFD: Canonical decomposition
            NFKC: Compatibility composition (recommended)
            NFKD: Compatibility decomposition
        """
        if not text:
            return ''
        return unicodedata.normalize(form, text)

    def remove_accents(self, text: str) -> str:
        """Remove accents from characters (e -> e)."""
        if not text:
            return ''
        # Decompose then remove combining marks
        normalized = unicodedata.normalize('NFD', text)
        return ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')

    def truncate(self, text: str, max_length: int, suffix: str = '...') -> str:
        """Truncate text at word boundary."""
        if not text or len(text) <= max_length:
            return text or ''
        truncated = text[:max_length].rsplit(' ', 1)[0]
        return truncated + suffix

    def is_empty(self, text) -> bool:
        """Check if text is empty after cleaning."""
        return not bool(self.clean(text))


# ===========================================
# Module-level functions (simple API)
# ===========================================

# Default cleaner instance
_default_cleaner = TextCleaner()

# Cleaner with newlines preserved
_multiline_cleaner = TextCleaner(preserve_newlines=True)

# Cleaner that keeps quotes
_keep_quotes_cleaner = TextCleaner(remove_quotes=False)


def clean(text) -> str:
    """Clean text with default settings."""
    return _default_cleaner.clean(text)


def clean_multiline(text) -> str:
    """Clean text preserving newlines."""
    return _multiline_cleaner.clean(text)


def clean_keep_quotes(text) -> str:
    """Clean text but keep quotes."""
    return _keep_quotes_cleaner.clean(text)


def clean_product_name(text) -> str:
    """Clean product name."""
    return _default_cleaner.clean_product_name(text)


def clean_brand(text) -> str:
    """Clean brand/vendor name."""
    return _default_cleaner.clean_brand(text)


def clean_sku(text) -> str:
    """Clean SKU code."""
    return _default_cleaner.clean_sku(text)


def clean_description(text) -> str:
    """Clean description with newlines."""
    return _default_cleaner.clean_description(text)


def clean_price_text(text) -> str:
    """Clean price string."""
    return _default_cleaner.clean_price_text(text)


def clean_url(text) -> str:
    """Clean URL."""
    return _default_cleaner.clean_url(text)


def clean_email(text) -> str:
    """Clean email address."""
    return _default_cleaner.clean_email(text)


def normalize_unicode(text: str, form: str = 'NFKC') -> str:
    """Normalize Unicode."""
    return _default_cleaner.normalize_unicode(text, form)


def remove_accents(text: str) -> str:
    """Remove accents."""
    return _default_cleaner.remove_accents(text)


# ===========================================
# Quick test
# ===========================================

if __name__ == '__main__':
    # Test cases
    tests = [
        '""'"Product  "" Name"'""',
        'Text\xa0with\xa0NBSP',
        'Dashes – — test',
        '  Multiple   spaces  ',
        '<p>HTML &amp; entities</p>',
        'Price: €99.99',
        'Unicode: café résumé',
        '"«Quotes»„everywhere"',
        'SKU-123_ABC',
        None,
        '',
        123,
    ]

    print("TextCleaner Tests")
    print("=" * 50)

    for test in tests:
        result = clean(test)
        print(f"{repr(test):40} -> {repr(result)}")