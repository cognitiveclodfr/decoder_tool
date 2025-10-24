"""File handlers for loading master files and order exports"""
import pandas as pd
from typing import Tuple, Optional


class MasterFileLoader:
    """Handles loading of master XLSX files with PRODUCTS and SETS sheets"""

    @staticmethod
    def load(file_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Load master file with PRODUCTS and SETS sheets

        Args:
            file_path: Path to XLSX file

        Returns:
            Tuple of (products_df, sets_df)

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If required sheets are missing
        """
        try:
            # Read all sheets
            excel_file = pd.ExcelFile(file_path)

            # Check for required sheets
            if 'PRODUCTS' not in excel_file.sheet_names:
                raise ValueError("Missing required sheet: PRODUCTS")
            if 'SETS' not in excel_file.sheet_names:
                raise ValueError("Missing required sheet: SETS")

            # Load sheets
            products_df = pd.read_excel(excel_file, sheet_name='PRODUCTS')
            sets_df = pd.read_excel(excel_file, sheet_name='SETS')

            return products_df, sets_df

        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except Exception as e:
            raise ValueError(f"Error loading master file: {str(e)}")


class OrdersFileLoader:
    """Handles loading of Shopify order export CSV files"""

    @staticmethod
    def load(file_path: str) -> pd.DataFrame:
        """
        Load orders from CSV file

        Args:
            file_path: Path to CSV file

        Returns:
            DataFrame with order data

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file cannot be parsed
        """
        try:
            orders_df = pd.read_csv(file_path)
            return orders_df
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except Exception as e:
            raise ValueError(f"Error loading orders file: {str(e)}")

    @staticmethod
    def save(df: pd.DataFrame, file_path: str) -> None:
        """
        Save processed orders to CSV file

        Args:
            df: DataFrame to save
            file_path: Output file path

        Raises:
            ValueError: If save fails
        """
        try:
            df.to_csv(file_path, index=False)
        except Exception as e:
            raise ValueError(f"Error saving file: {str(e)}")
