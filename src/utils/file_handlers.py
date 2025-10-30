"""File handlers for loading master files and order exports"""
import pandas as pd
from pathlib import Path
from typing import Tuple, Optional, List
from .column_mapper import ColumnMapper


class MasterFileLoader:
    """Handles loading of master XLSX files with PRODUCTS, SETS, and optionally ADDITION sheets"""

    @staticmethod
    def load(file_path: str) -> Tuple[pd.DataFrame, pd.DataFrame, Optional[pd.DataFrame]]:
        """
        Load master file with PRODUCTS, SETS, and optionally ADDITION sheets

        Args:
            file_path: Path to XLSX file

        Returns:
            Tuple of (products_df, sets_df, additions_df)
            additions_df will be None if ADDITION sheet doesn't exist

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

            # Load required sheets
            products_df = pd.read_excel(excel_file, sheet_name='PRODUCTS')
            sets_df = pd.read_excel(excel_file, sheet_name='SETS')

            # Load optional ADDITION sheet
            additions_df = None
            if 'ADDITION' in excel_file.sheet_names:
                additions_df = pd.read_excel(excel_file, sheet_name='ADDITION')

            return products_df, sets_df, additions_df

        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except Exception as e:
            raise ValueError(f"Error loading master file: {str(e)}")


class OrdersFileLoader:
    """Handles loading of order export CSV files with optional column mapping"""

    @staticmethod
    def load(file_path: str, column_mapper: Optional[ColumnMapper] = None) -> pd.DataFrame:
        """
        Load orders from CSV file with optional column mapping

        Args:
            file_path: Path to CSV file
            column_mapper: Optional ColumnMapper for transforming column names

        Returns:
            DataFrame with order data (columns mapped to standard names if mapper provided)

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file cannot be parsed or mapping fails
        """
        try:
            orders_df = pd.read_csv(file_path)

            # Apply column mapping if provided
            if column_mapper and column_mapper.has_mapping():
                orders_df = column_mapper.apply_mapping(orders_df)

            return orders_df
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except Exception as e:
            raise ValueError(f"Error loading orders file: {str(e)}")

    @staticmethod
    def load_multiple(file_paths: List[str], column_mapper: Optional[ColumnMapper] = None) -> pd.DataFrame:
        """
        Load and combine multiple CSV files into single DataFrame with optional column mapping

        Args:
            file_paths: List of paths to CSV files
            column_mapper: Optional ColumnMapper for transforming column names

        Returns:
            Combined DataFrame with all order data (columns mapped if mapper provided)

        Raises:
            FileNotFoundError: If any file doesn't exist
            ValueError: If files cannot be parsed or combined
        """
        if not file_paths:
            raise ValueError("No files provided")

        dataframes = []

        for file_path in file_paths:
            try:
                df = pd.read_csv(file_path)

                # Apply column mapping if provided
                if column_mapper and column_mapper.has_mapping():
                    df = column_mapper.apply_mapping(df)

                dataframes.append(df)
            except FileNotFoundError:
                raise FileNotFoundError(f"File not found: {file_path}")
            except Exception as e:
                raise ValueError(f"Error loading {file_path}: {str(e)}")

        # Combine all dataframes
        try:
            combined_df = pd.concat(dataframes, ignore_index=True)
            return combined_df
        except Exception as e:
            raise ValueError(f"Error combining CSV files: {str(e)}")

    @staticmethod
    def load_from_folder(folder_path: str, column_mapper: Optional[ColumnMapper] = None) -> Tuple[pd.DataFrame, List[str]]:
        """
        Load all CSV files from a folder with optional column mapping

        Args:
            folder_path: Path to folder containing CSV files
            column_mapper: Optional ColumnMapper for transforming column names

        Returns:
            Tuple of (combined DataFrame, list of loaded file names)

        Raises:
            FileNotFoundError: If folder doesn't exist
            ValueError: If no CSV files found or loading fails
        """
        folder = Path(folder_path)

        if not folder.exists():
            raise FileNotFoundError(f"Folder not found: {folder_path}")

        if not folder.is_dir():
            raise ValueError(f"Path is not a folder: {folder_path}")

        # Find all CSV files
        csv_files = list(folder.glob('*.csv'))

        if not csv_files:
            raise ValueError(f"No CSV files found in folder: {folder_path}")

        # Sort files by name for consistent ordering
        csv_files.sort()

        file_paths = [str(f) for f in csv_files]
        file_names = [f.name for f in csv_files]

        # Load and combine with column mapping
        combined_df = OrdersFileLoader.load_multiple(file_paths, column_mapper)

        return combined_df, file_names

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
