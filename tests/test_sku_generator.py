"""Unit tests for SKU generator utility"""
import pytest
import math
from src.utils.sku_generator import (
    generate_sku_from_name,
    is_empty_sku,
    validate_sku,
    sanitize_sku
)


class TestGenerateSkuFromName:
    """Test suite for generate_sku_from_name function"""

    def test_basic_conversion(self):
        """Test basic name to SKU conversion"""
        assert generate_sku_from_name("Barrier Cream Sample") == "BARRIER_CREAM_SAMPLE"
        assert generate_sku_from_name("Face Oil Sample") == "FACE_OIL_SAMPLE"
        assert generate_sku_from_name("Chamomile Tester") == "CHAMOMILE_TESTER"

    def test_lowercase_to_uppercase(self):
        """Test lowercase conversion"""
        assert generate_sku_from_name("lavender oil") == "LAVENDER_OIL"
        assert generate_sku_from_name("test product") == "TEST_PRODUCT"

    def test_multiple_spaces(self):
        """Test handling of multiple spaces"""
        assert generate_sku_from_name("Product  with   spaces") == "PRODUCT_WITH_SPACES"
        assert generate_sku_from_name("Too    Many    Spaces") == "TOO_MANY_SPACES"

    def test_special_characters_removed(self):
        """Test removal of special characters"""
        assert generate_sku_from_name("Product & Test") == "PRODUCT_TEST"
        assert generate_sku_from_name("Test-Product") == "TESTPRODUCT"
        assert generate_sku_from_name("Product (Sample)") == "PRODUCT_SAMPLE"
        assert generate_sku_from_name("100% Natural") == "100_NATURAL"

    def test_leading_trailing_spaces(self):
        """Test trimming of leading/trailing spaces"""
        assert generate_sku_from_name("  Product Name  ") == "PRODUCT_NAME"
        assert generate_sku_from_name("\tTabbed\t") == "TABBED"

    def test_numbers_preserved(self):
        """Test that numbers are preserved"""
        assert generate_sku_from_name("Cream 50ml") == "CREAM_50ML"
        assert generate_sku_from_name("Set 3 Pack") == "SET_3_PACK"

    def test_empty_or_none(self):
        """Test handling of empty or None input"""
        assert generate_sku_from_name("") == "UNKNOWN_PRODUCT"
        assert generate_sku_from_name(None) == "UNKNOWN_PRODUCT"
        assert generate_sku_from_name("   ") == "UNKNOWN_PRODUCT"

    def test_only_special_characters(self):
        """Test handling of names with only special characters"""
        assert generate_sku_from_name("!!!") == "UNKNOWN_PRODUCT"
        assert generate_sku_from_name("---") == "UNKNOWN_PRODUCT"


class TestIsEmptySku:
    """Test suite for is_empty_sku function"""

    def test_truly_empty(self):
        """Test detection of empty values"""
        assert is_empty_sku("") is True
        assert is_empty_sku(None) is True
        assert is_empty_sku("   ") is True

    def test_nan_values(self):
        """Test detection of NaN values"""
        assert is_empty_sku(float('nan')) is True

    def test_string_representations(self):
        """Test detection of string representations of empty"""
        assert is_empty_sku("nan") is True
        assert is_empty_sku("None") is True
        assert is_empty_sku("null") is True
        assert is_empty_sku("NaN") is True

    def test_valid_skus(self):
        """Test that valid SKUs are not marked as empty"""
        assert is_empty_sku("LAV-10ML") is False
        assert is_empty_sku("TEST_SKU") is False
        assert is_empty_sku("123") is False
        assert is_empty_sku("A") is False

    def test_with_whitespace(self):
        """Test SKUs with whitespace"""
        assert is_empty_sku("  LAV-10ML  ") is False  # Has content after strip


class TestValidateSku:
    """Test suite for validate_sku function"""

    def test_valid_skus(self):
        """Test validation of valid SKUs"""
        valid, err = validate_sku("LAV-10ML")
        assert valid is True
        assert err is None

        valid, err = validate_sku("TEST_SKU_123")
        assert valid is True
        assert err is None

    def test_empty_sku(self):
        """Test validation of empty SKU"""
        valid, err = validate_sku("")
        assert valid is False
        assert "empty" in err.lower()

    def test_too_short(self):
        """Test validation of too short SKU"""
        valid, err = validate_sku("A")
        assert valid is False
        assert "short" in err.lower()

    def test_too_long(self):
        """Test validation of very long SKU"""
        long_sku = "A" * 101
        valid, err = validate_sku(long_sku)
        assert valid is False
        assert "long" in err.lower()

    def test_invalid_characters(self):
        """Test validation of SKU with invalid characters"""
        valid, err = validate_sku("sku with spaces")
        assert valid is False
        assert "invalid" in err.lower()

        valid, err = validate_sku("sku@email")
        assert valid is False

    def test_lowercase_not_allowed(self):
        """Test that lowercase letters are not allowed"""
        valid, err = validate_sku("lowercase")
        assert valid is False


class TestSanitizeSku:
    """Test suite for sanitize_sku function"""

    def test_basic_sanitization(self):
        """Test basic SKU sanitization"""
        assert sanitize_sku("test-sku") == "TEST-SKU"
        assert sanitize_sku("test_sku") == "TEST_SKU"

    def test_remove_invalid_characters(self):
        """Test removal of invalid characters"""
        assert sanitize_sku("test sku") == "TESTSKU"  # Spaces removed
        assert sanitize_sku("test@sku") == "TESTSKU"  # @ removed
        assert sanitize_sku("test.sku") == "TESTSKU"  # . removed

    def test_preserve_valid_characters(self):
        """Test preservation of valid characters"""
        assert sanitize_sku("TEST-SKU_123") == "TEST-SKU_123"
        assert sanitize_sku("ABC123") == "ABC123"

    def test_empty_input(self):
        """Test handling of empty input"""
        assert sanitize_sku("") == ""
        assert sanitize_sku(None) == ""

    def test_whitespace_trimming(self):
        """Test trimming of whitespace"""
        assert sanitize_sku("  TEST-SKU  ") == "TEST-SKU"
