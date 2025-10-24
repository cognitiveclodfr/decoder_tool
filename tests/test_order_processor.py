"""Unit tests for OrderProcessor"""
import pytest
import pandas as pd
from src.models.product_manager import ProductManager
from src.models.set_manager import SetManager
from src.models.order_processor import OrderProcessor


class TestOrderProcessor:
    """Test suite for OrderProcessor class"""

    @pytest.fixture
    def product_manager(self):
        """Create and populate ProductManager"""
        pm = ProductManager()
        products_df = pd.DataFrame({
            'Products_Name': ['Lavender Oil', 'Chamomile Oil', 'Relax Box', 'Peppermint Oil'],
            'SKU': ['LAV-10ML', 'CHAM-10ML', 'BOX-RELAX', 'PEPP-10ML'],
            'Quantity_Product': [1, 1, 1, 2]
        })
        pm.load_from_dataframe(products_df)
        return pm

    @pytest.fixture
    def set_manager(self):
        """Create and populate SetManager"""
        sm = SetManager()
        sets_df = pd.DataFrame({
            'SET_Name': ['Relaxation Bundle', 'Relaxation Bundle', 'Relaxation Bundle'],
            'SET_SKU': ['SET-RELAX', 'SET-RELAX', 'SET-RELAX'],
            'SKUs_in_SET': ['LAV-10ML', 'CHAM-10ML', 'BOX-RELAX']
        })
        sm.load_from_dataframe(sets_df)
        return sm

    @pytest.fixture
    def order_processor(self, product_manager, set_manager):
        """Create OrderProcessor with managers"""
        return OrderProcessor(product_manager, set_manager)

    @pytest.fixture
    def sample_orders_df(self):
        """Create sample orders DataFrame"""
        return pd.DataFrame({
            'Name': ['#76360', '#76360', '#76361'],
            'Email': ['test@example.com', 'test@example.com', 'test2@example.com'],
            'Lineitem quantity': [2, 1, 1],
            'Lineitem name': ['Relaxation Bundle', 'Lavender Oil', 'Peppermint Oil'],
            'Lineitem sku': ['SET-RELAX', 'LAV-10ML', 'PEPP-10ML'],
            'Lineitem price': [49.99, 12.99, 11.99],
            'Lineitem discount': [0, 0, 0]
        })

    def test_initialization(self, order_processor):
        """Test OrderProcessor initialization"""
        assert order_processor.get_order_count() == 0

    def test_load_orders(self, order_processor, sample_orders_df):
        """Test loading orders"""
        order_processor.load_orders(sample_orders_df)
        assert order_processor.get_order_count() == 3

    def test_add_manual_product_success(self, order_processor, sample_orders_df):
        """Test successful manual product addition"""
        order_processor.load_orders(sample_orders_df)

        success, message = order_processor.add_manual_product('#76360', 'CHAM-10ML', 2)

        assert success is True
        assert 'Added CHAM-10ML' in message
        assert order_processor.get_order_count() == 4  # One row added

    def test_add_manual_product_no_orders(self, order_processor):
        """Test manual addition without loaded orders"""
        success, message = order_processor.add_manual_product('#76360', 'SKU', 1)

        assert success is False
        assert 'No orders loaded' in message

    def test_add_manual_product_order_not_found(self, order_processor, sample_orders_df):
        """Test manual addition with non-existent order"""
        order_processor.load_orders(sample_orders_df)

        success, message = order_processor.add_manual_product('#99999', 'SKU', 1)

        assert success is False
        assert 'not found' in message

    def test_add_manual_product_uses_product_name(self, order_processor, sample_orders_df):
        """Test that manual addition uses product name from map"""
        order_processor.load_orders(sample_orders_df)

        order_processor.add_manual_product('#76360', 'LAV-10ML', 1)
        df = order_processor.get_orders_dataframe()

        # Find the added row
        new_row = df.iloc[-1]
        assert new_row['Lineitem sku'] == 'LAV-10ML'
        assert new_row['Lineitem name'] == 'Lavender Oil'  # From product map
        assert new_row['Lineitem price'] == 0  # Price set to 0
        assert new_row['Lineitem discount'] == 0

    def test_add_manual_product_unknown_sku_uses_sku_as_name(self, order_processor, sample_orders_df):
        """Test that unknown SKU uses SKU as product name"""
        order_processor.load_orders(sample_orders_df)

        order_processor.add_manual_product('#76360', 'UNKNOWN-SKU', 1)
        df = order_processor.get_orders_dataframe()

        new_row = df.iloc[-1]
        assert new_row['Lineitem name'] == 'UNKNOWN-SKU'  # Uses SKU as fallback

    def test_process_orders_without_loading(self, order_processor):
        """Test processing without loading orders first"""
        with pytest.raises(ValueError, match="No orders loaded"):
            order_processor.process_orders()

    def test_process_orders_regular_products(self, order_processor, sample_orders_df):
        """Test processing orders with regular products (not sets)"""
        # Load only regular products
        orders_df = sample_orders_df[sample_orders_df['Lineitem sku'] != 'SET-RELAX'].copy()
        order_processor.load_orders(orders_df)

        result_df = order_processor.process_orders()

        # Regular products should pass through unchanged
        assert len(result_df) == 2
        assert result_df.iloc[0]['Lineitem sku'] == 'LAV-10ML'
        assert result_df.iloc[1]['Lineitem sku'] == 'PEPP-10ML'

    def test_process_orders_decode_set(self, order_processor, sample_orders_df):
        """Test decoding a set into components"""
        order_processor.load_orders(sample_orders_df)

        result_df = order_processor.process_orders()

        # Expected: SET-RELAX (qty 2) -> 3 component rows (each with qty 2)
        # Plus 2 regular products = 5 total rows
        assert len(result_df) == 5

        # Find decoded set components
        set_components = result_df[result_df['Name'] == '#76360']
        # Order #76360 had: SET-RELAX (qty 2) + LAV-10ML (qty 1)
        # SET-RELAX decodes to 3 component rows + LAV-10ML = 4 rows total
        assert len(set_components) == 4

    def test_process_orders_price_distribution(self, order_processor, sample_orders_df):
        """Test that only first component gets the price"""
        # Create order with just one set
        orders_df = sample_orders_df[sample_orders_df['Lineitem sku'] == 'SET-RELAX'].iloc[:1].copy()
        order_processor.load_orders(orders_df)

        result_df = order_processor.process_orders()

        # Check price distribution
        prices = result_df['Lineitem price'].tolist()
        assert prices[0] == 49.99  # First component gets price
        assert prices[1] == 0       # Second component gets 0
        assert prices[2] == 0       # Third component gets 0

    def test_process_orders_quantity_multiplication(self, order_processor, sample_orders_df):
        """Test quantity multiplication with physical_qty"""
        # Create order with set quantity = 2
        orders_df = sample_orders_df[sample_orders_df['Lineitem sku'] == 'SET-RELAX'].iloc[:1].copy()
        order_processor.load_orders(orders_df)

        result_df = order_processor.process_orders()

        # All components have physical_qty = 1, so quantity should be 2 * 1 = 2
        assert result_df.iloc[0]['Lineitem quantity'] == 2
        assert result_df.iloc[1]['Lineitem quantity'] == 2
        assert result_df.iloc[2]['Lineitem quantity'] == 2

    def test_process_orders_component_not_in_product_map(self, order_processor):
        """Test decoding set with component not in product map"""
        # Create set with unknown component
        sm = SetManager()
        sets_df = pd.DataFrame({
            'SET_Name': ['Test Set', 'Test Set'],
            'SET_SKU': ['SET-TEST', 'SET-TEST'],
            'SKUs_in_SET': ['LAV-10ML', 'UNKNOWN-COMP']
        })
        sm.load_from_dataframe(sets_df)

        op = OrderProcessor(order_processor.product_manager, sm)

        orders_df = pd.DataFrame({
            'Name': ['#1'],
            'Lineitem quantity': [1],
            'Lineitem name': ['Test Set'],
            'Lineitem sku': ['SET-TEST'],
            'Lineitem price': [10.0],
            'Lineitem discount': [0]
        })
        op.load_orders(orders_df)

        result_df = op.process_orders()

        # Should have 2 components
        assert len(result_df) == 2

        # First component (LAV-10ML) should have name from product map
        assert result_df.iloc[0]['Lineitem name'] == 'Lavender Oil'
        assert result_df.iloc[0]['Lineitem quantity'] == 1  # physical_qty = 1

        # Second component (UNKNOWN-COMP) should use SKU as name
        assert result_df.iloc[1]['Lineitem name'] == 'UNKNOWN-COMP'
        assert result_df.iloc[1]['Lineitem quantity'] == 1  # fallback physical_qty = 1

    def test_clear_orders(self, order_processor, sample_orders_df):
        """Test clearing orders"""
        order_processor.load_orders(sample_orders_df)
        assert order_processor.get_order_count() == 3

        order_processor.clear_orders()
        assert order_processor.get_order_count() == 0

    def test_get_orders_dataframe_returns_copy(self, order_processor, sample_orders_df):
        """Test that get_orders_dataframe returns a copy"""
        order_processor.load_orders(sample_orders_df)

        df1 = order_processor.get_orders_dataframe()
        df2 = order_processor.get_orders_dataframe()

        # Modify df1
        df1.iloc[0, 0] = 'MODIFIED'

        # df2 should be unchanged
        assert df2.iloc[0, 0] != 'MODIFIED'

    def test_generate_missing_skus_basic(self, order_processor):
        """Test basic SKU generation for empty SKUs"""
        # Create orders with empty SKUs
        orders_df = pd.DataFrame({
            'Name': ['#1', '#1'],
            'Lineitem name': ['Barrier Cream Sample', 'Face Oil Sample'],
            'Lineitem sku': ['', ''],
            'Lineitem quantity': [1, 1],
            'Lineitem price': [0, 0]
        })

        order_processor.load_orders(orders_df)
        count, changes = order_processor.generate_missing_skus()

        assert count == 2
        assert len(changes) == 2

        # Check generated SKUs
        df = order_processor.get_orders_dataframe()
        assert df.iloc[0]['Lineitem sku'] == 'BARRIER_CREAM_SAMPLE'
        assert df.iloc[1]['Lineitem sku'] == 'FACE_OIL_SAMPLE'

    def test_generate_missing_skus_no_empty(self, order_processor, sample_orders_df):
        """Test SKU generation when no empty SKUs exist"""
        order_processor.load_orders(sample_orders_df)
        count, changes = order_processor.generate_missing_skus()

        assert count == 0
        assert len(changes) == 0

    def test_generate_missing_skus_mixed(self, order_processor):
        """Test SKU generation with mix of empty and filled SKUs"""
        orders_df = pd.DataFrame({
            'Name': ['#1', '#1', '#1'],
            'Lineitem name': ['Product 1', 'Tester Sample', 'Product 3'],
            'Lineitem sku': ['PROD-1', '', 'PROD-3'],
            'Lineitem quantity': [1, 1, 1],
            'Lineitem price': [10, 0, 15]
        })

        order_processor.load_orders(orders_df)
        count, changes = order_processor.generate_missing_skus()

        assert count == 1
        assert len(changes) == 1
        assert changes[0]['name'] == 'Tester Sample'
        assert changes[0]['new_sku'] == 'TESTER_SAMPLE'

        # Check that other SKUs are unchanged
        df = order_processor.get_orders_dataframe()
        assert df.iloc[0]['Lineitem sku'] == 'PROD-1'
        assert df.iloc[1]['Lineitem sku'] == 'TESTER_SAMPLE'
        assert df.iloc[2]['Lineitem sku'] == 'PROD-3'

    def test_generate_missing_skus_special_characters(self, order_processor):
        """Test SKU generation handles special characters"""
        orders_df = pd.DataFrame({
            'Name': ['#1'],
            'Lineitem name': ['Product & Sample (Test)'],
            'Lineitem sku': [''],
            'Lineitem quantity': [1],
            'Lineitem price': [0]
        })

        order_processor.load_orders(orders_df)
        count, changes = order_processor.generate_missing_skus()

        assert count == 1
        df = order_processor.get_orders_dataframe()
        # Special characters should be removed
        assert df.iloc[0]['Lineitem sku'] == 'PRODUCT_SAMPLE_TEST'

    def test_generate_missing_skus_no_orders_loaded(self, order_processor):
        """Test SKU generation when no orders are loaded"""
        count, changes = order_processor.generate_missing_skus()

        assert count == 0
        assert len(changes) == 0
