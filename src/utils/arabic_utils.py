"""
Utilities for handling Arabic text
"""
import arabic_reshaper
from bidi.algorithm import get_display

def reshape_arabic_text(text):
    """
    Reshape Arabic text for proper display
    
    Args:
        text (str): Arabic text to reshape
        
    Returns:
        str: Reshaped Arabic text
    """
    if not text:
        return text
    
    try:
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        return bidi_text
    except Exception:
        return text

def normalize_arabic_text(text):
    """
    Normalize Arabic text for comparison and storage
    
    Args:
        text (str): Arabic text to normalize
        
    Returns:
        str: Normalized Arabic text
    """
    if not text:
        return text
    
    # Remove extra spaces
    text = ' '.join(text.split())
    
    # Remove diacritics
    arabic_diacritics = ['َ', 'ً', 'ُ', 'ٌ', 'ِ', 'ٍ', 'ّ', 'ْ']
    for diacritic in arabic_diacritics:
        text = text.replace(diacritic, '')
    
    return text.strip()

def is_arabic(text):
    """
    Check if text contains Arabic characters
    
    Args:
        text (str): Text to check
        
    Returns:
        bool: True if text contains Arabic characters
    """
    if not text:
        return False
    
    arabic_range = range(0x0600, 0x06FF + 1)
    return any(ord(char) in arabic_range for char in text)