"""Addition Manager - handles automatic product additions from ADDITION sheet"""
import pandas as pd
from typing import Dict, Optional, List


class AdditionManager:
    """Manages automatic product addition rules for companion products"""

    def __init__(self):
        """Initialize empty addition rules map"""
        self._addition_rules: Dict[str, Dict[str, any]] = {}

    def load_from_dataframe(self, df: pd.DataFrame) -> None:
        """
        Load addition rules from a DataFrame (ADDITION sheet)

        Expected columns:
        - IF_SKU: Target SKU that triggers addition
        - THEN_ADD: SKU to automatically add
        - QUANTITY: Quantity of the added product (optional, defaults to 1)

        Example:
        IF_SKU: NECTAR-30
        THEN_ADD: NECTAR-DROPPER
        QUANTITY: 1

        When NECTAR-30 is in an order, NECTAR-DROPPER will be automatically added.

        Args:
            df: DataFrame with addition rules

        Raises:
            ValueError: If required columns are missing
        """
        required_columns = ['IF_SKU', 'THEN_ADD']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        # Check if QUANTITY column exists
        has_quantity_column = 'QUANTITY' in df.columns

        # Build addition rules map
        self._addition_rules = {}
        for _, row in df.iterrows():
            # Check for NaN before converting to string
            if pd.isna(row['IF_SKU']) or pd.isna(row['THEN_ADD']):
                continue

            if_sku = str(row['IF_SKU']).strip()
            then_add = str(row['THEN_ADD']).strip()

            # Skip empty values
            if (not if_sku or not then_add or
                if_sku.lower() in ('nan', 'none', '') or
                then_add.lower() in ('nan', 'none', '')):
                continue

            # Get quantity from QUANTITY column, default to 1
            if has_quantity_column:
                try:
                    quantity = int(row['QUANTITY'])
                except (ValueError, TypeError):
                    quantity = 1
            else:
                quantity = 1

            self._addition_rules[if_sku] = {
                'add_sku': then_add,
                'quantity': quantity
            }

    def get_addition_rule(self, sku: str) -> Optional[Dict[str, any]]:
        """
        Get addition rule for a SKU

        Args:
            sku: Product SKU to check

        Returns:
            Dictionary with 'add_sku' and 'quantity', or None if no rule exists
        """
        return self._addition_rules.get(str(sku).strip())

    def has_addition_rule(self, sku: str) -> bool:
        """
        Check if SKU has an addition rule

        Args:
            sku: Product SKU to check

        Returns:
            True if SKU has addition rule, False otherwise
        """
        return str(sku).strip() in self._addition_rules

    def get_all_trigger_skus(self) -> List[str]:
        """
        Get list of all SKUs that trigger additions

        Returns:
            List of all trigger SKUs in the addition rules
        """
        return list(self._addition_rules.keys())

    def count(self) -> int:
        """
        Get number of addition rules

        Returns:
            Number of addition rules
        """
        return len(self._addition_rules)

    def clear(self) -> None:
        """Clear all addition rules"""
        self._addition_rules.clear()
