"""Column Mapper - handles column name mapping for different e-commerce platforms"""
import pandas as pd
from typing import Dict, List, Optional, Set
from ..models.client_profile import ClientProfile


class ColumnMapper:
    """
    Maps column names from client-specific format to standard format

    This allows the application to work with exports from different
    e-commerce platforms (Shopify, WooCommerce, etc.) that use
    different column names.
    """

    # Standard column names used by the application
    STANDARD_COLUMNS = {
        'Name',  # Order ID
        'Created at',  # Order date
        'Lineitem quantity',  # Quantity
        'Lineitem name',  # Product name
        'Lineitem sku',  # Product SKU
        'Lineitem price',  # Price
        'Lineitem discount',  # Discount
        'Shipping Name',  # Shipping name
        'Shipping Method',  # Shipping method
    }

    # Required columns that must be present (or mapped)
    REQUIRED_COLUMNS = {
        'Name',
        'Lineitem sku',
        'Lineitem quantity',
    }

    def __init__(self, profile: Optional[ClientProfile] = None):
        """
        Initialize column mapper

        Args:
            profile: ClientProfile with column mapping (optional)
        """
        self.profile = profile
        self._mapping: Dict[str, str] = {}

        if profile and profile.column_mapping:
            # Invert mapping: client column → standard column
            self._mapping = profile.column_mapping.copy()

    def apply_mapping(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply column mapping to DataFrame

        Renames columns from client format to standard format.
        Missing columns are handled gracefully.

        Args:
            df: DataFrame with client-specific column names

        Returns:
            DataFrame with standard column names

        Raises:
            ValueError: If required columns are missing after mapping
        """
        if not self._mapping:
            # No mapping needed
            return df.copy()

        # Create a copy to avoid modifying original
        result_df = df.copy()

        # Apply column renaming
        result_df.rename(columns=self._mapping, inplace=True)

        # Validate that required columns are present
        missing_required = self._get_missing_required_columns(result_df)
        if missing_required:
            raise ValueError(
                f"Missing required columns after mapping: {missing_required}\n"
                f"Original columns: {list(df.columns)}\n"
                f"Mapped columns: {list(result_df.columns)}"
            )

        # Add missing optional columns with default values
        self._add_missing_optional_columns(result_df)

        return result_df

    def _get_missing_required_columns(self, df: pd.DataFrame) -> Set[str]:
        """
        Get set of required columns that are missing

        Args:
            df: DataFrame to check

        Returns:
            Set of missing required column names
        """
        return self.REQUIRED_COLUMNS - set(df.columns)

    def _add_missing_optional_columns(self, df: pd.DataFrame) -> None:
        """
        Add missing optional columns with default values

        Modifies DataFrame in-place.

        Args:
            df: DataFrame to modify
        """
        for col in self.STANDARD_COLUMNS:
            if col not in df.columns:
                # Add missing column with empty/default values
                if col == 'Lineitem price':
                    df[col] = 0.0
                elif col == 'Lineitem discount':
                    df[col] = 0.0
                elif col == 'Lineitem quantity':
                    df[col] = 1
                else:
                    df[col] = ''

    def validate_mapping(self, columns: List[str]) -> Dict[str, List[str]]:
        """
        Validate that mapping will work for given columns

        Args:
            columns: List of column names from client export

        Returns:
            Dictionary with validation results:
            {
                'mapped': [list of columns that will be mapped],
                'unmapped': [list of columns without mapping],
                'missing_required': [list of required columns that will be missing],
                'warnings': [list of warning messages]
            }
        """
        result = {
            'mapped': [],
            'unmapped': [],
            'missing_required': [],
            'warnings': []
        }

        # Check which columns will be mapped
        for col in columns:
            if col in self._mapping:
                result['mapped'].append(f"{col} → {self._mapping[col]}")
            else:
                result['unmapped'].append(col)

        # Check for missing required columns after mapping
        columns_after_mapping = set(columns)
        for client_col, standard_col in self._mapping.items():
            if client_col in columns_after_mapping:
                columns_after_mapping.remove(client_col)
                columns_after_mapping.add(standard_col)

        missing_required = self.REQUIRED_COLUMNS - columns_after_mapping
        result['missing_required'] = list(missing_required)

        # Generate warnings
        if missing_required:
            result['warnings'].append(
                f"Missing required columns: {missing_required}. "
                f"Processing may fail."
            )

        missing_optional = self.STANDARD_COLUMNS - columns_after_mapping - self.REQUIRED_COLUMNS
        if missing_optional:
            result['warnings'].append(
                f"Missing optional columns: {missing_optional}. "
                f"These will be added with default values."
            )

        return result

    def get_mapping_summary(self) -> str:
        """
        Get human-readable summary of the mapping

        Returns:
            String describing the column mapping
        """
        if not self._mapping:
            return "No column mapping (using standard column names)"

        lines = ["Column Mapping:"]
        for client_col, standard_col in self._mapping.items():
            lines.append(f"  {client_col} → {standard_col}")

        return "\n".join(lines)

    def has_mapping(self) -> bool:
        """
        Check if mapper has any mappings defined

        Returns:
            True if mappings exist, False otherwise
        """
        return bool(self._mapping)

    def get_standard_column(self, client_column: str) -> str:
        """
        Get standard column name for a client column

        Args:
            client_column: Column name from client's export

        Returns:
            Standard column name (or original if no mapping)
        """
        return self._mapping.get(client_column, client_column)

    def get_client_column(self, standard_column: str) -> Optional[str]:
        """
        Get client column name for a standard column (reverse mapping)

        Args:
            standard_column: Standard column name

        Returns:
            Client column name or None if not found
        """
        for client_col, std_col in self._mapping.items():
            if std_col == standard_column:
                return client_col
        return None


def create_mapper_from_profile(profile: ClientProfile) -> ColumnMapper:
    """
    Create a ColumnMapper from a ClientProfile

    Args:
        profile: ClientProfile with column mapping

    Returns:
        ColumnMapper instance
    """
    return ColumnMapper(profile)


def detect_platform(columns: List[str]) -> str:
    """
    Attempt to detect the e-commerce platform from column names

    Args:
        columns: List of column names from export

    Returns:
        Platform name ('Shopify', 'WooCommerce', 'Unknown')
    """
    columns_set = set(columns)

    # Shopify indicators
    shopify_indicators = {'Name', 'Created at', 'Lineitem sku'}
    if shopify_indicators.issubset(columns_set):
        return 'Shopify'

    # WooCommerce indicators
    woocommerce_indicators = {'Order ID', 'Ordered at'}
    if woocommerce_indicators.issubset(columns_set):
        return 'WooCommerce'

    return 'Unknown'
