"""Order Processor - handles order processing and set decoding logic"""
import pandas as pd
from typing import List, Dict, Tuple
from .product_manager import ProductManager
from .set_manager import SetManager
from ..utils.sku_generator import generate_sku_from_name, is_empty_sku


class OrderProcessor:
    """Processes orders and decodes sets into individual components"""

    def __init__(self, product_manager: ProductManager, set_manager: SetManager):
        """
        Initialize order processor

        Args:
            product_manager: ProductManager instance with loaded product data
            set_manager: SetManager instance with loaded set data
        """
        self.product_manager = product_manager
        self.set_manager = set_manager
        self._orders_df: pd.DataFrame = None

    def load_orders(self, df: pd.DataFrame) -> None:
        """
        Load orders from a DataFrame

        Args:
            df: DataFrame with order data from Shopify export
        """
        self._orders_df = df.copy()

    def generate_missing_skus(self) -> Tuple[int, List[Dict[str, str]]]:
        """
        Generate SKUs for products that have empty SKU field

        Generates SKU from product name by converting to uppercase
        and replacing spaces with underscores.

        Returns:
            Tuple of (count_generated, list of changes)
            where changes = [{'name': str, 'old_sku': str, 'new_sku': str}, ...]
        """
        if self._orders_df is None:
            return 0, []

        changes = []
        count = 0

        for idx, row in self._orders_df.iterrows():
            sku = row.get('Lineitem sku', '')
            name = row.get('Lineitem name', '')

            if is_empty_sku(sku) and name:
                # Generate new SKU from product name
                new_sku = generate_sku_from_name(name)

                # Track the change
                changes.append({
                    'name': str(name),
                    'old_sku': str(sku) if not is_empty_sku(sku) else '(empty)',
                    'new_sku': new_sku
                })

                # Update the dataframe
                self._orders_df.at[idx, 'Lineitem sku'] = new_sku
                count += 1

        return count, changes

    def add_manual_product(self, order_id: str, sku: str, quantity: int) -> tuple[bool, str]:
        """
        Manually add a product to an existing order

        Args:
            order_id: Order ID (e.g., '#76360')
            sku: Product SKU to add
            quantity: Quantity to add

        Returns:
            Tuple of (success: bool, message: str)
        """
        if self._orders_df is None:
            return False, "Error: No orders loaded"

        # Find first matching order row
        matching_rows = self._orders_df[self._orders_df['Name'] == order_id]

        if matching_rows.empty:
            return False, f"Error: Order ID {order_id} not found"

        # Get first matching row as template
        template_row = matching_rows.iloc[0].copy()

        # Update with new product info
        template_row['Lineitem sku'] = sku
        template_row['Lineitem quantity'] = quantity

        # Get product name from product map
        product_name = self.product_manager.get_product_name(sku, fallback=sku)
        template_row['Lineitem name'] = product_name

        # Set financial values to 0 to avoid duplication
        template_row['Lineitem price'] = 0
        template_row['Lineitem discount'] = 0

        # Add new row to orders DataFrame
        # Convert to DataFrame for concatenation
        new_row_df = pd.DataFrame([template_row])
        self._orders_df = pd.concat([self._orders_df, new_row_df], ignore_index=True)

        return True, f"Added {sku} (Qty: {quantity}) to order {order_id}"

    def process_orders(self) -> pd.DataFrame:
        """
        Process orders by decoding sets into components

        Main logic:
        1. Iterate through each order line
        2. If SKU is a set:
           - Don't include the set line itself
           - Decode into component products
           - First component gets the original price
           - Other components get price = 0
        3. If SKU is not a set:
           - Include as-is

        Returns:
            Processed DataFrame with sets decoded

        Raises:
            ValueError: If orders not loaded
        """
        if self._orders_df is None:
            raise ValueError("No orders loaded. Call load_orders() first.")

        processed_rows = []

        # Iterate through each order row
        for _, order_row in self._orders_df.iterrows():
            sku = str(order_row['Lineitem sku']).strip()

            # Check if this SKU is a set
            if self.set_manager.is_set(sku):
                # This is a set - decode it
                self._decode_set(order_row, processed_rows)
            else:
                # Regular product - add as-is
                processed_rows.append(order_row.to_dict())

        # Create output DataFrame
        return pd.DataFrame(processed_rows)

    def _decode_set(self, order_row: pd.Series, processed_rows: List[Dict]) -> None:
        """
        Decode a set into its component products

        Args:
            order_row: Order row containing the set
            processed_rows: List to append decoded components to
        """
        set_sku = str(order_row['Lineitem sku']).strip()
        order_quantity = int(order_row['Lineitem quantity'])
        order_price = order_row['Lineitem price']

        # Get set components with quantities
        components = self.set_manager.get_components(set_sku)

        if not components:
            # No components found - skip this set
            return

        # Process each component
        for idx, component in enumerate(components):
            component_sku = component['sku']
            set_quantity = component['quantity']  # Quantity of this component in the set

            new_row = order_row.to_dict()

            # Get component details from product map
            product_details = self.product_manager.get_product(component_sku)

            if product_details:
                # Component found in product map
                new_row['Lineitem name'] = product_details['name']
                physical_qty = int(product_details['physical_qty'])
            else:
                # Component not in product map - use SKU as name, qty = 1
                new_row['Lineitem name'] = component_sku
                physical_qty = 1

            # Update component info
            new_row['Lineitem sku'] = component_sku
            # Final quantity = order_quantity × set_quantity × physical_qty
            new_row['Lineitem quantity'] = order_quantity * set_quantity * physical_qty

            # Price distribution: only first component gets the price
            if idx == 0:
                new_row['Lineitem price'] = order_price
            else:
                new_row['Lineitem price'] = 0

            processed_rows.append(new_row)

    def get_orders_dataframe(self) -> pd.DataFrame:
        """
        Get current orders DataFrame (with any manual additions)

        Returns:
            Current orders DataFrame or None if not loaded
        """
        return self._orders_df.copy() if self._orders_df is not None else None

    def get_order_count(self) -> int:
        """
        Get number of order rows loaded

        Returns:
            Number of rows in orders DataFrame, or 0 if not loaded
        """
        return len(self._orders_df) if self._orders_df is not None else 0

    def clear_orders(self) -> None:
        """Clear loaded orders"""
        self._orders_df = None
