"""Unit tests for SetManager"""
import pytest
import pandas as pd
from src.models.set_manager import SetManager


class TestSetManager:
    """Test suite for SetManager class"""

    @pytest.fixture
    def sample_sets_df(self):
        """Create sample sets DataFrame"""
        return pd.DataFrame({
            'SET_Name': [
                'Relaxation Bundle', 'Relaxation Bundle', 'Relaxation Bundle',
                'Energy Bundle', 'Energy Bundle'
            ],
            'SET_SKU': [
                'SET-RELAX', 'SET-RELAX', 'SET-RELAX',
                'SET-ENERGY', 'SET-ENERGY'
            ],
            'SKUs_in_SET': [
                'LAV-10ML', 'CHAM-10ML', 'BOX-RELAX',
                'PEPP-10ML', 'EUCA-10ML'
            ]
        })

    @pytest.fixture
    def set_manager(self):
        """Create SetManager instance"""
        return SetManager()

    def test_initialization(self, set_manager):
        """Test SetManager initializes with empty map"""
        assert set_manager.count() == 0
        assert set_manager.get_all_set_skus() == []

    def test_load_from_dataframe(self, set_manager, sample_sets_df):
        """Test loading sets from DataFrame"""
        set_manager.load_from_dataframe(sample_sets_df)

        assert set_manager.count() == 2  # Two unique sets
        assert 'SET-RELAX' in set_manager.get_all_set_skus()
        assert 'SET-ENERGY' in set_manager.get_all_set_skus()

    def test_load_missing_columns(self, set_manager):
        """Test error handling for missing columns"""
        invalid_df = pd.DataFrame({'SET_SKU': ['TEST']})

        with pytest.raises(ValueError, match="Missing required columns"):
            set_manager.load_from_dataframe(invalid_df)

    def test_get_components(self, set_manager, sample_sets_df):
        """Test getting set components"""
        set_manager.load_from_dataframe(sample_sets_df)

        components = set_manager.get_components('SET-RELAX')
        assert components is not None
        assert len(components) == 3

        # Components are now dicts with 'sku' and 'quantity'
        component_skus = [comp['sku'] for comp in components]
        assert 'LAV-10ML' in component_skus
        assert 'CHAM-10ML' in component_skus
        assert 'BOX-RELAX' in component_skus

        # Check default quantity is 1
        for comp in components:
            assert comp['quantity'] == 1

    def test_get_components_not_found(self, set_manager, sample_sets_df):
        """Test getting components for non-existent set"""
        set_manager.load_from_dataframe(sample_sets_df)

        components = set_manager.get_components('NONEXISTENT')
        assert components is None

    def test_is_set(self, set_manager, sample_sets_df):
        """Test checking if SKU is a set"""
        set_manager.load_from_dataframe(sample_sets_df)

        assert set_manager.is_set('SET-RELAX') is True
        assert set_manager.is_set('SET-ENERGY') is True
        assert set_manager.is_set('LAV-10ML') is False
        assert set_manager.is_set('UNKNOWN') is False

    def test_get_component_count(self, set_manager, sample_sets_df):
        """Test getting component count"""
        set_manager.load_from_dataframe(sample_sets_df)

        count = set_manager.get_component_count('SET-RELAX')
        assert count == 3

        count = set_manager.get_component_count('SET-ENERGY')
        assert count == 2

        count = set_manager.get_component_count('UNKNOWN')
        assert count == 0

    def test_clear(self, set_manager, sample_sets_df):
        """Test clearing set map"""
        set_manager.load_from_dataframe(sample_sets_df)
        assert set_manager.count() == 2

        set_manager.clear()
        assert set_manager.count() == 0
        assert set_manager.get_all_set_skus() == []

    def test_empty_component_skus(self, set_manager):
        """Test handling of empty component SKUs"""
        df_with_empty = pd.DataFrame({
            'SET_Name': ['Test Set', 'Test Set'],
            'SET_SKU': ['SET-TEST', 'SET-TEST'],
            'SKUs_in_SET': ['COMP-1', '']  # One empty
        })

        set_manager.load_from_dataframe(df_with_empty)

        components = set_manager.get_components('SET-TEST')
        assert len(components) == 1

        # Components are now dicts with 'sku' and 'quantity'
        component_skus = [comp['sku'] for comp in components]
        assert 'COMP-1' in component_skus
        assert components[0]['quantity'] == 1

    def test_set_quantity_column(self, set_manager):
        """Test SET_QUANTITY column support"""
        df_with_quantities = pd.DataFrame({
            'SET_Name': ['Bundle A', 'Bundle A', 'Bundle A'],
            'SET_SKU': ['SET-A', 'SET-A', 'SET-A'],
            'SKUs_in_SET': ['COMP-1', 'COMP-2', 'COMP-3'],
            'SET_QUANTITY': [2, 1, 3]  # Different quantities
        })

        set_manager.load_from_dataframe(df_with_quantities)

        components = set_manager.get_components('SET-A')
        assert len(components) == 3

        # Check that quantities are correctly loaded
        assert components[0] == {'sku': 'COMP-1', 'quantity': 2}
        assert components[1] == {'sku': 'COMP-2', 'quantity': 1}
        assert components[2] == {'sku': 'COMP-3', 'quantity': 3}

    def test_set_quantity_defaults_to_one(self, set_manager):
        """Test that missing SET_QUANTITY column defaults to 1"""
        df_without_quantity = pd.DataFrame({
            'SET_Name': ['Bundle B', 'Bundle B'],
            'SET_SKU': ['SET-B', 'SET-B'],
            'SKUs_in_SET': ['COMP-X', 'COMP-Y']
            # No SET_QUANTITY column
        })

        set_manager.load_from_dataframe(df_without_quantity)

        components = set_manager.get_components('SET-B')
        assert len(components) == 2

        # Both should default to quantity 1
        assert components[0]['quantity'] == 1
        assert components[1]['quantity'] == 1

    def test_set_quantity_invalid_values(self, set_manager):
        """Test handling of invalid SET_QUANTITY values"""
        df_with_invalid = pd.DataFrame({
            'SET_Name': ['Bundle C', 'Bundle C', 'Bundle C'],
            'SET_SKU': ['SET-C', 'SET-C', 'SET-C'],
            'SKUs_in_SET': ['COMP-1', 'COMP-2', 'COMP-3'],
            'SET_QUANTITY': [2, 'invalid', None]  # Invalid values
        })

        set_manager.load_from_dataframe(df_with_invalid)

        components = set_manager.get_components('SET-C')
        assert len(components) == 3

        # Valid quantity should be preserved
        assert components[0]['quantity'] == 2
        # Invalid values should default to 1
        assert components[1]['quantity'] == 1
        assert components[2]['quantity'] == 1
