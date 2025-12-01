"""Script to create SQLite database and load Excel data.

This script creates the santander_bank.db database with customers and
transactions tables, then loads data from the corresponding Excel files.
"""

# Standard library
import sqlite3
from pathlib import Path

# Third-party
import pandas as pd


def create_database(db_path: str) -> sqlite3.Connection:
    """Create a new SQLite database connection.

    Args:
        db_path: Path where the database file should be created.

    Returns:
        SQLite connection object.
    """
    conn = sqlite3.connect(db_path)
    print(f"Created database: {db_path}")
    return conn


def create_customers_table(conn: sqlite3.Connection) -> None:
    """Create the customers table with appropriate schema.

    Args:
        conn: SQLite database connection.
    """
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id TEXT PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            date_of_birth TEXT,
            age INTEGER,
            gender TEXT,
            address TEXT,
            city TEXT,
            postcode TEXT,
            account_type TEXT,
            account_number INTEGER,
            sort_code TEXT,
            account_open_date TEXT,
            balance REAL,
            income_bracket TEXT,
            credit_score INTEGER,
            num_products INTEGER,
            customer_segment TEXT,
            is_active INTEGER,
            has_mobile_app INTEGER,
            has_online_banking INTEGER,
            marketing_consent INTEGER
        )
    """)
    conn.commit()
    print("Created customers table")


def create_transactions_table(conn: sqlite3.Connection) -> None:
    """Create the transactions table with appropriate schema.

    Args:
        conn: SQLite database connection.
    """
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            transaction_date TEXT,
            transaction_time TEXT,
            transaction_type TEXT,
            category TEXT,
            amount REAL,
            currency TEXT,
            merchant_name TEXT,
            merchant_category_code INTEGER,
            channel TEXT,
            location TEXT,
            is_international INTEGER,
            is_recurring INTEGER,
            status TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        )
    """)
    conn.commit()
    print("Created transactions table")


def load_customers_data(conn: sqlite3.Connection, excel_path: str) -> int:
    """Load customer data from Excel file into the database.

    Args:
        conn: SQLite database connection.
        excel_path: Path to the customers Excel file.

    Returns:
        Number of rows loaded.

    Raises:
        FileNotFoundError: If the Excel file doesn't exist.
    """
    if not Path(excel_path).exists():
        raise FileNotFoundError(f"Excel file not found: {excel_path}")

    df = pd.read_excel(excel_path)

    bool_columns = ["is_active", "has_mobile_app", "has_online_banking", "marketing_consent"]
    for col in bool_columns:
        if col in df.columns:
            df[col] = df[col].astype(int)

    df.to_sql("customers", conn, if_exists="replace", index=False)
    print(f"Loaded {len(df)} rows into customers table")
    return len(df)


def load_transactions_data(conn: sqlite3.Connection, excel_path: str) -> int:
    """Load transaction data from Excel file into the database.

    Args:
        conn: SQLite database connection.
        excel_path: Path to the transactions Excel file.

    Returns:
        Number of rows loaded.

    Raises:
        FileNotFoundError: If the Excel file doesn't exist.
    """
    if not Path(excel_path).exists():
        raise FileNotFoundError(f"Excel file not found: {excel_path}")

    df = pd.read_excel(excel_path)

    bool_columns = ["is_international", "is_recurring"]
    for col in bool_columns:
        if col in df.columns:
            df[col] = df[col].astype(int)

    df.to_sql("transactions", conn, if_exists="replace", index=False)
    print(f"Loaded {len(df)} rows into transactions table")
    return len(df)


def verify_data(conn: sqlite3.Connection) -> None:
    """Run sample queries to verify data was loaded correctly.

    Args:
        conn: SQLite database connection.
    """
    cursor = conn.cursor()

    print("\n" + "=" * 60)
    print("DATA VERIFICATION")
    print("=" * 60)

    cursor.execute("SELECT COUNT(*) FROM customers")
    customer_count = cursor.fetchone()[0]
    print(f"\nTotal customers: {customer_count}")

    cursor.execute("SELECT COUNT(*) FROM transactions")
    transaction_count = cursor.fetchone()[0]
    print(f"Total transactions: {transaction_count}")

    print("\n--- Sample Customers (first 5) ---")
    cursor.execute("""
        SELECT 
            customer_id,
            first_name,
            last_name,
            city,
            account_type,
            balance
        FROM customers
        LIMIT 5
    """)
    for row in cursor.fetchall():
        print(f"  {row}")

    print("\n--- Sample Transactions (first 5) ---")
    cursor.execute("""
        SELECT 
            transaction_id,
            customer_id,
            transaction_date,
            transaction_type,
            amount,
            status
        FROM transactions
        LIMIT 5
    """)
    for row in cursor.fetchall():
        print(f"  {row}")

    print("\n--- Customer Transactions Summary ---")
    cursor.execute("""
        SELECT 
            c.customer_id,
            c.first_name || ' ' || c.last_name AS customer_name,
            c.city,
            COUNT(t.transaction_id) AS transaction_count,
            ROUND(SUM(t.amount), 2) AS total_amount,
            ROUND(AVG(t.amount), 2) AS avg_amount
        FROM customers c
        LEFT JOIN transactions t ON c.customer_id = t.customer_id
        GROUP BY c.customer_id, customer_name, c.city
        ORDER BY transaction_count DESC
        LIMIT 10
    """)
    print("\nTop 10 customers by transaction count:")
    for row in cursor.fetchall():
        print(f"  {row[0]} | {row[1]} | {row[2]} | {row[3]} txns | Total: £{row[4]} | Avg: £{row[5]}")


def main() -> None:
    """Main function to create database and load data."""
    scripts_dir = Path(__file__).parent
    data_dir = scripts_dir.parent / "data"
    db_path = data_dir / "santander_bank.db"
    customers_excel = data_dir / "santander_customers.xlsx"
    transactions_excel = data_dir / "santander_transactions.xlsx"

    if db_path.exists():
        db_path.unlink()
        print(f"Removed existing database: {db_path}")

    conn = create_database(str(db_path))

    try:
        create_customers_table(conn)
        create_transactions_table(conn)

        load_customers_data(conn, str(customers_excel))
        load_transactions_data(conn, str(transactions_excel))

        verify_data(conn)

    finally:
        conn.close()
        print(f"\nDatabase created successfully: {db_path}")


if __name__ == "__main__":
    main()
