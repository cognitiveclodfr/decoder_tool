"""Set Manager - handles set map from SETS sheet"""
import pandas as pd
from typing import Dict, List, Optional


class SetManager:
    """Manages set (bundle) data and provides set component lookup"""

    def __init__(self):
        """Initialize empty set map"""
        self._set_map: Dict[str, List[str]] = {}

    def load_from_dataframe(self, df: pd.DataFrame) -> None:
        """
        Load sets from a DataFrame (SETS sheet)

        Expected columns:
        - SET_Name: Set/bundle name
        - SET_SKU: Set SKU (unique identifier)
        - SKUs_in_SET: Component SKU (one per row)

        Multiple rows with the same SET_SKU represent different components of the set.

        Args:
            df: DataFrame with set data

        Raises:
            ValueError: If required columns are missing
        """
        required_columns = ['SET_Name', 'SET_SKU', 'SKUs_in_SET']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        # Group by SET_SKU to collect all components
        self._set_map = {}
        grouped = df.groupby('SET_SKU')

        for set_sku, group in grouped:
            # Collect all component SKUs for this set
            component_skus = []
            for _, row in group.iterrows():
                component_sku = str(row['SKUs_in_SET']).strip()
                if component_sku:  # Skip empty values
                    component_skus.append(component_sku)

            if component_skus:  # Only add if there are components
                self._set_map[str(set_sku).strip()] = component_skus

    def get_components(self, set_sku: str) -> Optional[List[str]]:
        """
        Get list of component SKUs for a set

        Args:
            set_sku: Set SKU

        Returns:
            List of component SKUs, or None if set not found
        """
        return self._set_map.get(str(set_sku).strip())

    def is_set(self, sku: str) -> bool:
        """
        Check if a SKU represents a set/bundle

        Args:
            sku: SKU to check

        Returns:
            True if SKU is a set, False otherwise
        """
        return str(sku).strip() in self._set_map

    def get_all_set_skus(self) -> list:
        """
        Get list of all set SKUs

        Returns:
            List of all set SKUs
        """
        return list(self._set_map.keys())

    def count(self) -> int:
        """
        Get number of sets in the map

        Returns:
            Number of sets
        """
        return len(self._set_map)

    def get_component_count(self, set_sku: str) -> int:
        """
        Get number of components in a set

        Args:
            set_sku: Set SKU

        Returns:
            Number of components, or 0 if set not found
        """
        components = self.get_components(set_sku)
        return len(components) if components else 0

    def clear(self) -> None:
        """Clear the set map"""
        self._set_map.clear()
