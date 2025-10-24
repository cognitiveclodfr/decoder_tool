"""UI Stability Tests - Test UI components and manager API usage"""
import pytest
import pandas as pd
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.product_manager import ProductManager
from src.models.set_manager import SetManager
from src.models.order_processor import OrderProcessor


class TestProductManagerAPI:
    """Test ProductManager public API methods used by UI"""

    def test_count_method_exists(self):
        """Test that count() method exists and works"""
        manager = ProductManager()

        # Should return 0 for empty manager
        assert manager.count() == 0

        # Load some products
        df = pd.DataFrame({
            'Products_Name': ['Product A', 'Product B', 'Product C'],
            'SKU': ['SKU001', 'SKU002', 'SKU003'],
            'Quantity_Product': [1, 2, 3]
        })
        manager.load_from_dataframe(df)

        # Should return correct count
        assert manager.count() == 3

    def test_count_after_clear(self):
        """Test that count() returns 0 after clear"""
        manager = ProductManager()

        df = pd.DataFrame({
            'Products_Name': ['Product A'],
            'SKU': ['SKU001'],
            'Quantity_Product': [1]
        })
        manager.load_from_dataframe(df)
        assert manager.count() == 1

        manager.clear()
        assert manager.count() == 0

    def test_get_all_skus_method(self):
        """Test that get_all_skus() returns list of SKUs"""
        manager = ProductManager()

        df = pd.DataFrame({
            'Products_Name': ['Product A', 'Product B'],
            'SKU': ['SKU001', 'SKU002'],
            'Quantity_Product': [1, 2]
        })
        manager.load_from_dataframe(df)

        skus = manager.get_all_skus()
        assert isinstance(skus, list)
        assert len(skus) == 2
        assert 'SKU001' in skus
        assert 'SKU002' in skus

    def test_no_private_attribute_access_needed(self):
        """Test that all needed data is accessible through public methods"""
        manager = ProductManager()

        df = pd.DataFrame({
            'Products_Name': ['Product A', 'Product B', 'Product C'],
            'SKU': ['SKU001', 'SKU002', 'SKU003'],
            'Quantity_Product': [1, 2, 3]
        })
        manager.load_from_dataframe(df)

        # UI should be able to get all info without accessing _product_map
        count = manager.count()  # Get count
        skus = manager.get_all_skus()  # Get all SKUs

        # Check each product
        for sku in skus:
            assert manager.has_product(sku)
            product = manager.get_product(sku)
            assert product is not None
            assert 'name' in product
            assert 'physical_qty' in product


class TestSetManagerAPI:
    """Test SetManager public API methods used by UI"""

    def test_count_method_exists(self):
        """Test that count() method exists and works"""
        manager = SetManager()

        # Should return 0 for empty manager
        assert manager.count() == 0

        # Load some sets
        df = pd.DataFrame({
            'SET_Name': ['Set A', 'Set A', 'Set B'],
            'SET_SKU': ['SET001', 'SET001', 'SET002'],
            'SKUs_in_SET': ['SKU001', 'SKU002', 'SKU003']
        })
        manager.load_from_dataframe(df)

        # Should return correct count (2 unique sets)
        assert manager.count() == 2

    def test_count_after_clear(self):
        """Test that count() returns 0 after clear"""
        manager = SetManager()

        df = pd.DataFrame({
            'SET_Name': ['Set A'],
            'SET_SKU': ['SET001'],
            'SKUs_in_SET': ['SKU001']
        })
        manager.load_from_dataframe(df)
        assert manager.count() == 1

        manager.clear()
        assert manager.count() == 0

    def test_get_all_set_skus_method(self):
        """Test that get_all_set_skus() returns list of set SKUs"""
        manager = SetManager()

        df = pd.DataFrame({
            'SET_Name': ['Set A', 'Set A', 'Set B'],
            'SET_SKU': ['SET001', 'SET001', 'SET002'],
            'SKUs_in_SET': ['SKU001', 'SKU002', 'SKU003']
        })
        manager.load_from_dataframe(df)

        set_skus = manager.get_all_set_skus()
        assert isinstance(set_skus, list)
        assert len(set_skus) == 2
        assert 'SET001' in set_skus
        assert 'SET002' in set_skus

    def test_no_private_attribute_access_needed(self):
        """Test that all needed data is accessible through public methods"""
        manager = SetManager()

        df = pd.DataFrame({
            'SET_Name': ['Set A', 'Set A', 'Set B'],
            'SET_SKU': ['SET001', 'SET001', 'SET002'],
            'SKUs_in_SET': ['SKU001', 'SKU002', 'SKU003']
        })
        manager.load_from_dataframe(df)

        # UI should be able to get all info without accessing _set_map
        count = manager.count()  # Get count
        set_skus = manager.get_all_set_skus()  # Get all set SKUs

        # Check each set
        for set_sku in set_skus:
            assert manager.is_set(set_sku)
            components = manager.get_components(set_sku)
            assert components is not None
            assert len(components) > 0


class TestOrderProcessorAPI:
    """Test OrderProcessor public API methods used by UI"""

    def test_get_orders_dataframe_returns_none_when_empty(self):
        """Test that get_orders_dataframe() returns None when no orders loaded"""
        processor = OrderProcessor(ProductManager(), SetManager())

        # Should return None when no orders loaded
        df = processor.get_orders_dataframe()
        assert df is None

    def test_get_orders_dataframe_returns_copy_when_loaded(self):
        """Test that get_orders_dataframe() returns DataFrame after loading"""
        processor = OrderProcessor(ProductManager(), SetManager())

        orders_df = pd.DataFrame({
            'Name': ['#12345'],
            'Lineitem sku': ['SKU001'],
            'Lineitem name': ['Product A'],
            'Lineitem quantity': [1],
            'Lineitem price': [10.0]
        })
        processor.load_orders(orders_df)

        df = processor.get_orders_dataframe()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1

    def test_process_orders_returns_dataframe(self):
        """Test that process_orders() returns DataFrame"""
        product_manager = ProductManager()
        set_manager = SetManager()
        processor = OrderProcessor(product_manager, set_manager)

        # Load minimal test data
        products_df = pd.DataFrame({
            'Products_Name': ['Product A'],
            'SKU': ['SKU001'],
            'Quantity_Product': [1]
        })
        product_manager.load_from_dataframe(products_df)

        orders_df = pd.DataFrame({
            'Name': ['#12345'],
            'Lineitem sku': ['SKU001'],
            'Lineitem name': ['Product A'],
            'Lineitem quantity': [1],
            'Lineitem price': [10.0]
        })
        processor.load_orders(orders_df)

        result = processor.process_orders()
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0

    def test_generate_missing_skus_returns_correct_format(self):
        """Test that generate_missing_skus() returns (int, List[Dict])"""
        product_manager = ProductManager()
        set_manager = SetManager()
        processor = OrderProcessor(product_manager, set_manager)

        # Load orders with empty SKUs
        orders_df = pd.DataFrame({
            'Name': ['#12345', '#12346'],
            'Lineitem sku': ['', ''],
            'Lineitem name': ['Product A', 'Product B'],
            'Lineitem quantity': [1, 1],
            'Lineitem price': [10.0, 20.0]
        })
        processor.load_orders(orders_df)

        count, changes = processor.generate_missing_skus()

        # Check return format
        assert isinstance(count, int)
        assert isinstance(changes, list)
        assert count == 2

        # Check each change has correct keys
        for change in changes:
            assert isinstance(change, dict)
            assert 'name' in change
            assert 'old_sku' in change
            assert 'new_sku' in change


class TestUIIntegration:
    """Test UI-related integration scenarios"""

    def test_typical_ui_workflow(self):
        """Test a typical workflow that UI would perform"""
        # Create managers
        product_manager = ProductManager()
        set_manager = SetManager()
        order_processor = OrderProcessor(product_manager, set_manager)

        # 1. Load master file (products and sets)
        products_df = pd.DataFrame({
            'Products_Name': ['Product A', 'Product B'],
            'SKU': ['SKU001', 'SKU002'],
            'Quantity_Product': [1, 2]
        })
        product_manager.load_from_dataframe(products_df)

        sets_df = pd.DataFrame({
            'SET_Name': ['Set X'],
            'SET_SKU': ['SET001'],
            'SKUs_in_SET': ['SKU001']
        })
        set_manager.load_from_dataframe(sets_df)

        # 2. Get counts for UI display (THIS WAS THE BUG)
        product_count = product_manager.count()
        set_count = set_manager.count()

        assert product_count == 2
        assert set_count == 1

        # 3. Load orders
        orders_df = pd.DataFrame({
            'Name': ['#12345'],
            'Lineitem sku': ['SET001'],
            'Lineitem name': ['Set X'],
            'Lineitem quantity': [1],
            'Lineitem price': [100.0]
        })
        order_processor.load_orders(orders_df)

        # 4. Get order count for UI display
        order_count = len(order_processor.get_orders_dataframe())
        assert order_count == 1

        # 5. Process orders
        result_df = order_processor.process_orders()

        assert isinstance(result_df, pd.DataFrame)
        assert len(result_df) > 0

    def test_update_process_info_scenario(self):
        """Test the exact scenario from _update_process_info() method"""
        product_manager = ProductManager()
        set_manager = SetManager()
        order_processor = OrderProcessor(product_manager, set_manager)

        # Load master data
        products_df = pd.DataFrame({
            'Products_Name': ['Product A', 'Product B', 'Product C'],
            'SKU': ['SKU001', 'SKU002', 'SKU003'],
            'Quantity_Product': [1, 2, 3]
        })
        product_manager.load_from_dataframe(products_df)

        sets_df = pd.DataFrame({
            'SET_Name': ['Set X', 'Set X'],
            'SET_SKU': ['SET001', 'SET001'],
            'SKUs_in_SET': ['SKU001', 'SKU002']
        })
        set_manager.load_from_dataframe(sets_df)

        # Load orders
        orders_df = pd.DataFrame({
            'Name': ['#12345', '#12346'],
            'Lineitem sku': ['SKU001', 'SET001'],
            'Lineitem name': ['Product A', 'Set X'],
            'Lineitem quantity': [1, 1],
            'Lineitem price': [10.0, 100.0]
        })
        order_processor.load_orders(orders_df)

        # This is what _update_process_info() does (FIXED VERSION)
        product_count = product_manager.count()  # NOT len(product_manager._products)
        set_count = set_manager.count()  # NOT len(set_manager._sets)
        orders_df = order_processor.get_orders_dataframe()
        order_count = len(orders_df) if orders_df is not None else 0

        # Verify counts
        assert product_count == 3
        assert set_count == 1
        assert order_count == 2

        # Build info text like UI does
        info_text = f"Ready to process: {product_count} products, {set_count} sets, {order_count} order rows"
        assert "3 products" in info_text
        assert "1 sets" in info_text
        assert "2 order rows" in info_text

    def test_reload_master_scenario(self):
        """Test reloading master file doesn't break counts"""
        product_manager = ProductManager()
        set_manager = SetManager()

        # Initial load
        products_df = pd.DataFrame({
            'Products_Name': ['Product A'],
            'SKU': ['SKU001'],
            'Quantity_Product': [1]
        })
        product_manager.load_from_dataframe(products_df)
        assert product_manager.count() == 1

        # Reload with different data
        product_manager.clear()

        products_df2 = pd.DataFrame({
            'Products_Name': ['Product A', 'Product B', 'Product C'],
            'SKU': ['SKU001', 'SKU002', 'SKU003'],
            'Quantity_Product': [1, 2, 3]
        })
        product_manager.load_from_dataframe(products_df2)

        # Count should update correctly
        assert product_manager.count() == 3


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
