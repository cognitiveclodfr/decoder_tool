"""Integration tests for addition rules with FIXED and MATCHED types"""
import pytest
import pandas as pd
from src.models.product_manager import ProductManager
from src.models.set_manager import SetManager
from src.models.addition_manager import AdditionManager
from src.models.order_processor import OrderProcessor


class TestAdditionRulesIntegration:
    """Integration tests for addition rules functionality"""

    def test_fixed_type_addition(self):
        """Test FIXED type - adds fixed quantity regardless of order quantity"""
        # Setup managers
        product_manager = ProductManager()
        set_manager = SetManager()
        addition_manager = AdditionManager()

        # Load products
        products_df = pd.DataFrame({
            'Products_Name': ['Product A', 'Accessory B'],
            'SKU': ['PRODUCT-A', 'ACCESSORY-B'],
            'Quantity_Product': [1, 1]
        })
        product_manager.load_from_dataframe(products_df)

        # Load addition rule - FIXED type
        additions_df = pd.DataFrame({
            'IF_SKU': ['PRODUCT-A'],
            'THEN_ADD': ['ACCESSORY-B'],
            'TYPE': ['FIXED'],
            'QUANTITY': [1]
        })
        addition_manager.load_from_dataframe(additions_df)

        # Create order processor
        order_processor = OrderProcessor(product_manager, set_manager, addition_manager)

        # Load order with 5 × PRODUCT-A
        orders_df = pd.DataFrame({
            'Name': ['#12345'],
            'Lineitem sku': ['PRODUCT-A'],
            'Lineitem name': ['Product A'],
            'Lineitem quantity': [5],
            'Lineitem price': [50.0]
        })
        order_processor.load_orders(orders_df)

        # Process orders
        result = order_processor.process_orders()

        # Should have 2 rows: original + accessory
        assert len(result) == 2

        # First row: original product with quantity 5
        assert result.iloc[0]['Lineitem sku'] == 'PRODUCT-A'
        assert result.iloc[0]['Lineitem quantity'] == 5

        # Second row: accessory with FIXED quantity 1
        assert result.iloc[1]['Lineitem sku'] == 'ACCESSORY-B'
        assert result.iloc[1]['Lineitem quantity'] == 1  # Fixed at 1, not 5!
        assert result.iloc[1]['Lineitem price'] == 0

    def test_matched_type_addition(self):
        """Test MATCHED type - quantity matches trigger product quantity"""
        # Setup managers
        product_manager = ProductManager()
        set_manager = SetManager()
        addition_manager = AdditionManager()

        # Load products
        products_df = pd.DataFrame({
            'Products_Name': ['Nectar 30ml', 'Dropper'],
            'SKU': ['NECTAR-30', 'NECTAR-DROPPER'],
            'Quantity_Product': [1, 1]
        })
        product_manager.load_from_dataframe(products_df)

        # Load addition rule - MATCHED type
        additions_df = pd.DataFrame({
            'IF_SKU': ['NECTAR-30'],
            'THEN_ADD': ['NECTAR-DROPPER'],
            'TYPE': ['MATCHED']
        })
        addition_manager.load_from_dataframe(additions_df)

        # Create order processor
        order_processor = OrderProcessor(product_manager, set_manager, addition_manager)

        # Load order with 3 × NECTAR-30
        orders_df = pd.DataFrame({
            'Name': ['#10001'],
            'Lineitem sku': ['NECTAR-30'],
            'Lineitem name': ['Nectar 30ml'],
            'Lineitem quantity': [3],
            'Lineitem price': [150.0]
        })
        order_processor.load_orders(orders_df)

        # Process orders
        result = order_processor.process_orders()

        # Should have 2 rows: original + dropper
        assert len(result) == 2

        # First row: original product with quantity 3
        assert result.iloc[0]['Lineitem sku'] == 'NECTAR-30'
        assert result.iloc[0]['Lineitem quantity'] == 3

        # Second row: dropper with MATCHED quantity 3
        assert result.iloc[1]['Lineitem sku'] == 'NECTAR-DROPPER'
        assert result.iloc[1]['Lineitem quantity'] == 3  # Matched to 3!
        assert result.iloc[1]['Lineitem price'] == 0

    def test_matched_type_different_quantities(self):
        """Test MATCHED type with different order quantities"""
        # Setup managers
        product_manager = ProductManager()
        set_manager = SetManager()
        addition_manager = AdditionManager()

        # Load products
        products_df = pd.DataFrame({
            'Products_Name': ['Nectar 30ml', 'Dropper'],
            'SKU': ['NECTAR-30', 'NECTAR-DROPPER'],
            'Quantity_Product': [1, 1]
        })
        product_manager.load_from_dataframe(products_df)

        # Load addition rule - MATCHED type
        additions_df = pd.DataFrame({
            'IF_SKU': ['NECTAR-30'],
            'THEN_ADD': ['NECTAR-DROPPER'],
            'TYPE': ['MATCHED']
        })
        addition_manager.load_from_dataframe(additions_df)

        # Create order processor
        order_processor = OrderProcessor(product_manager, set_manager, addition_manager)

        # Load multiple orders with different quantities
        orders_df = pd.DataFrame({
            'Name': ['#10001', '#10002', '#10003'],
            'Lineitem sku': ['NECTAR-30', 'NECTAR-30', 'NECTAR-30'],
            'Lineitem name': ['Nectar 30ml', 'Nectar 30ml', 'Nectar 30ml'],
            'Lineitem quantity': [1, 5, 10],
            'Lineitem price': [50.0, 250.0, 500.0]
        })
        order_processor.load_orders(orders_df)

        # Process orders
        result = order_processor.process_orders()

        # Should have 6 rows: 3 originals + 3 droppers
        assert len(result) == 6

        # Check order #10001: 1 nectar → 1 dropper
        order1_rows = result[result['Name'] == '#10001']
        assert len(order1_rows) == 2
        assert order1_rows[order1_rows['Lineitem sku'] == 'NECTAR-30']['Lineitem quantity'].values[0] == 1
        assert order1_rows[order1_rows['Lineitem sku'] == 'NECTAR-DROPPER']['Lineitem quantity'].values[0] == 1

        # Check order #10002: 5 nectar → 5 droppers
        order2_rows = result[result['Name'] == '#10002']
        assert len(order2_rows) == 2
        assert order2_rows[order2_rows['Lineitem sku'] == 'NECTAR-30']['Lineitem quantity'].values[0] == 5
        assert order2_rows[order2_rows['Lineitem sku'] == 'NECTAR-DROPPER']['Lineitem quantity'].values[0] == 5

        # Check order #10003: 10 nectar → 10 droppers
        order3_rows = result[result['Name'] == '#10003']
        assert len(order3_rows) == 2
        assert order3_rows[order3_rows['Lineitem sku'] == 'NECTAR-30']['Lineitem quantity'].values[0] == 10
        assert order3_rows[order3_rows['Lineitem sku'] == 'NECTAR-DROPPER']['Lineitem quantity'].values[0] == 10

    def test_mixed_fixed_and_matched_rules(self):
        """Test combination of FIXED and MATCHED rules"""
        # Setup managers
        product_manager = ProductManager()
        set_manager = SetManager()
        addition_manager = AdditionManager()

        # Load products
        products_df = pd.DataFrame({
            'Products_Name': ['Nectar 30ml', 'Product A', 'Dropper', 'Manual'],
            'SKU': ['NECTAR-30', 'PRODUCT-A', 'NECTAR-DROPPER', 'MANUAL-PDF'],
            'Quantity_Product': [1, 1, 1, 1]
        })
        product_manager.load_from_dataframe(products_df)

        # Load addition rules - one MATCHED, one FIXED
        additions_df = pd.DataFrame({
            'IF_SKU': ['NECTAR-30', 'PRODUCT-A'],
            'THEN_ADD': ['NECTAR-DROPPER', 'MANUAL-PDF'],
            'TYPE': ['MATCHED', 'FIXED'],
            'QUANTITY': [1, 1]
        })
        addition_manager.load_from_dataframe(additions_df)

        # Create order processor
        order_processor = OrderProcessor(product_manager, set_manager, addition_manager)

        # Load order with both products
        orders_df = pd.DataFrame({
            'Name': ['#10001', '#10001'],
            'Lineitem sku': ['NECTAR-30', 'PRODUCT-A'],
            'Lineitem name': ['Nectar 30ml', 'Product A'],
            'Lineitem quantity': [3, 5],
            'Lineitem price': [150.0, 100.0]
        })
        order_processor.load_orders(orders_df)

        # Process orders
        result = order_processor.process_orders()

        # Should have 4 rows: 2 originals + 2 additions
        assert len(result) == 4

        # Check MATCHED rule: 3 × NECTAR-30 → 3 × NECTAR-DROPPER
        nectar_dropper = result[result['Lineitem sku'] == 'NECTAR-DROPPER']
        assert len(nectar_dropper) == 1
        assert nectar_dropper['Lineitem quantity'].values[0] == 3  # Matched to NECTAR-30

        # Check FIXED rule: 5 × PRODUCT-A → 1 × MANUAL-PDF
        manual = result[result['Lineitem sku'] == 'MANUAL-PDF']
        assert len(manual) == 1
        assert manual['Lineitem quantity'].values[0] == 1  # Fixed at 1, not 5

    def test_backwards_compatibility_no_type_column(self):
        """Test that rules without TYPE column default to FIXED"""
        # Setup managers
        product_manager = ProductManager()
        set_manager = SetManager()
        addition_manager = AdditionManager()

        # Load products
        products_df = pd.DataFrame({
            'Products_Name': ['Product A', 'Accessory B'],
            'SKU': ['PRODUCT-A', 'ACCESSORY-B'],
            'Quantity_Product': [1, 1]
        })
        product_manager.load_from_dataframe(products_df)

        # Load addition rule WITHOUT TYPE column (backwards compatibility)
        additions_df = pd.DataFrame({
            'IF_SKU': ['PRODUCT-A'],
            'THEN_ADD': ['ACCESSORY-B'],
            'QUANTITY': [2]
            # No TYPE column
        })
        addition_manager.load_from_dataframe(additions_df)

        # Create order processor
        order_processor = OrderProcessor(product_manager, set_manager, addition_manager)

        # Load order with 10 × PRODUCT-A
        orders_df = pd.DataFrame({
            'Name': ['#12345'],
            'Lineitem sku': ['PRODUCT-A'],
            'Lineitem name': ['Product A'],
            'Lineitem quantity': [10],
            'Lineitem price': [100.0]
        })
        order_processor.load_orders(orders_df)

        # Process orders
        result = order_processor.process_orders()

        # Should default to FIXED behavior: add fixed quantity 2
        assert len(result) == 2
        assert result.iloc[1]['Lineitem sku'] == 'ACCESSORY-B'
        assert result.iloc[1]['Lineitem quantity'] == 2  # Fixed at 2, not 10


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
