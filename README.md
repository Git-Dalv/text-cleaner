# Text Cleaner

A comprehensive text cleaning module for web scraping and data processing projects. Handles HTML entities, Unicode artifacts, special characters, and formatting issues commonly encountered when extracting text from websites.

## Features

- Removes or normalizes 15+ types of quotation marks
- Handles 17+ types of special space characters (NBSP, em space, thin space, etc.)
- Normalizes 10+ dash and hyphen variations
- Decodes HTML entities and removes HTML tags
- Removes invisible and zero-width characters
- Unicode normalization and accent removal
- Configurable options for different use cases
- Both simple functions and class-based API

## Installation

Copy `text_cleaner.py` to your project or install as a package:

```bash
# Copy to project
cp text_cleaner.py your_project/

# Or install as editable package
pip install -e .
```

## Quick Start

```python
from text_cleaner import clean

# Basic cleaning
text = clean('"Dirty   text   here"')
# Result: 'Dirty text here'

# HTML content
text = clean('<p>Product&nbsp;name</p>')
# Result: 'Product name'

# Unicode issues
text = clean('Price:\xa0€99.99')
# Result: 'Price: €99.99'
```

## API Reference

### Simple Functions

```python
from text_cleaner import (
    clean,              # Universal cleaning
    clean_multiline,    # Preserves newlines
    clean_keep_quotes,  # Keeps quotation marks
    clean_product_name, # Product names
    clean_brand,        # Brand/vendor names
    clean_sku,          # SKU codes (uppercase)
    clean_description,  # Descriptions with newlines
    clean_price_text,   # Price strings (digits only)
    clean_url,          # URLs (minimal cleaning)
    clean_email,        # Email addresses
    remove_accents,     # Remove diacritics
    normalize_unicode,  # Unicode normalization
)
```

### Function Examples

```python
from text_cleaner import *

# Product name - removes quotes, normalizes spaces
clean_product_name('"Samsung Galaxy S24"')
# Result: 'Samsung Galaxy S24'

# Brand name
clean_brand('«Apple®»')
# Result: 'Apple®'

# SKU - uppercase, alphanumeric only
clean_sku('sku-123_abc')
# Result: 'SKU-123_ABC'

# Description - preserves line breaks
clean_description('<p>First paragraph</p><p>Second paragraph</p>')
# Result: 'First paragraph\n\nSecond paragraph'

# Price - extracts digits and decimals
clean_price_text('€1,299.99 EUR')
# Result: '1,299.99'

# URL - minimal cleaning
clean_url('  https://example.com/path  ')
# Result: 'https://example.com/path'

# Email - lowercase, stripped
clean_email('  USER@Example.COM  ')
# Result: 'user@example.com'

# Remove accents
remove_accents('café résumé naïve')
# Result: 'cafe resume naive'
```

### Class-Based API

For custom configurations, use the `TextCleaner` class:

```python
from text_cleaner import TextCleaner

# Custom cleaner
cleaner = TextCleaner(
    remove_quotes=False,       # Keep quotes
    preserve_newlines=True,    # Keep line breaks
    lowercase=True,            # Convert to lowercase
    max_length=200,            # Truncate long text
)

text = cleaner.clean(raw_html)
```

### Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `remove_quotes` | `True` | Remove all quotation mark types |
| `normalize_dashes` | `True` | Convert all dashes to standard hyphen |
| `normalize_spaces` | `True` | Convert special spaces to regular space |
| `remove_html_tags` | `True` | Strip HTML tags |
| `decode_html_entities` | `True` | Decode `&amp;` `&nbsp;` etc. |
| `remove_invisible` | `True` | Remove zero-width and control characters |
| `preserve_newlines` | `False` | Keep newlines (False = single line) |
| `lowercase` | `False` | Convert to lowercase |
| `max_length` | `None` | Truncate to max length |
| `allowed_chars` | `None` | Regex pattern of allowed characters |
| `extra_remove` | `None` | Additional characters to remove |

### Configuration Examples

```python
from text_cleaner import TextCleaner

# For product titles
product_cleaner = TextCleaner(
    remove_quotes=True,
    normalize_dashes=True,
    max_length=150,
)

# For descriptions
description_cleaner = TextCleaner(
    remove_quotes=False,
    preserve_newlines=True,
    max_length=5000,
)

# For search indexing
search_cleaner = TextCleaner(
    remove_quotes=True,
    lowercase=True,
    extra_remove='®™©',
)

# Strict alphanumeric only
strict_cleaner = TextCleaner(
    allowed_chars=r'\w\s',
)
```

## Handled Patterns

### Quotation Marks (15+ types)

| Character | Name |
|-----------|------|
| `"` | Standard double quote |
| `'` | Standard single quote |
| `«` `»` | French guillemets |
| `„` `"` | German quotes |
| `'` `'` | Single curly quotes |
| `"` `"` | Double curly quotes |
| `` ` `` `´` | Backtick and acute |
| `″` `′` | Prime marks |

### Special Spaces (17+ types)

| Character | Code | Name |
|-----------|------|------|
| ` ` | `\xa0` | Non-breaking space (NBSP) |
| ` ` | `\u2002` | En space |
| ` ` | `\u2003` | Em space |
| ` ` | `\u2009` | Thin space |
| ` ` | `\u200a` | Hair space |
| ​ | `\u200b` | Zero-width space |
| ` ` | `\u202f` | Narrow NBSP |
| `　` | `\u3000` | Ideographic space |
| `` | `\ufeff` | BOM / Zero-width NBSP |

### Dashes (10+ types)

| Character | Code | Name |
|-----------|------|------|
| `–` | `\u2013` | En dash |
| `—` | `\u2014` | Em dash |
| `‐` | `\u2010` | Hyphen |
| `‑` | `\u2011` | Non-breaking hyphen |
| `−` | `\u2212` | Minus sign |
| `－` | `\uff0d` | Fullwidth hyphen-minus |

### HTML Artifacts

| Pattern | Replacement |
|---------|-------------|
| `&nbsp;` | ` ` (space) |
| `NBSP` | ` ` (space) |
| `&amp;` | `&` |
| `&lt;` `&gt;` | `<` `>` |
| `&quot;` | `"` |
| `&mdash;` | `-` |
| `<br>` `<br/>` | `\n` (newline) |
| `<p>` | `\n` (newline) |

## Use Cases

### Web Scraping

```python
from text_cleaner import clean, clean_description

# Product data extraction
product = {
    'name': clean(raw_name),
    'brand': clean(raw_brand),
    'description': clean_description(raw_html),
    'price': clean_price_text(raw_price),
}
```

### Data Cleaning Pipeline

```python
from text_cleaner import TextCleaner
import pandas as pd

cleaner = TextCleaner()

df['product_name'] = df['product_name'].apply(cleaner.clean)
df['description'] = df['description'].apply(cleaner.clean_description)
```

### Search Indexing

```python
from text_cleaner import TextCleaner, remove_accents

search_cleaner = TextCleaner(lowercase=True)

def prepare_for_search(text):
    text = search_cleaner.clean(text)
    text = remove_accents(text)
    return text
```

### CSV/Excel Export

```python
from text_cleaner import clean

# Clean data before export to prevent encoding issues
clean_data = []
for row in raw_data:
    clean_data.append({
        'name': clean(row['name']),
        'description': clean(row['description']),
    })
```

## Utility Methods

### Unicode Normalization

```python
from text_cleaner import normalize_unicode

# Forms: NFC, NFD, NFKC (recommended), NFKD
text = normalize_unicode('café', form='NFKC')
```

### Accent Removal

```python
from text_cleaner import remove_accents

remove_accents('Zürich café naïve')
# Result: 'Zurich cafe naive'
```

### Text Truncation

```python
from text_cleaner import TextCleaner

cleaner = TextCleaner()
cleaner.truncate('Long text here that needs to be shortened', max_length=20)
# Result: 'Long text here...'
```

### Empty Check

```python
from text_cleaner import TextCleaner

cleaner = TextCleaner()
cleaner.is_empty('   ')      # True
cleaner.is_empty('\xa0')     # True
cleaner.is_empty('text')     # False
```

## Testing

Run the built-in tests:

```bash
python text_cleaner.py
```

Output:

```
TextCleaner Tests
==================================================
'"Product   Name"'                       -> 'Product Name'
'Text\xa0with\xa0NBSP'                   -> 'Text with NBSP'
'Dashes – — test'                        -> 'Dashes - - test'
'  Multiple   spaces  '                  -> 'Multiple spaces'
'<p>HTML &amp; entities</p>'             -> 'HTML & entities'
...
```

## Performance

The module precompiles regex patterns at initialization for better performance when processing large datasets:

```python
from text_cleaner import TextCleaner

# Create once, reuse many times
cleaner = TextCleaner()

# Process thousands of items efficiently
results = [cleaner.clean(item) for item in large_list]
```

## Dependencies

- Python 3.9+
- No external dependencies (uses only standard library)

## License

MIT License - free for personal and commercial use.
