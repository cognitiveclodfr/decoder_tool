"""Script to generate demo data files for testing"""
import pandas as pd
from datetime import datetime

def create_master_file():
    """Create demo master file (HERBAR_TRUTH_FILE.xlsx) with PRODUCTS and SETS sheets"""

    # PRODUCTS sheet data
    products_data = {
        'Products_Name': [
            'Lavender Essential Oil 10ml',
            'Rose Essential Oil 10ml',
            'Chamomile Essential Oil 10ml',
            'Tea Tree Essential Oil 10ml',
            'Peppermint Essential Oil 10ml',
            'Eucalyptus Essential Oil 10ml',
            'Relaxation Set Box',
            'Energy Set Box',
            'Gift Bag Small',
            'Gift Bag Large'
        ],
        'SKU': [
            'LAV-10ML',
            'ROSE-10ML',
            'CHAM-10ML',
            'TEA-10ML',
            'PEPP-10ML',
            'EUCA-10ML',
            'BOX-RELAX',
            'BOX-ENERGY',
            'BAG-SM',
            'BAG-LG'
        ],
        'Quantity_Product': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    }

    # SETS sheet data - multiple rows for each component
    # Includes SET_QUANTITY to specify how many of each component in the set
    sets_data = {
        'SET_Name': [
            'Relaxation Bundle',
            'Relaxation Bundle',
            'Relaxation Bundle',
            'Relaxation Bundle',
            'Energy Bundle',
            'Energy Bundle',
            'Energy Bundle',
            'Energy Bundle',
            'Complete Wellness Pack',
            'Complete Wellness Pack',
            'Complete Wellness Pack',
            'Complete Wellness Pack',
            'Complete Wellness Pack',
            'Complete Wellness Pack',
            'Complete Wellness Pack'
        ],
        'SET_SKU': [
            'SET-RELAX',
            'SET-RELAX',
            'SET-RELAX',
            'SET-RELAX',
            'SET-ENERGY',
            'SET-ENERGY',
            'SET-ENERGY',
            'SET-ENERGY',
            'SET-WELLNESS',
            'SET-WELLNESS',
            'SET-WELLNESS',
            'SET-WELLNESS',
            'SET-WELLNESS',
            'SET-WELLNESS',
            'SET-WELLNESS'
        ],
        'SKUs_in_SET': [
            'LAV-10ML',
            'CHAM-10ML',
            'BOX-RELAX',
            'BAG-SM',
            'PEPP-10ML',
            'EUCA-10ML',
            'BOX-ENERGY',
            'BAG-SM',
            'LAV-10ML',
            'ROSE-10ML',
            'CHAM-10ML',
            'TEA-10ML',
            'PEPP-10ML',
            'EUCA-10ML',
            'BAG-LG'
        ],
        'SET_QUANTITY': [
            1,  # Relaxation: 1x Lavender
            1,  # Relaxation: 1x Chamomile
            1,  # Relaxation: 1x Box
            1,  # Relaxation: 1x Small bag
            1,  # Energy: 1x Peppermint
            1,  # Energy: 1x Eucalyptus
            1,  # Energy: 1x Box
            1,  # Energy: 1x Small bag
            2,  # Wellness: 2x Lavender (example of quantity > 1)
            1,  # Wellness: 1x Rose
            1,  # Wellness: 1x Chamomile
            1,  # Wellness: 1x Tea Tree
            1,  # Wellness: 1x Peppermint
            1,  # Wellness: 1x Eucalyptus
            1   # Wellness: 1x Large bag
        ]
    }

    # Create DataFrames
    products_df = pd.DataFrame(products_data)
    sets_df = pd.DataFrame(sets_data)

    # Save to Excel with multiple sheets
    output_path = 'demo_data/HERBAR_TRUTH_FILE.xlsx'
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        products_df.to_excel(writer, sheet_name='PRODUCTS', index=False)
        sets_df.to_excel(writer, sheet_name='SETS', index=False)

    print(f"✓ Created master file: {output_path}")
    print(f"  - PRODUCTS sheet: {len(products_df)} products")
    print(f"  - SETS sheet: {len(sets_df)} set components (3 sets total)")
    print(f"  - SET_QUANTITY column included for component quantities in sets")


def create_orders_export():
    """Create demo Shopify orders export CSV file"""

    # Shopify order export format
    orders_data = {
        'Name': [
            '#76360', '#76360', '#76360',
            '#76361', '#76361',
            '#76362',
            '#76363', '#76363', '#76363',
            '#76364'
        ],
        'Email': [
            'customer1@example.com', 'customer1@example.com', 'customer1@example.com',
            'customer2@example.com', 'customer2@example.com',
            'customer3@example.com',
            'customer4@example.com', 'customer4@example.com', 'customer4@example.com',
            'customer5@example.com'
        ],
        'Financial Status': [
            'paid', 'paid', 'paid',
            'paid', 'paid',
            'paid',
            'paid', 'paid', 'paid',
            'pending'
        ],
        'Paid at': [
            '2024-10-20 10:30:00', '2024-10-20 10:30:00', '2024-10-20 10:30:00',
            '2024-10-21 14:15:00', '2024-10-21 14:15:00',
            '2024-10-22 09:45:00',
            '2024-10-23 16:20:00', '2024-10-23 16:20:00', '2024-10-23 16:20:00',
            ''
        ],
        'Fulfillment Status': [
            'unfulfilled', 'unfulfilled', 'unfulfilled',
            'unfulfilled', 'unfulfilled',
            'fulfilled',
            'unfulfilled', 'unfulfilled', 'unfulfilled',
            'unfulfilled'
        ],
        'Lineitem quantity': [2, 1, 1, 1, 2, 1, 1, 3, 1, 2],
        'Lineitem name': [
            'Relaxation Bundle',
            'Lavender Essential Oil 10ml',
            'Rose Essential Oil 10ml',
            'Energy Bundle',
            'Tea Tree Essential Oil 10ml',
            'Complete Wellness Pack',
            'Relaxation Bundle',
            'Peppermint Essential Oil 10ml',
            'Eucalyptus Essential Oil 10ml',
            'Lavender Essential Oil 10ml'
        ],
        'Lineitem sku': [
            'SET-RELAX',
            'LAV-10ML',
            'ROSE-10ML',
            'SET-ENERGY',
            'TEA-10ML',
            'SET-WELLNESS',
            'SET-RELAX',
            'PEPP-10ML',
            'EUCA-10ML',
            'LAV-10ML'
        ],
        'Lineitem price': [
            49.99, 12.99, 15.99,
            45.00, 10.99,
            89.99,
            49.99, 11.99,
            11.99,
            12.99
        ],
        'Lineitem discount': [
            0, 0, 0,
            5.00, 0,
            10.00,
            0, 0,
            0,
            0
        ],
        'Shipping Name': [
            'John Doe', 'John Doe', 'John Doe',
            'Jane Smith', 'Jane Smith',
            'Bob Johnson',
            'Alice Brown', 'Alice Brown', 'Alice Brown',
            'Charlie Wilson'
        ],
        'Shipping Street': [
            '123 Main St', '123 Main St', '123 Main St',
            '456 Oak Ave', '456 Oak Ave',
            '789 Pine Rd',
            '321 Elm St', '321 Elm St', '321 Elm St',
            '654 Maple Dr'
        ],
        'Shipping City': [
            'New York', 'New York', 'New York',
            'Los Angeles', 'Los Angeles',
            'Chicago',
            'Houston', 'Houston', 'Houston',
            'Phoenix'
        ],
        'Shipping Zip': [
            '10001', '10001', '10001',
            '90001', '90001',
            '60601',
            '77001', '77001', '77001',
            '85001'
        ],
        'Shipping Province': [
            'NY', 'NY', 'NY',
            'CA', 'CA',
            'IL',
            'TX', 'TX', 'TX',
            'AZ'
        ],
        'Shipping Country': [
            'United States', 'United States', 'United States',
            'United States', 'United States',
            'United States',
            'United States', 'United States', 'United States',
            'United States'
        ]
    }

    # Create DataFrame
    orders_df = pd.DataFrame(orders_data)

    # Save to CSV
    output_path = 'demo_data/orders_export.csv'
    orders_df.to_csv(output_path, index=False)

    print(f"\n✓ Created orders export: {output_path}")
    print(f"  - Total rows: {len(orders_df)}")
    print(f"  - Unique orders: {orders_df['Name'].nunique()}")
    print(f"  - Orders with sets: #76360, #76361, #76362, #76363")


if __name__ == '__main__':
    print("Creating demo data files...\n")
    create_master_file()
    create_orders_export()
    print("\n✓ All demo files created successfully!")
