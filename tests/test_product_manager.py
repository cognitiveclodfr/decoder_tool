"""Unit tests for ProductManager"""
import pytest
import pandas as pd
from src.models.product_manager import ProductManager


class TestProductManager:
    """Test suite for ProductManager class"""

    @pytest.fixture
    def sample_products_df(self):
        """Create sample products DataFrame"""
        return pd.DataFrame({
            'Products_Name': ['Lavender Oil', 'Rose Oil', 'Tea Tree Oil'],
            'SKU': ['LAV-10ML', 'ROSE-10ML', 'TEA-10ML'],
            'Quantity_Product': [1, 1, 2]
        })

    @pytest.fixture
    def product_manager(self):
        """Create ProductManager instance"""
        return ProductManager()

    def test_initialization(self, product_manager):
        """Test ProductManager initializes with empty map"""
        assert product_manager.count() == 0
        assert product_manager.get_all_skus() == []

    def test_load_from_dataframe(self, product_manager, sample_products_df):
        """Test loading products from DataFrame"""
        product_manager.load_from_dataframe(sample_products_df)

        assert product_manager.count() == 3
        assert 'LAV-10ML' in product_manager.get_all_skus()

    def test_load_missing_columns(self, product_manager):
        """Test error handling for missing columns"""
        invalid_df = pd.DataFrame({'SKU': ['TEST']})

        with pytest.raises(ValueError, match="Missing required columns"):
            product_manager.load_from_dataframe(invalid_df)

    def test_duplicate_skus_keep_first(self, product_manager):
        """Test that duplicates are handled by keeping first"""
        df_with_dupes = pd.DataFrame({
            'Products_Name': ['First Product', 'Second Product'],
            'SKU': ['DUP-SKU', 'DUP-SKU'],
            'Quantity_Product': [1, 2]
        })

        product_manager.load_from_dataframe(df_with_dupes)

        assert product_manager.count() == 1
        product = product_manager.get_product('DUP-SKU')
        assert product['name'] == 'First Product'
        assert product['physical_qty'] == 1

    def test_get_product(self, product_manager, sample_products_df):
        """Test getting product by SKU"""
        product_manager.load_from_dataframe(sample_products_df)

        product = product_manager.get_product('LAV-10ML')
        assert product is not None
        assert product['name'] == 'Lavender Oil'
        assert product['physical_qty'] == 1

    def test_get_product_not_found(self, product_manager, sample_products_df):
        """Test getting non-existent product"""
        product_manager.load_from_dataframe(sample_products_df)

        product = product_manager.get_product('NONEXISTENT')
        assert product is None

    def test_get_product_name(self, product_manager, sample_products_df):
        """Test getting product name"""
        product_manager.load_from_dataframe(sample_products_df)

        name = product_manager.get_product_name('LAV-10ML')
        assert name == 'Lavender Oil'

    def test_get_product_name_fallback(self, product_manager, sample_products_df):
        """Test product name fallback for non-existent SKU"""
        product_manager.load_from_dataframe(sample_products_df)

        # Default fallback (SKU itself)
        name = product_manager.get_product_name('UNKNOWN')
        assert name == 'UNKNOWN'

        # Custom fallback
        name = product_manager.get_product_name('UNKNOWN', fallback='Not Found')
        assert name == 'Not Found'

    def test_get_product_quantity(self, product_manager, sample_products_df):
        """Test getting product quantity"""
        product_manager.load_from_dataframe(sample_products_df)

        qty = product_manager.get_product_quantity('TEA-10ML')
        assert qty == 2

    def test_get_product_quantity_fallback(self, product_manager, sample_products_df):
        """Test product quantity fallback for non-existent SKU"""
        product_manager.load_from_dataframe(sample_products_df)

        qty = product_manager.get_product_quantity('UNKNOWN')
        assert qty == 1  # Default fallback

        qty = product_manager.get_product_quantity('UNKNOWN', fallback=5)
        assert qty == 5

    def test_has_product(self, product_manager, sample_products_df):
        """Test checking if product exists"""
        product_manager.load_from_dataframe(sample_products_df)

        assert product_manager.has_product('LAV-10ML') is True
        assert product_manager.has_product('UNKNOWN') is False

    def test_clear(self, product_manager, sample_products_df):
        """Test clearing product map"""
        product_manager.load_from_dataframe(sample_products_df)
        assert product_manager.count() == 3

        product_manager.clear()
        assert product_manager.count() == 0
        assert product_manager.get_all_skus() == []
