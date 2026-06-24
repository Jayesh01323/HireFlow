"""
Text Cleaner Module

Provides utility functions for text cleaning and preprocessing.
Includes functions for removing noise, normalizing text, and extracting structured information.
"""

from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)


def clean_text(text: str) -> str:
    """Clean and normalize text."""
    # TODO: Implement text cleaning logic
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text)
    
    # Remove special characters (keep basic punctuation)
    text = re.sub(r"[^\w\s.,!?-]", "", text)
    
    return text.strip()


def remove_html_tags(text: str) -> str:
    """Remove HTML tags from text."""
    # TODO: Implement HTML tag removal
    if not text:
        return ""
    
    # Simple regex-based HTML tag removal
    text = re.sub(r"<[^>]+>", "", text)
    return text


def extract_emails(text: str) -> list[str]:
    """Extract email addresses from text."""
    # TODO: Implement email extraction
    if not text:
        return []
    
    pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    return re.findall(pattern, text)


def extract_phone_numbers(text: str) -> list[str]:
    """Extract phone numbers from text."""
    # TODO: Implement phone number extraction
    if not text:
        return []
    
    pattern = r"\+?[\d\s-]{10,}"
    return re.findall(pattern, text)


def extract_urls(text: str) -> list[str]:
    """Extract URLs from text."""
    # TODO: Implement URL extraction
    if not text:
        return []
    
    pattern = r"https?://[^\s<>\"]+|www\.[^\s<>\"]+"
    return re.findall(pattern, text)


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text."""
    if not text:
        return ""
    
    # Replace tabs with spaces
    text = text.replace("\t", " ")
    
    # Replace multiple spaces with single space
    text = re.sub(r" +", " ", text)
    
    # Replace multiple newlines with single newline
    text = re.sub(r"\n+", "\n", text)
    
    # Replace multiple carriage returns with single
    text = re.sub(r"\r+", "\r", text)
    
    # Remove leading/trailing whitespace from each line
    lines = text.split("\n")
    lines = [line.strip() for line in lines]
    text = "\n".join(lines)
    
    return text.strip()


def truncate_text(text: str, max_length: int = 500, suffix: str = "...") -> str:
    """Truncate text to maximum length with suffix, respecting word boundaries."""
    if not text or len(text) <= max_length:
        return text
    
    if len(suffix) >= max_length:
        return text[:max_length]
    
    # Truncate at word boundary
    truncated = text[: max_length - len(suffix)]
    
    # Find last space to avoid cutting words
    last_space = truncated.rfind(" ")
    if last_space > max_length // 2:  # Only if we have enough text
        truncated = truncated[:last_space]
    
    return truncated.strip() + suffix


def remove_special_characters(text: str, keep_punctuation: bool = True) -> str:
    """Remove special characters from text with unicode support."""
    if not text:
        return ""
    
    if keep_punctuation:
        # Keep basic punctuation and unicode letters/numbers
        pattern = r"[^\w\s.,!?\-\u0080-\uFFFF]"
    else:
        # Remove all non-alphanumeric characters except unicode
        pattern = r"[^\w\s\u0080-\uFFFF]"
    
    return re.sub(pattern, "", text)
