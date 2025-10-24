"""Utility functions for SKU generation and validation"""
import re
from typing import Optional


def generate_sku_from_name(product_name: str) -> str:
    """
    Generate SKU from product name by converting to uppercase and replacing spaces with underscores

    Examples:
        "Barrier Cream Sample" -> "BARRIER_CREAM_SAMPLE"
        "Face Oil Sample" -> "FACE_OIL_SAMPLE"
        "Product  with   spaces" -> "PRODUCT_WITH_SPACES"

    Args:
        product_name: Product name to convert

    Returns:
        Generated SKU string
    """
    if not product_name or not isinstance(product_name, str):
        return "UNKNOWN_PRODUCT"

    # Remove special characters except spaces and alphanumeric
    cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', product_name)

    # Replace multiple spaces with single space
    cleaned = re.sub(r'\s+', ' ', cleaned)

    # Strip leading/trailing spaces
    cleaned = cleaned.strip()

    # Convert to uppercase and replace spaces with underscores
    sku = cleaned.upper().replace(' ', '_')

    return sku if sku else "UNKNOWN_PRODUCT"


def is_empty_sku(sku) -> bool:
    """
    Check if SKU is empty or invalid

    Args:
        sku: SKU value to check

    Returns:
        True if SKU is empty, None, NaN, or whitespace only
    """
    if sku is None:
        return True

    # Handle pandas NaN
    try:
        import math
        if math.isnan(sku):
            return True
    except (TypeError, ValueError):
        pass

    # Convert to string and check if empty or whitespace
    sku_str = str(sku).strip()

    # Check for common empty indicators
    if not sku_str or sku_str.lower() in ['nan', 'none', 'null', '']:
        return True

    return False


def validate_sku(sku: str) -> tuple[bool, Optional[str]]:
    """
    Validate SKU format

    Args:
        sku: SKU to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if is_empty_sku(sku):
        return False, "SKU is empty"

    sku_str = str(sku).strip()

    # Check length
    if len(sku_str) < 2:
        return False, "SKU too short (minimum 2 characters)"

    if len(sku_str) > 100:
        return False, "SKU too long (maximum 100 characters)"

    # Check for valid characters (alphanumeric, dash, underscore)
    if not re.match(r'^[A-Z0-9\-_]+$', sku_str):
        return False, "SKU contains invalid characters (use A-Z, 0-9, -, _)"

    return True, None


def sanitize_sku(sku: str) -> str:
    """
    Clean and sanitize SKU

    Args:
        sku: SKU to sanitize

    Returns:
        Sanitized SKU
    """
    if is_empty_sku(sku):
        return ""

    # Convert to string and uppercase
    sku_str = str(sku).strip().upper()

    # Remove invalid characters
    sku_str = re.sub(r'[^A-Z0-9\-_]', '', sku_str)

    return sku_str
