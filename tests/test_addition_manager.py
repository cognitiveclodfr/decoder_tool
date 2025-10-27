"""Tests for AdditionManager - automatic product additions"""
import pytest
import pandas as pd
from src.models.addition_manager import AdditionManager


class TestAdditionManager:
    """Tests for AdditionManager class"""

    def test_initialization(self):
        """Test that AdditionManager initializes with empty rules"""
        manager = AdditionManager()
        assert manager.count() == 0
        assert len(manager.get_all_trigger_skus()) == 0

    def test_load_from_dataframe(self):
        """Test loading addition rules from DataFrame"""
        manager = AdditionManager()

        df = pd.DataFrame({
            'IF_SKU': ['NECTAR-30', 'PRODUCT-A'],
            'THEN_ADD': ['NECTAR-DROPPER', 'PRODUCT-B'],
            'QUANTITY': [1, 2]
        })

        manager.load_from_dataframe(df)

        assert manager.count() == 2
        assert manager.has_addition_rule('NECTAR-30')
        assert manager.has_addition_rule('PRODUCT-A')

    def test_load_missing_columns(self):
        """Test that loading fails with missing columns"""
        manager = AdditionManager()

        df = pd.DataFrame({
            'IF_SKU': ['PRODUCT-A'],
            'QUANTITY': [1]
            # Missing THEN_ADD column
        })

        with pytest.raises(ValueError, match="Missing required columns"):
            manager.load_from_dataframe(df)

    def test_get_addition_rule(self):
        """Test getting addition rule for a SKU"""
        manager = AdditionManager()

        df = pd.DataFrame({
            'IF_SKU': ['NECTAR-30'],
            'THEN_ADD': ['NECTAR-DROPPER'],
            'QUANTITY': [1]
        })
        manager.load_from_dataframe(df)

        rule = manager.get_addition_rule('NECTAR-30')
        assert rule is not None
        assert rule['add_sku'] == 'NECTAR-DROPPER'
        assert rule['quantity'] == 1

    def test_get_addition_rule_not_found(self):
        """Test getting rule for SKU that doesn't have one"""
        manager = AdditionManager()

        df = pd.DataFrame({
            'IF_SKU': ['NECTAR-30'],
            'THEN_ADD': ['NECTAR-DROPPER'],
            'QUANTITY': [1]
        })
        manager.load_from_dataframe(df)

        rule = manager.get_addition_rule('NONEXISTENT')
        assert rule is None

    def test_has_addition_rule(self):
        """Test checking if SKU has addition rule"""
        manager = AdditionManager()

        df = pd.DataFrame({
            'IF_SKU': ['NECTAR-30', 'PRODUCT-A'],
            'THEN_ADD': ['NECTAR-DROPPER', 'PRODUCT-B'],
            'QUANTITY': [1, 2]
        })
        manager.load_from_dataframe(df)

        assert manager.has_addition_rule('NECTAR-30') is True
        assert manager.has_addition_rule('PRODUCT-A') is True
        assert manager.has_addition_rule('NONEXISTENT') is False

    def test_quantity_defaults_to_one(self):
        """Test that quantity defaults to 1 if not specified"""
        manager = AdditionManager()

        df = pd.DataFrame({
            'IF_SKU': ['PRODUCT-A'],
            'THEN_ADD': ['PRODUCT-B']
            # No QUANTITY column
        })
        manager.load_from_dataframe(df)

        rule = manager.get_addition_rule('PRODUCT-A')
        assert rule['quantity'] == 1

    def test_quantity_invalid_values(self):
        """Test that invalid quantity values default to 1"""
        manager = AdditionManager()

        df = pd.DataFrame({
            'IF_SKU': ['PRODUCT-A', 'PRODUCT-B', 'PRODUCT-C'],
            'THEN_ADD': ['PRODUCT-X', 'PRODUCT-Y', 'PRODUCT-Z'],
            'QUANTITY': ['invalid', None, '']
        })
        manager.load_from_dataframe(df)

        # All invalid quantities should default to 1
        assert manager.get_addition_rule('PRODUCT-A')['quantity'] == 1
        assert manager.get_addition_rule('PRODUCT-B')['quantity'] == 1
        assert manager.get_addition_rule('PRODUCT-C')['quantity'] == 1

    def test_empty_skus_ignored(self):
        """Test that rows with empty SKUs are ignored"""
        manager = AdditionManager()

        df = pd.DataFrame({
            'IF_SKU': ['PRODUCT-A', '', None, 'nan'],
            'THEN_ADD': ['PRODUCT-B', 'PRODUCT-C', 'PRODUCT-D', 'PRODUCT-E'],
            'QUANTITY': [1, 1, 1, 1]
        })
        manager.load_from_dataframe(df)

        # Only PRODUCT-A should be loaded
        assert manager.count() == 1
        assert manager.has_addition_rule('PRODUCT-A')

    def test_empty_additions_ignored(self):
        """Test that rows with empty additions are ignored"""
        manager = AdditionManager()

        df = pd.DataFrame({
            'IF_SKU': ['PRODUCT-A', 'PRODUCT-B', 'PRODUCT-C'],
            'THEN_ADD': ['', None, 'PRODUCT-Z'],
            'QUANTITY': [1, 1, 1]
        })
        manager.load_from_dataframe(df)

        # Only PRODUCT-C should have a rule
        assert manager.count() == 1
        assert manager.has_addition_rule('PRODUCT-C')

    def test_get_all_trigger_skus(self):
        """Test getting all trigger SKUs"""
        manager = AdditionManager()

        df = pd.DataFrame({
            'IF_SKU': ['NECTAR-30', 'PRODUCT-A', 'PRODUCT-B'],
            'THEN_ADD': ['NECTAR-DROPPER', 'PRODUCT-X', 'PRODUCT-Y'],
            'QUANTITY': [1, 2, 3]
        })
        manager.load_from_dataframe(df)

        trigger_skus = manager.get_all_trigger_skus()
        assert len(trigger_skus) == 3
        assert 'NECTAR-30' in trigger_skus
        assert 'PRODUCT-A' in trigger_skus
        assert 'PRODUCT-B' in trigger_skus

    def test_clear(self):
        """Test clearing all addition rules"""
        manager = AdditionManager()

        df = pd.DataFrame({
            'IF_SKU': ['NECTAR-30'],
            'THEN_ADD': ['NECTAR-DROPPER'],
            'QUANTITY': [1]
        })
        manager.load_from_dataframe(df)

        assert manager.count() == 1

        manager.clear()

        assert manager.count() == 0
        assert not manager.has_addition_rule('NECTAR-30')

    def test_duplicate_trigger_sku(self):
        """Test that duplicate trigger SKUs keep last rule"""
        manager = AdditionManager()

        df = pd.DataFrame({
            'IF_SKU': ['PRODUCT-A', 'PRODUCT-A'],
            'THEN_ADD': ['PRODUCT-B', 'PRODUCT-C'],  # Second one should win
            'QUANTITY': [1, 2]
        })
        manager.load_from_dataframe(df)

        # Should only have 1 rule, with the last value
        assert manager.count() == 1
        rule = manager.get_addition_rule('PRODUCT-A')
        assert rule['add_sku'] == 'PRODUCT-C'
        assert rule['quantity'] == 2

    def test_whitespace_handling(self):
        """Test that whitespace is properly stripped from SKUs"""
        manager = AdditionManager()

        df = pd.DataFrame({
            'IF_SKU': ['  PRODUCT-A  ', '\tPRODUCT-B\n'],
            'THEN_ADD': ['  PRODUCT-X  ', '\tPRODUCT-Y\n'],
            'QUANTITY': [1, 2]
        })
        manager.load_from_dataframe(df)

        # Should be accessible without whitespace
        assert manager.has_addition_rule('PRODUCT-A')
        assert manager.has_addition_rule('PRODUCT-B')

        rule_a = manager.get_addition_rule('PRODUCT-A')
        assert rule_a['add_sku'] == 'PRODUCT-X'

        rule_b = manager.get_addition_rule('PRODUCT-B')
        assert rule_b['add_sku'] == 'PRODUCT-Y'

    def test_type_fixed(self):
        """Test FIXED type addition rule"""
        manager = AdditionManager()

        df = pd.DataFrame({
            'IF_SKU': ['PRODUCT-A'],
            'THEN_ADD': ['PRODUCT-B'],
            'TYPE': ['FIXED'],
            'QUANTITY': [2]
        })
        manager.load_from_dataframe(df)

        rule = manager.get_addition_rule('PRODUCT-A')
        assert rule['type'] == 'FIXED'
        assert rule['quantity'] == 2

    def test_type_matched(self):
        """Test MATCHED type addition rule"""
        manager = AdditionManager()

        df = pd.DataFrame({
            'IF_SKU': ['NECTAR-30'],
            'THEN_ADD': ['NECTAR-DROPPER'],
            'TYPE': ['MATCHED']
        })
        manager.load_from_dataframe(df)

        rule = manager.get_addition_rule('NECTAR-30')
        assert rule['type'] == 'MATCHED'
        assert rule['add_sku'] == 'NECTAR-DROPPER'

    def test_type_defaults_to_fixed(self):
        """Test that TYPE defaults to FIXED if not specified"""
        manager = AdditionManager()

        df = pd.DataFrame({
            'IF_SKU': ['PRODUCT-A'],
            'THEN_ADD': ['PRODUCT-B'],
            'QUANTITY': [1]
            # No TYPE column
        })
        manager.load_from_dataframe(df)

        rule = manager.get_addition_rule('PRODUCT-A')
        assert rule['type'] == 'FIXED'

    def test_type_invalid_defaults_to_fixed(self):
        """Test that invalid TYPE values default to FIXED"""
        manager = AdditionManager()

        df = pd.DataFrame({
            'IF_SKU': ['PRODUCT-A', 'PRODUCT-B', 'PRODUCT-C'],
            'THEN_ADD': ['PRODUCT-X', 'PRODUCT-Y', 'PRODUCT-Z'],
            'TYPE': ['INVALID', 'random', '']
        })
        manager.load_from_dataframe(df)

        # All should default to FIXED
        assert manager.get_addition_rule('PRODUCT-A')['type'] == 'FIXED'
        assert manager.get_addition_rule('PRODUCT-B')['type'] == 'FIXED'
        assert manager.get_addition_rule('PRODUCT-C')['type'] == 'FIXED'

    def test_type_case_insensitive(self):
        """Test that TYPE is case-insensitive"""
        manager = AdditionManager()

        df = pd.DataFrame({
            'IF_SKU': ['PRODUCT-A', 'PRODUCT-B', 'PRODUCT-C', 'PRODUCT-D'],
            'THEN_ADD': ['PRODUCT-W', 'PRODUCT-X', 'PRODUCT-Y', 'PRODUCT-Z'],
            'TYPE': ['fixed', 'FIXED', 'matched', 'MATCHED']
        })
        manager.load_from_dataframe(df)

        assert manager.get_addition_rule('PRODUCT-A')['type'] == 'FIXED'
        assert manager.get_addition_rule('PRODUCT-B')['type'] == 'FIXED'
        assert manager.get_addition_rule('PRODUCT-C')['type'] == 'MATCHED'
        assert manager.get_addition_rule('PRODUCT-D')['type'] == 'MATCHED'

    def test_mixed_types_in_same_file(self):
        """Test loading both FIXED and MATCHED rules in same file"""
        manager = AdditionManager()

        df = pd.DataFrame({
            'IF_SKU': ['PRODUCT-A', 'NECTAR-30', 'PRODUCT-C'],
            'THEN_ADD': ['ACCESSORY-A', 'NECTAR-DROPPER', 'ACCESSORY-C'],
            'TYPE': ['FIXED', 'MATCHED', 'FIXED'],
            'QUANTITY': [1, 1, 3]
        })
        manager.load_from_dataframe(df)

        assert manager.count() == 3
        assert manager.get_addition_rule('PRODUCT-A')['type'] == 'FIXED'
        assert manager.get_addition_rule('NECTAR-30')['type'] == 'MATCHED'
        assert manager.get_addition_rule('PRODUCT-C')['type'] == 'FIXED'
        assert manager.get_addition_rule('PRODUCT-C')['quantity'] == 3


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
