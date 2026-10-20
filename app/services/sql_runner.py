import sqlite3
import time
from typing import Dict, Any, List

def init_ecommerce_schema(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(150) UNIQUE NOT NULL,
        country VARCHAR(50) DEFAULT 'US',
        tier VARCHAR(20) DEFAULT 'Standard',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sku VARCHAR(50) UNIQUE NOT NULL,
        name VARCHAR(150) NOT NULL,
        category VARCHAR(50) NOT NULL,
        price DECIMAL(10,2) NOT NULL,
        stock_quantity INTEGER NOT NULL DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        total_amount DECIMAL(10,2) NOT NULL,
        status VARCHAR(30) DEFAULT 'COMPLETED',
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    );

    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price DECIMAL(10,2) NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    );

    CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);
    CREATE INDEX IF NOT EXISTS idx_order_date ON orders(order_date);
    CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
    """)

    # Seed data
    cur.execute("SELECT COUNT(*) FROM customers")
    if cur.fetchone()[0] == 0:
        cur.executemany("""
        INSERT INTO customers (name, email, country, tier) VALUES (?, ?, ?, ?)
        """, [
            ("Alice Smith", "alice@amazon.com", "US", "Prime"),
            ("Bob Jones", "bob@google.com", "UK", "Standard"),
            ("Charlie Brown", "charlie@microsoft.com", "US", "Prime"),
            ("Diana Prince", "diana@uber.com", "CA", "VIP"),
            ("Evan Wright", "evan@meta.com", "US", "Standard"),
            ("Fiona Gallagher", "fiona@netflix.com", "DE", "Standard"),
            ("George Clark", "george@apple.com", "US", "Prime"),
            ("Hannah Abbott", "hannah@stripe.com", "UK", "VIP"),
        ])

        cur.executemany("""
        INSERT INTO products (sku, name, category, price, stock_quantity) VALUES (?, ?, ?, ?, ?)
        """, [
            ("SKU-LAP-01", "MacBook Pro M3 Max", "Electronics", 2499.00, 45),
            ("SKU-LAP-02", "Dell XPS 15", "Electronics", 1799.00, 60),
            ("SKU-PHN-01", "iPhone 16 Pro", "Electronics", 1099.00, 120),
            ("SKU-AUD-01", "Sony WH-1000XM5", "Audio", 399.00, 85),
            ("SKU-AUD-02", "AirPods Pro 2", "Audio", 249.00, 200),
            ("SKU-DESK-01", "Ergonomic Standing Desk", "Furniture", 599.00, 30),
            ("SKU-CHAIR-01", "Herman Miller Aeron", "Furniture", 1250.00, 18),
            ("SKU-MON-01", "LG 27GP850-B Gaming Monitor", "Electronics", 349.00, 75),
        ])

        cur.executemany("""
        INSERT INTO orders (customer_id, order_date, total_amount, status) VALUES (?, ?, ?, ?)
        """, [
            (1, "2026-01-10 10:15:00", 2499.00, "COMPLETED"),
            (1, "2026-02-14 14:22:00", 399.00, "COMPLETED"),
            (2, "2026-02-01 09:30:00", 1799.00, "COMPLETED"),
            (3, "2026-02-18 16:45:00", 1348.00, "COMPLETED"),
            (4, "2026-03-01 11:10:00", 2898.00, "COMPLETED"),
            (4, "2026-03-12 18:00:00", 1250.00, "COMPLETED"),
            (5, "2026-03-15 13:20:00", 249.00, "REFUNDED"),
            (7, "2026-03-20 15:40:00", 1099.00, "COMPLETED"),
        ])

        cur.executemany("""
        INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)
        """, [
            (1, 1, 1, 2499.00),
            (2, 4, 1, 399.00),
            (3, 2, 1, 1799.00),
            (4, 3, 1, 1099.00),
            (4, 5, 1, 249.00),
            (5, 1, 1, 2499.00),
            (5, 4, 1, 399.00),
            (6, 7, 1, 1250.00),
            (7, 5, 1, 249.00),
            (8, 3, 1, 1099.00),
        ])
    conn.commit()

def init_fintech_schema(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_number VARCHAR(34) UNIQUE NOT NULL,
        user_name VARCHAR(100) NOT NULL,
        account_type VARCHAR(20) DEFAULT 'CHECKING',
        balance DECIMAL(15,2) NOT NULL DEFAULT 0.00,
        currency VARCHAR(3) DEFAULT 'USD',
        status VARCHAR(20) DEFAULT 'ACTIVE'
    );

    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_account_id INTEGER NOT NULL,
        receiver_account_id INTEGER NOT NULL,
        amount DECIMAL(15,2) NOT NULL,
        status VARCHAR(20) DEFAULT 'SUCCESS', -- SUCCESS, PENDING, FAILED
        idempotency_key VARCHAR(64) UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sender_account_id) REFERENCES accounts(id),
        FOREIGN KEY (receiver_account_id) REFERENCES accounts(id)
    );

    CREATE INDEX IF NOT EXISTS idx_tx_sender ON transactions(sender_account_id);
    CREATE INDEX IF NOT EXISTS idx_tx_receiver ON transactions(receiver_account_id);
    CREATE INDEX IF NOT EXISTS idx_tx_idempotency ON transactions(idempotency_key);
    """)

    cur.execute("SELECT COUNT(*) FROM accounts")
    if cur.fetchone()[0] == 0:
        cur.executemany("""
        INSERT INTO accounts (account_number, user_name, account_type, balance, currency, status) VALUES (?, ?, ?, ?, ?, ?)
        """, [
            ("ACC-US-1001", "Stripe Internal Settlement", "SETTLEMENT", 5000000.00, "USD", "ACTIVE"),
            ("ACC-US-2002", "Uber Technologies Inc", "COMMERCIAL", 1250000.00, "USD", "ACTIVE"),
            ("ACC-US-3003", "Apex Capital LLC", "CHECKING", 85000.00, "USD", "ACTIVE"),
            ("ACC-US-4004", "Retail Customer John", "SAVINGS", 14250.00, "USD", "ACTIVE"),
            ("ACC-US-5005", "Retail Customer Jane", "CHECKING", 9300.00, "USD", "ACTIVE"),
            ("ACC-US-6006", "Suspicious Shell Co", "CHECKING", 250.00, "USD", "FROZEN"),
        ])

        cur.executemany("""
        INSERT INTO transactions (sender_account_id, receiver_account_id, amount, status, idempotency_key, created_at) VALUES (?, ?, ?, ?, ?, ?)
        """, [
            (2, 1, 250000.00, "SUCCESS", "tx-idemp-001", "2026-03-01 10:00:00"),
            (3, 2, 12000.00, "SUCCESS", "tx-idemp-002", "2026-03-02 11:30:00"),
            (4, 5, 450.00, "SUCCESS", "tx-idemp-003", "2026-03-03 14:15:00"),
            (5, 4, 120.00, "SUCCESS", "tx-idemp-004", "2026-03-04 09:20:00"),
            (3, 4, 3500.00, "SUCCESS", "tx-idemp-005", "2026-03-05 16:45:00"),
            (6, 1, 100000.00, "FAILED", "tx-idemp-006", "2026-03-06 18:00:00"),
        ])
    conn.commit()

def init_hr_schema(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS departments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dept_name VARCHAR(100) NOT NULL,
        location VARCHAR(100) NOT NULL,
        annual_budget DECIMAL(15,2) NOT NULL
    );

    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100) NOT NULL,
        department_id INTEGER,
        manager_id INTEGER,
        role VARCHAR(100) NOT NULL,
        salary DECIMAL(10,2) NOT NULL,
        hire_date DATE NOT NULL,
        FOREIGN KEY (department_id) REFERENCES departments(id),
        FOREIGN KEY (manager_id) REFERENCES employees(id)
    );

    CREATE TABLE IF NOT EXISTS performance_reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER NOT NULL,
        review_year INTEGER NOT NULL,
        rating DECIMAL(3,1) NOT NULL, -- 1.0 to 5.0
        bonus_awarded DECIMAL(10,2) DEFAULT 0.00,
        FOREIGN KEY (employee_id) REFERENCES employees(id)
    );

    CREATE INDEX IF NOT EXISTS idx_emp_dept ON employees(department_id);
    CREATE INDEX IF NOT EXISTS idx_emp_salary ON employees(salary);
    """)

    cur.execute("SELECT COUNT(*) FROM departments")
    if cur.fetchone()[0] == 0:
        cur.executemany("""
        INSERT INTO departments (dept_name, location, annual_budget) VALUES (?, ?, ?)
        """, [
            ("Core Engineering", "San Francisco, CA", 15000000.00),
            ("Cloud Infrastructure & SRE", "Seattle, WA", 12000000.00),
            ("Data & AI Platform", "New York, NY", 18000000.00),
            ("Product & Design", "Austin, TX", 8000000.00),
        ])

        cur.executemany("""
        INSERT INTO employees (name, department_id, manager_id, role, salary, hire_date) VALUES (?, ?, ?, ?, ?, ?)
        """, [
            ("Satya Nadella", 1, None, "VP Engineering", 350000.00, "2018-05-01"),
            ("Sundar Pichai", 2, None, "VP Infrastructure", 340000.00, "2018-06-15"),
            ("Linus Torvalds", 1, 1, "Principal Architect", 260000.00, "2019-01-10"),
            ("Grace Hopper", 1, 3, "Staff Backend Engineer", 195000.00, "2020-03-12"),
            ("Alan Turing", 3, 2, "Staff ML Engineer", 205000.00, "2020-08-01"),
            ("Ada Lovelace", 3, 5, "Senior Data Engineer", 165000.00, "2021-02-15"),
            ("Margaret Hamilton", 2, 2, "Senior SRE Engineer", 170000.00, "2021-06-20"),
            ("Ken Thompson", 1, 4, "Mid Backend Engineer", 135000.00, "2023-01-10"),
            ("Dennis Ritchie", 1, 4, "Junior Backend Engineer", 110000.00, "2024-07-01"),
        ])

        cur.executemany("""
        INSERT INTO performance_reviews (employee_id, review_year, rating, bonus_awarded) VALUES (?, ?, ?, ?)
        """, [
            (3, 2025, 4.9, 45000.00),
            (4, 2025, 4.8, 30000.00),
            (5, 2025, 4.9, 35000.00),
            (6, 2025, 4.5, 20000.00),
            (7, 2025, 4.7, 25000.00),
            (8, 2025, 4.2, 12000.00),
            (9, 2025, 4.0, 8000.00),
        ])
    conn.commit()

def run_sql_query(query: str, schema_name: str = "ecommerce", include_explain: bool = True, max_rows: int = 100) -> Dict[str, Any]:
    """
    Executes a SQL query in an isolated in-memory or template database with realistic MNC data.
    Runs EXPLAIN QUERY PLAN to evaluate indexing, query cost, and execution efficiency.
    """
    # Guard against destructive commands
    forbidden_sql = ["ATTACH", "DETACH", "PRAGMA", "LOAD_EXTENSION"]
    for keyword in forbidden_sql:
        if keyword in query.upper():
            return {
                "columns": [],
                "rows": [],
                "row_count": 0,
                "execution_time_ms": 0.0,
                "success": False,
                "error": f"Keyword '{keyword}' is forbidden in interview sandbox."
            }

    conn = sqlite3.connect(":memory:")
    try:
        # Load appropriate schema
        if schema_name == "fintech":
            init_fintech_schema(conn)
        elif schema_name == "hr_tech":
            init_hr_schema(conn)
        else:
            init_ecommerce_schema(conn)

        cur = conn.cursor()
        start_time = time.perf_counter()
        
        # Execute Query
        cur.execute(query)
        columns = [desc[0] for desc in cur.description] if cur.description else []
        rows = cur.fetchmany(max_rows)
        execution_time_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

        # Execute EXPLAIN QUERY PLAN if SELECT
        query_plan = []
        clean_q = query.strip().upper()
        if include_explain and (clean_q.startswith("SELECT") or clean_q.startswith("WITH")):
            try:
                explain_cur = conn.cursor()
                explain_cur.execute(f"EXPLAIN QUERY PLAN {query}")
                plan_rows = explain_cur.fetchall()
                # SQLite explain format: (id, parent, notused, detail)
                for r in plan_rows:
                    query_plan.append({
                        "id": r[0],
                        "parent": r[1],
                        "detail": r[3] if len(r) > 3 else str(r)
                    })
            except Exception:
                pass

        return {
            "columns": columns,
            "rows": rows,
            "row_count": len(rows),
            "execution_time_ms": execution_time_ms,
            "success": True,
            "error": None,
            "query_plan": query_plan
        }
    except Exception as e:
        return {
            "columns": [],
            "rows": [],
            "row_count": 0,
            "execution_time_ms": 0.0,
            "success": False,
            "error": str(e),
            "query_plan": []
        }
    finally:
        conn.close()
