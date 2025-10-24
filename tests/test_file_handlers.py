"""Unit tests for file handlers"""
import pytest
import pandas as pd
from pathlib import Path
import tempfile
import shutil
from src.utils.file_handlers import OrdersFileLoader


class TestOrdersFileLoader:
    """Test suite for OrdersFileLoader class"""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files"""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp)

    @pytest.fixture
    def sample_csv_1(self, temp_dir):
        """Create first sample CSV file"""
        data = {
            'Name': ['#001', '#001'],
            'Email': ['test1@example.com', 'test1@example.com'],
            'Financial Status': ['paid', 'paid'],
            'Paid at': ['2024-01-01', '2024-01-01'],
            'Fulfillment Status': ['unfulfilled', 'unfulfilled'],
            'Lineitem quantity': [1, 2],
            'Lineitem name': ['Product A', 'Product B'],
            'Lineitem sku': ['SKU-A', 'SKU-B'],
            'Lineitem price': [10.00, 20.00],
            'Lineitem discount': [0, 0],
            'Shipping Name': ['John Doe', 'John Doe'],
            'Shipping Street': ['123 Main St', '123 Main St'],
            'Shipping City': ['New York', 'New York'],
            'Shipping Zip': ['10001', '10001'],
            'Shipping Province': ['NY', 'NY'],
            'Shipping Country': ['USA', 'USA']
        }
        df = pd.DataFrame(data)
        file_path = Path(temp_dir) / 'orders1.csv'
        df.to_csv(file_path, index=False)
        return str(file_path)

    @pytest.fixture
    def sample_csv_2(self, temp_dir):
        """Create second sample CSV file"""
        data = {
            'Name': ['#002'],
            'Email': ['test2@example.com'],
            'Financial Status': ['paid'],
            'Paid at': ['2024-01-02'],
            'Fulfillment Status': ['unfulfilled'],
            'Lineitem quantity': [3],
            'Lineitem name': ['Product C'],
            'Lineitem sku': ['SKU-C'],
            'Lineitem price': [30.00],
            'Lineitem discount': [5.00],
            'Shipping Name': ['Jane Smith'],
            'Shipping Street': ['456 Oak Ave'],
            'Shipping City': ['Los Angeles'],
            'Shipping Zip': ['90001'],
            'Shipping Province': ['CA'],
            'Shipping Country': ['USA']
        }
        df = pd.DataFrame(data)
        file_path = Path(temp_dir) / 'orders2.csv'
        df.to_csv(file_path, index=False)
        return str(file_path)

    @pytest.fixture
    def sample_csv_3(self, temp_dir):
        """Create third sample CSV file"""
        data = {
            'Name': ['#003', '#003'],
            'Email': ['test3@example.com', 'test3@example.com'],
            'Financial Status': ['paid', 'paid'],
            'Paid at': ['2024-01-03', '2024-01-03'],
            'Fulfillment Status': ['fulfilled', 'fulfilled'],
            'Lineitem quantity': [1, 1],
            'Lineitem name': ['Product D', 'Product E'],
            'Lineitem sku': ['SKU-D', 'SKU-E'],
            'Lineitem price': [40.00, 50.00],
            'Lineitem discount': [0, 10.00],
            'Shipping Name': ['Bob Johnson', 'Bob Johnson'],
            'Shipping Street': ['789 Pine Rd', '789 Pine Rd'],
            'Shipping City': ['Chicago', 'Chicago'],
            'Shipping Zip': ['60601', '60601'],
            'Shipping Province': ['IL', 'IL'],
            'Shipping Country': ['USA', 'USA']
        }
        df = pd.DataFrame(data)
        file_path = Path(temp_dir) / 'orders3.csv'
        df.to_csv(file_path, index=False)
        return str(file_path)

    def test_load_single_file(self, sample_csv_1):
        """Test loading a single CSV file"""
        df = OrdersFileLoader.load(sample_csv_1)

        assert len(df) == 2
        assert df['Name'].unique().tolist() == ['#001']
        assert 'SKU-A' in df['Lineitem sku'].values
        assert 'SKU-B' in df['Lineitem sku'].values

    def test_load_multiple_files(self, sample_csv_1, sample_csv_2, sample_csv_3):
        """Test loading multiple CSV files"""
        file_paths = [sample_csv_1, sample_csv_2, sample_csv_3]
        combined_df = OrdersFileLoader.load_multiple(file_paths)

        # Check total rows (2 + 1 + 2 = 5)
        assert len(combined_df) == 5

        # Check unique orders
        unique_orders = combined_df['Name'].unique().tolist()
        assert '#001' in unique_orders
        assert '#002' in unique_orders
        assert '#003' in unique_orders

        # Check all SKUs are present
        all_skus = combined_df['Lineitem sku'].values
        assert 'SKU-A' in all_skus
        assert 'SKU-B' in all_skus
        assert 'SKU-C' in all_skus
        assert 'SKU-D' in all_skus
        assert 'SKU-E' in all_skus

    def test_load_multiple_empty_list(self):
        """Test loading multiple files with empty list raises error"""
        with pytest.raises(ValueError, match="No files provided"):
            OrdersFileLoader.load_multiple([])

    def test_load_multiple_single_file(self, sample_csv_1):
        """Test load_multiple with just one file"""
        combined_df = OrdersFileLoader.load_multiple([sample_csv_1])

        assert len(combined_df) == 2
        assert combined_df['Name'].unique().tolist() == ['#001']

    def test_load_from_folder(self, temp_dir, sample_csv_1, sample_csv_2, sample_csv_3):
        """Test loading all CSV files from a folder"""
        combined_df, file_names = OrdersFileLoader.load_from_folder(temp_dir)

        # Check DataFrame
        assert len(combined_df) == 5
        assert len(combined_df['Name'].unique()) == 3

        # Check file names returned
        assert len(file_names) == 3
        assert 'orders1.csv' in file_names
        assert 'orders2.csv' in file_names
        assert 'orders3.csv' in file_names

        # Files should be sorted alphabetically
        assert file_names == sorted(file_names)

    def test_load_from_folder_empty(self, temp_dir):
        """Test loading from folder with no CSV files raises error"""
        # Create a non-CSV file
        dummy_file = Path(temp_dir) / 'not_csv.txt'
        dummy_file.write_text('This is not a CSV')

        with pytest.raises(ValueError, match="No CSV files found in folder"):
            OrdersFileLoader.load_from_folder(temp_dir)

    def test_load_from_folder_with_non_csv_files(self, temp_dir, sample_csv_1):
        """Test folder loading ignores non-CSV files"""
        # Create some non-CSV files
        (Path(temp_dir) / 'readme.txt').write_text('README')
        (Path(temp_dir) / 'data.xlsx').write_text('Excel file')

        combined_df, file_names = OrdersFileLoader.load_from_folder(temp_dir)

        # Should only load the CSV file
        assert len(combined_df) == 2
        assert len(file_names) == 1
        assert file_names[0] == 'orders1.csv'

    def test_load_multiple_preserves_column_order(self, sample_csv_1, sample_csv_2):
        """Test that column order is preserved when combining files"""
        combined_df = OrdersFileLoader.load_multiple([sample_csv_1, sample_csv_2])

        expected_columns = [
            'Name', 'Email', 'Financial Status', 'Paid at',
            'Fulfillment Status', 'Lineitem quantity', 'Lineitem name',
            'Lineitem sku', 'Lineitem price', 'Lineitem discount',
            'Shipping Name', 'Shipping Street', 'Shipping City',
            'Shipping Zip', 'Shipping Province', 'Shipping Country'
        ]

        assert list(combined_df.columns) == expected_columns

    def test_load_multiple_handles_different_row_counts(self, sample_csv_1, sample_csv_2):
        """Test combining files with different numbers of rows"""
        # sample_csv_1 has 2 rows, sample_csv_2 has 1 row
        combined_df = OrdersFileLoader.load_multiple([sample_csv_1, sample_csv_2])

        assert len(combined_df) == 3

        # Check that all data is present
        orders = combined_df['Name'].unique()
        assert '#001' in orders
        assert '#002' in orders
