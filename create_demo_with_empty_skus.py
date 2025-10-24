"""Script to generate demo orders with empty SKUs for testing"""
import pandas as pd


def create_orders_with_empty_skus():
    """Create demo orders file with some products having empty SKUs (testers)"""

    # Shopify order export format with some empty SKUs
    orders_data = {
        'Name': [
            '#76365', '#76365', '#76365',
            '#76366', '#76366',
            '#76367',
        ],
        'Email': [
            'customer6@example.com', 'customer6@example.com', 'customer6@example.com',
            'customer7@example.com', 'customer7@example.com',
            'customer8@example.com',
        ],
        'Financial Status': [
            'paid', 'paid', 'paid',
            'paid', 'paid',
            'paid',
        ],
        'Paid at': [
            '2024-10-24 10:00:00', '2024-10-24 10:00:00', '2024-10-24 10:00:00',
            '2024-10-24 11:00:00', '2024-10-24 11:00:00',
            '2024-10-24 12:00:00',
        ],
        'Fulfillment Status': [
            'unfulfilled', 'unfulfilled', 'unfulfilled',
            'unfulfilled', 'unfulfilled',
            'unfulfilled',
        ],
        'Lineitem quantity': [1, 1, 1, 2, 1, 1],
        'Lineitem name': [
            'Lavender Essential Oil 10ml',
            'Barrier Cream Sample',  # Empty SKU
            'Face Oil Sample',       # Empty SKU
            'Relaxation Bundle',
            'Rose Essential Oil 10ml',
            'Chamomile Tester',      # Empty SKU
        ],
        'Lineitem sku': [
            'LAV-10ML',
            '',           # Empty - should generate BARRIER_CREAM_SAMPLE
            '',           # Empty - should generate FACE_OIL_SAMPLE
            'SET-RELAX',
            'ROSE-10ML',
            '',           # Empty - should generate CHAMOMILE_TESTER
        ],
        'Lineitem price': [
            12.99,
            0.00,  # Free sample
            0.00,  # Free sample
            49.99,
            15.99,
            0.00,  # Free sample
        ],
        'Lineitem discount': [0, 0, 0, 0, 0, 0],
        'Shipping Name': [
            'Emily Davis', 'Emily Davis', 'Emily Davis',
            'Michael Brown', 'Michael Brown',
            'Sarah Wilson',
        ],
        'Shipping Street': [
            '111 Test Ave', '111 Test Ave', '111 Test Ave',
            '222 Demo St', '222 Demo St',
            '333 Sample Rd',
        ],
        'Shipping City': [
            'Seattle', 'Seattle', 'Seattle',
            'Boston', 'Boston',
            'Denver',
        ],
        'Shipping Zip': [
            '98101', '98101', '98101',
            '02101', '02101',
            '80201',
        ],
        'Shipping Province': [
            'WA', 'WA', 'WA',
            'MA', 'MA',
            'CO',
        ],
        'Shipping Country': [
            'United States', 'United States', 'United States',
            'United States', 'United States',
            'United States',
        ]
    }

    # Create DataFrame
    orders_df = pd.DataFrame(orders_data)

    # Save to CSV
    output_path = 'demo_data/orders_with_empty_skus.csv'
    orders_df.to_csv(output_path, index=False)

    print(f"✓ Created orders with empty SKUs: {output_path}")
    print(f"  - Total rows: {len(orders_df)}")
    print(f"  - Products with empty SKU: 3")
    print("  - Empty SKU products:")
    print("    • Barrier Cream Sample → should generate BARRIER_CREAM_SAMPLE")
    print("    • Face Oil Sample → should generate FACE_OIL_SAMPLE")
    print("    • Chamomile Tester → should generate CHAMOMILE_TESTER")


if __name__ == '__main__':
    print("Creating demo orders file with empty SKUs...\n")
    create_orders_with_empty_skus()
    print("\n✓ Demo file created successfully!")
