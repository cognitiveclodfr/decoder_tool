"""Product Manager - handles product map from PRODUCTS sheet"""
import pandas as pd
from typing import Dict, Optional


class ProductManager:
    """Manages product data and provides product information lookup"""

    def __init__(self):
        """Initialize empty product map"""
        self._product_map: Dict[str, Dict[str, any]] = {}

    def load_from_dataframe(self, df: pd.DataFrame) -> None:
        """
        Load products from a DataFrame (PRODUCTS sheet)

        Expected columns:
        - Products_Name: Product name
        - SKU: Product SKU (unique identifier)
        - Quantity_Product: Physical quantity in product

        Args:
            df: DataFrame with product data

        Raises:
            ValueError: If required columns are missing
        """
        required_columns = ['Products_Name', 'SKU', 'Quantity_Product']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        # Handle duplicates by keeping first occurrence
        df_clean = df.drop_duplicates(subset=['SKU'], keep='first')

        # Build product map
        self._product_map = {}
        for _, row in df_clean.iterrows():
            sku = str(row['SKU']).strip()
            self._product_map[sku] = {
                'name': str(row['Products_Name']),
                'physical_qty': int(row['Quantity_Product'])
            }

    def get_product(self, sku: str) -> Optional[Dict[str, any]]:
        """
        Get product details by SKU

        Args:
            sku: Product SKU

        Returns:
            Dictionary with 'name' and 'physical_qty', or None if not found
        """
        return self._product_map.get(str(sku).strip())

    def get_product_name(self, sku: str, fallback: Optional[str] = None) -> str:
        """
        Get product name by SKU with fallback

        Args:
            sku: Product SKU
            fallback: Fallback value if product not found (defaults to SKU itself)

        Returns:
            Product name or fallback value
        """
        product = self.get_product(sku)
        if product:
            return product['name']
        return fallback if fallback is not None else sku

    def get_product_quantity(self, sku: str, fallback: int = 1) -> int:
        """
        Get physical quantity for a product

        Args:
            sku: Product SKU
            fallback: Fallback value if product not found (defaults to 1)

        Returns:
            Physical quantity or fallback value
        """
        product = self.get_product(sku)
        if product:
            return product['physical_qty']
        return fallback

    def has_product(self, sku: str) -> bool:
        """
        Check if product exists in the map

        Args:
            sku: Product SKU

        Returns:
            True if product exists, False otherwise
        """
        return str(sku).strip() in self._product_map

    def get_all_skus(self) -> list:
        """
        Get list of all product SKUs

        Returns:
            List of all SKUs in the product map
        """
        return list(self._product_map.keys())

    def count(self) -> int:
        """
        Get number of products in the map

        Returns:
            Number of products
        """
        return len(self._product_map)

    def clear(self) -> None:
        """Clear the product map"""
        self._product_map.clear()
