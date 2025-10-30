"""Tests for ColumnMapper module"""
import pytest
import pandas as pd
from src.models.client_profile import ClientProfile
from src.utils.column_mapper import ColumnMapper, create_mapper_from_profile, detect_platform


class TestColumnMapper:
    """Test ColumnMapper class"""

    @pytest.fixture
    def woocommerce_profile(self):
        """Create WooCommerce profile for testing"""
        return ClientProfile(
            client_id="WOO001",
            client_name="WooCommerce Client",
            column_mapping={
                "Order ID": "Name",
                "Ordered at": "Created at"
            },
            platform="WooCommerce"
        )

    @pytest.fixture
    def sample_woocommerce_df(self):
        """Create sample WooCommerce DataFrame"""
        return pd.DataFrame({
            'Order ID': ['#1001', '#1002', '#1003'],
            'Ordered at': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'Lineitem sku': ['SKU001', 'SKU002', 'SKU003'],
            'Lineitem quantity': [1, 2, 3],
            'Lineitem name': ['Product 1', 'Product 2', 'Product 3']
        })

    def test_create_mapper_without_profile(self):
        """Test creating mapper without profile"""
        mapper = ColumnMapper()

        assert not mapper.has_mapping()
        assert mapper.profile is None

    def test_create_mapper_with_profile(self, woocommerce_profile):
        """Test creating mapper with profile"""
        mapper = ColumnMapper(woocommerce_profile)

        assert mapper.has_mapping()
        assert mapper.profile == woocommerce_profile

    def test_apply_mapping(self, woocommerce_profile, sample_woocommerce_df):
        """Test applying column mapping to DataFrame"""
        mapper = ColumnMapper(woocommerce_profile)
        result_df = mapper.apply_mapping(sample_woocommerce_df)

        # Check columns were renamed
        assert 'Name' in result_df.columns
        assert 'Created at' in result_df.columns
        assert 'Order ID' not in result_df.columns
        assert 'Ordered at' not in result_df.columns

        # Check data is preserved
        assert list(result_df['Name']) == ['#1001', '#1002', '#1003']
        assert list(result_df['Created at']) == ['2024-01-01', '2024-01-02', '2024-01-03']

        # Check unmapped columns remain
        assert 'Lineitem sku' in result_df.columns
        assert 'Lineitem quantity' in result_df.columns

    def test_apply_mapping_without_mapping(self):
        """Test applying mapping when no mapping defined"""
        mapper = ColumnMapper()
        df = pd.DataFrame({'Column1': [1, 2, 3]})

        result_df = mapper.apply_mapping(df)

        # Should return copy without changes
        assert list(result_df.columns) == ['Column1']
        pd.testing.assert_frame_equal(result_df, df)

    def test_apply_mapping_adds_missing_optional_columns(self, woocommerce_profile):
        """Test that missing optional columns are added with defaults"""
        mapper = ColumnMapper(woocommerce_profile)

        # DataFrame missing optional columns
        df = pd.DataFrame({
            'Order ID': ['#1001'],
            'Lineitem sku': ['SKU001'],
            'Lineitem quantity': [1]
        })

        result_df = mapper.apply_mapping(df)

        # Check required columns are present
        assert 'Name' in result_df.columns
        assert 'Lineitem sku' in result_df.columns
        assert 'Lineitem quantity' in result_df.columns

        # Check optional columns were added
        assert 'Lineitem price' in result_df.columns
        assert 'Lineitem discount' in result_df.columns
        assert 'Shipping Name' in result_df.columns

    def test_apply_mapping_missing_required_raises_error(self):
        """Test that missing required columns raises error"""
        profile = ClientProfile(
            client_id="TEST001",
            client_name="Test",
            column_mapping={"Order ID": "Name"}
        )
        mapper = ColumnMapper(profile)

        # DataFrame missing required column after mapping
        df = pd.DataFrame({
            'Order ID': ['#1001'],
            'Lineitem quantity': [1]
            # Missing Lineitem sku
        })

        with pytest.raises(ValueError, match="Missing required columns"):
            mapper.apply_mapping(df)

    def test_get_standard_column(self, woocommerce_profile):
        """Test getting standard column name"""
        mapper = ColumnMapper(woocommerce_profile)

        assert mapper.get_standard_column("Order ID") == "Name"
        assert mapper.get_standard_column("Ordered at") == "Created at"
        assert mapper.get_standard_column("Unknown") == "Unknown"

    def test_get_client_column(self, woocommerce_profile):
        """Test getting client column name (reverse mapping)"""
        mapper = ColumnMapper(woocommerce_profile)

        assert mapper.get_client_column("Name") == "Order ID"
        assert mapper.get_client_column("Created at") == "Ordered at"
        assert mapper.get_client_column("Unknown") is None

    def test_has_mapping(self, woocommerce_profile):
        """Test checking if mapper has mappings"""
        mapper_with = ColumnMapper(woocommerce_profile)
        mapper_without = ColumnMapper()

        assert mapper_with.has_mapping() is True
        assert mapper_without.has_mapping() is False

    def test_validate_mapping(self, woocommerce_profile):
        """Test validating column mapping"""
        mapper = ColumnMapper(woocommerce_profile)

        columns = ['Order ID', 'Ordered at', 'Lineitem sku', 'Lineitem quantity', 'Lineitem name']
        validation = mapper.validate_mapping(columns)

        # Check mapped columns
        assert len(validation['mapped']) == 2
        assert 'Order ID → Name' in validation['mapped']
        assert 'Ordered at → Created at' in validation['mapped']

        # Check unmapped columns
        assert 'Lineitem sku' in validation['unmapped']
        assert 'Lineitem quantity' in validation['unmapped']

        # Check no missing required columns
        assert len(validation['missing_required']) == 0

    def test_validate_mapping_with_missing_required(self):
        """Test validation with missing required columns"""
        profile = ClientProfile(
            client_id="TEST001",
            client_name="Test",
            column_mapping={"Order ID": "Name"}
        )
        mapper = ColumnMapper(profile)

        # Missing Lineitem sku and Lineitem quantity
        columns = ['Order ID', 'Product Name']
        validation = mapper.validate_mapping(columns)

        assert 'Lineitem sku' in validation['missing_required']
        assert 'Lineitem quantity' in validation['missing_required']
        assert len(validation['warnings']) > 0

    def test_get_mapping_summary(self, woocommerce_profile):
        """Test getting mapping summary"""
        mapper = ColumnMapper(woocommerce_profile)
        summary = mapper.get_mapping_summary()

        assert 'Column Mapping:' in summary
        assert 'Order ID → Name' in summary
        assert 'Ordered at → Created at' in summary

    def test_get_mapping_summary_no_mapping(self):
        """Test getting summary when no mapping"""
        mapper = ColumnMapper()
        summary = mapper.get_mapping_summary()

        assert 'No column mapping' in summary

    def test_create_mapper_from_profile(self, woocommerce_profile):
        """Test creating mapper from profile"""
        mapper = create_mapper_from_profile(woocommerce_profile)

        assert isinstance(mapper, ColumnMapper)
        assert mapper.has_mapping()
        assert mapper.get_standard_column("Order ID") == "Name"

    def test_detect_platform_shopify(self):
        """Test detecting Shopify platform"""
        columns = ['Name', 'Created at', 'Lineitem sku', 'Lineitem quantity']
        platform = detect_platform(columns)

        assert platform == 'Shopify'

    def test_detect_platform_woocommerce(self):
        """Test detecting WooCommerce platform"""
        columns = ['Order ID', 'Ordered at', 'Lineitem sku', 'Lineitem quantity']
        platform = detect_platform(columns)

        assert platform == 'WooCommerce'

    def test_detect_platform_unknown(self):
        """Test detecting unknown platform"""
        columns = ['Col1', 'Col2', 'Col3']
        platform = detect_platform(columns)

        assert platform == 'Unknown'

    def test_apply_mapping_preserves_original_df(self, woocommerce_profile, sample_woocommerce_df):
        """Test that apply_mapping doesn't modify original DataFrame"""
        mapper = ColumnMapper(woocommerce_profile)
        original_columns = list(sample_woocommerce_df.columns)

        mapper.apply_mapping(sample_woocommerce_df)

        # Original should be unchanged
        assert list(sample_woocommerce_df.columns) == original_columns
        assert 'Order ID' in sample_woocommerce_df.columns
        assert 'Name' not in sample_woocommerce_df.columns

    def test_apply_mapping_with_empty_dataframe(self, woocommerce_profile):
        """Test applying mapping to empty DataFrame"""
        mapper = ColumnMapper(woocommerce_profile)

        df = pd.DataFrame(columns=['Order ID', 'Ordered at', 'Lineitem sku', 'Lineitem quantity'])

        # Should work with empty dataframe as long as columns are present
        result = mapper.apply_mapping(df)
        assert 'Name' in result.columns
        assert 'Created at' in result.columns
        assert len(result) == 0

    def test_standard_columns_defined(self):
        """Test that standard columns are properly defined"""
        assert 'Name' in ColumnMapper.STANDARD_COLUMNS
        assert 'Lineitem sku' in ColumnMapper.STANDARD_COLUMNS
        assert 'Lineitem quantity' in ColumnMapper.STANDARD_COLUMNS

    def test_required_columns_defined(self):
        """Test that required columns are properly defined"""
        assert 'Name' in ColumnMapper.REQUIRED_COLUMNS
        assert 'Lineitem sku' in ColumnMapper.REQUIRED_COLUMNS
        assert 'Lineitem quantity' in ColumnMapper.REQUIRED_COLUMNS


class TestColumnMapperIntegration:
    """Integration tests for ColumnMapper with real scenarios"""

    def test_full_woocommerce_to_shopify_conversion(self):
        """Test full conversion from WooCommerce to Shopify format"""
        # Create WooCommerce profile
        profile = ClientProfile(
            client_id="WOO_TEST",
            client_name="WooCommerce Test",
            column_mapping={
                "Order ID": "Name",
                "Ordered at": "Created at"
            },
            platform="WooCommerce"
        )

        # Create WooCommerce export
        woo_df = pd.DataFrame({
            'Order ID': ['#1001', '#1002'],
            'Ordered at': ['2024-01-01', '2024-01-02'],
            'Lineitem sku': ['SKU001', 'SKU002'],
            'Lineitem quantity': [1, 2],
            'Lineitem name': ['Product 1', 'Product 2'],
            'Shipping Name': ['Customer 1', 'Customer 2']
        })

        # Apply mapping
        mapper = ColumnMapper(profile)
        shopify_df = mapper.apply_mapping(woo_df)

        # Verify Shopify format
        assert 'Name' in shopify_df.columns
        assert 'Created at' in shopify_df.columns
        assert 'Lineitem sku' in shopify_df.columns
        assert 'Lineitem quantity' in shopify_df.columns
        assert 'Lineitem name' in shopify_df.columns
        assert 'Shipping Name' in shopify_df.columns

        # Verify no WooCommerce columns
        assert 'Order ID' not in shopify_df.columns
        assert 'Ordered at' not in shopify_df.columns

        # Verify data integrity
        assert list(shopify_df['Name']) == ['#1001', '#1002']
        assert list(shopify_df['Lineitem sku']) == ['SKU001', 'SKU002']

    def test_shopify_export_no_mapping_needed(self):
        """Test that Shopify export works without mapping"""
        # Create Shopify profile (no mapping)
        profile = ClientProfile(
            client_id="SHOPIFY_TEST",
            client_name="Shopify Test",
            platform="Shopify"
        )

        # Create Shopify export
        shopify_df = pd.DataFrame({
            'Name': ['#1001', '#1002'],
            'Created at': ['2024-01-01', '2024-01-02'],
            'Lineitem sku': ['SKU001', 'SKU002'],
            'Lineitem quantity': [1, 2]
        })

        # Apply mapping (should be no-op)
        mapper = ColumnMapper(profile)
        result_df = mapper.apply_mapping(shopify_df)

        # Should be identical
        pd.testing.assert_frame_equal(result_df, shopify_df)
