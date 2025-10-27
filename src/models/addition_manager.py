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
        - TYPE: Addition type - "FIXED" or "MATCHED" (optional, defaults to "FIXED")
          - FIXED: Add fixed quantity specified in QUANTITY column
          - MATCHED: Add quantity matching the trigger product quantity
        - QUANTITY: Quantity of the added product (optional, defaults to 1, ignored for MATCHED type)

        Examples:
        1. FIXED type (default):
           IF_SKU: PRODUCT-A, THEN_ADD: ACCESSORY-B, TYPE: FIXED, QUANTITY: 1
           → Always add 1 × ACCESSORY-B when PRODUCT-A is in order

        2. MATCHED type:
           IF_SKU: NECTAR-30, THEN_ADD: NECTAR-DROPPER, TYPE: MATCHED
           → Add 3 × NECTAR-DROPPER when order has 3 × NECTAR-30
           → Add 5 × NECTAR-DROPPER when order has 5 × NECTAR-30

        Args:
            df: DataFrame with addition rules

        Raises:
            ValueError: If required columns are missing
        """
        required_columns = ['IF_SKU', 'THEN_ADD']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        # Check for optional columns
        has_quantity_column = 'QUANTITY' in df.columns
        has_type_column = 'TYPE' in df.columns

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

            # Get type from TYPE column, default to FIXED
            rule_type = 'FIXED'
            if has_type_column and not pd.isna(row['TYPE']):
                rule_type = str(row['TYPE']).strip().upper()
                # Validate type
                if rule_type not in ('FIXED', 'MATCHED'):
                    rule_type = 'FIXED'  # Default to FIXED for invalid values

            # Get quantity from QUANTITY column, default to 1
            # Note: For MATCHED type, quantity is ignored
            if has_quantity_column:
                try:
                    quantity = int(row['QUANTITY'])
                except (ValueError, TypeError):
                    quantity = 1
            else:
                quantity = 1

            self._addition_rules[if_sku] = {
                'add_sku': then_add,
                'quantity': quantity,
                'type': rule_type
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
