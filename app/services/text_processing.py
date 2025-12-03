import re
import unicodedata
from spellchecker import SpellChecker


class TextProcessor:
    """
    Offline text processing for OCR output
    - Unicode normalization
    - OCR error correction (rule-based)
    - Spell checking
    """

    # Common OCR character substitution errors
    OCR_CORRECTIONS = {
        '0': 'o', 'O': '0',
        '1': 'l', 'l': '1', 'I': '1',
        '5': 's', 'S': '5',
        '8': 'B', 'B': '8',
        '6': 'G', 'G': '6',
        '2': 'Z', 'Z': '2',
        '|': 'l',
        'rn': 'm',
        'vv': 'w',
        'cl': 'd',
    }

    # Context-aware patterns for correction
    CONTEXT_PATTERNS = [
        # Numbers in words should be letters
        (r'\b(\w*)0(\w+)\b', r'\1o\2'),  # w0rd -> word
        (r'\b(\w+)0(\w*)\b', r'\1o\2'),
        (r'\b(\w*)1(\w+)\b', r'\1l\2'),  # he11o -> hello
        (r'\b(\w+)1(\w*)\b', r'\1l\2'),
        (r'\b(\w*)5(\w+)\b', r'\1s\2'),  # te5t -> test
        (r'\b(\w+)5(\w*)\b', r'\1s\2'),
    ]

    def __init__(self, language='en'):
        self.language = language
        self.spell_checker = SpellChecker(language=language) if language == 'en' else None

    @staticmethod
    def normalize_unicode(text):
        """Normalize Unicode characters"""
        # NFC normalization
        text = unicodedata.normalize('NFC', text)
        return text

    @staticmethod
    def normalize_whitespace(text):
        """Normalize whitespace and line breaks"""
        # Replace multiple spaces with single space
        text = re.sub(r'[ \t]+', ' ', text)
        # Normalize line breaks
        text = re.sub(r'\r\n', '\n', text)
        text = re.sub(r'\r', '\n', text)
        # Remove excessive line breaks (more than 2)
        text = re.sub(r'\n{3,}', '\n\n', text)
        # Strip leading/trailing whitespace from each line
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        return text.strip()

    def apply_ocr_rules(self, text):
        """Apply rule-based OCR error corrections"""
        # Apply context-aware patterns
        for pattern, replacement in self.CONTEXT_PATTERNS:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        # Fix common multi-character errors
        text = text.replace('rn', 'm')  # Often misread
        text = text.replace('vv', 'w')
        text = text.replace('cl', 'd')

        return text

    def spell_check(self, text):
        """Apply spell checking (English only for now)"""
        if self.spell_checker is None:
            return text

        words = text.split()
        corrected_words = []

        for word in words:
            # Skip if word contains numbers or special chars
            if not word.isalpha():
                corrected_words.append(word)
                continue

            # Check if word is misspelled
            if word.lower() not in self.spell_checker:
                correction = self.spell_checker.correction(word.lower())
                if correction and correction != word.lower():
                    # Preserve original case
                    if word.isupper():
                        correction = correction.upper()
                    elif word[0].isupper():
                        correction = correction.capitalize()
                    corrected_words.append(correction)
                else:
                    corrected_words.append(word)
            else:
                corrected_words.append(word)

        return ' '.join(corrected_words)

    def process(self, text, apply_spell_check=True):
        """
        Full text processing pipeline
        1. Normalize Unicode
        2. Normalize whitespace
        3. Apply OCR rules
        4. Spell check (optional)
        """
        text = self.normalize_unicode(text)
        text = self.normalize_whitespace(text)
        text = self.apply_ocr_rules(text)

        if apply_spell_check and self.language == 'en':
            text = self.spell_check(text)

        return text
