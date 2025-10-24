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
        assert 'LAV-10ML' in components
        assert 'CHAM-10ML' in components
        assert 'BOX-RELAX' in components

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
        assert 'COMP-1' in components
