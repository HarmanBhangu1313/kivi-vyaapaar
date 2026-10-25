"""
Database management for Kivi-Vyaapaar (किरण - कीवी व्यापार)
SQLite-backed store for Khata (Ledger), Inventory, Vendors, Bills, and Indus Audit Logs.
"""

import sqlite3
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "vyaapaar.db")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Customers table (Khata)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        phone TEXT,
        balance REAL DEFAULT 0.0,
        credit_limit REAL DEFAULT 15000.0,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 2. Ledger Transactions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        customer_name TEXT NOT NULL,
        type TEXT NOT NULL, -- 'UDHAAR', 'JAMA'
        amount REAL NOT NULL,
        note TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    )
    """)

    # 3. Inventory table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name TEXT UNIQUE NOT NULL,
        category TEXT DEFAULT 'General',
        quantity REAL NOT NULL,
        unit TEXT NOT NULL,
        unit_price REAL NOT NULL,
        reorder_level REAL DEFAULT 10.0,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 4. Digital Invoices / Bills table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bill_no TEXT UNIQUE NOT NULL,
        customer_name TEXT NOT NULL,
        items TEXT NOT NULL, -- JSON list of items
        subtotal REAL NOT NULL,
        tax REAL DEFAULT 0.0,
        total REAL NOT NULL,
        payment_status TEXT DEFAULT 'UDHAAR',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 5. Vendors table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vendors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        phone TEXT,
        category TEXT,
        last_order TEXT
    )
    """)

    # 6. Indus Approvals table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS approvals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action_type TEXT NOT NULL,
        title TEXT NOT NULL,
        details TEXT NOT NULL,
        payload TEXT NOT NULL,
        status TEXT DEFAULT 'PENDING',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        resolved_at TIMESTAMP
    )
    """)

    # 7. Audit Logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        voice_transcript TEXT,
        agent_intent TEXT,
        plan_steps TEXT,
        tools_executed TEXT,
        result_summary TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

def seed_sample_data():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM customers")
    if cursor.fetchone()[0] == 0:
        customers = [
            ("Ramesh Kirana", "9876543210", 1450.0, 15000.0),
            ("Gupta Ji Chai Wale", "9812345678", 680.0, 5000.0),
            ("Varanasi Sweets Corner", "9823456789", 3200.0, 25000.0),
            ("Pandey Ji (Assi Ghat)", "9834567890", 250.0, 5000.0),
            ("Kashi Silk Emporium", "9845678901", 0.0, 50000.0)
        ]
        cursor.executemany(
            "INSERT OR IGNORE INTO customers (name, phone, balance, credit_limit) VALUES (?, ?, ?, ?)",
            customers
        )
        cursor.execute("INSERT INTO transactions (customer_name, type, amount, note) VALUES ('Ramesh Kirana', 'UDHAAR', 1200.0, '20 packets basmati rice')")
        cursor.execute("INSERT INTO transactions (customer_name, type, amount, note) VALUES ('Ramesh Kirana', 'UDHAAR', 250.0, '5 kg mustard oil')")
        cursor.execute("INSERT INTO transactions (customer_name, type, amount, note) VALUES ('Gupta Ji Chai Wale', 'JAMA', 500.0, 'UPI payment received')")
        cursor.execute("INSERT INTO transactions (customer_name, type, amount, note) VALUES ('Gupta Ji Chai Wale', 'UDHAAR', 680.0, 'Sugar 10kg & Tea 2kg')")

    cursor.execute("SELECT COUNT(*) FROM inventory")
    if cursor.fetchone()[0] == 0:
        inventory_items = [
            ("Basmati Rice 10kg", "Grains", 18.0, "bags", 650.0, 10.0),
            ("Mustard Oil (Kachi Ghani 1L)", "Oils", 42.0, "packets", 145.0, 15.0),
            ("Refined Oil 15L Tin", "Oils", 4.0, "tin", 1850.0, 6.0),
            ("Sugar (Madhur)", "Groceries", 65.0, "kg", 44.0, 20.0),
            ("Tata Tea Gold 500g", "Beverages", 8.0, "packets", 290.0, 10.0),
            ("Wheat Flour (Aashirvaad 10kg)", "Grains", 25.0, "bags", 420.0, 10.0),
            ("Toor Dal 1kg", "Pulses", 30.0, "packets", 160.0, 12.0)
        ]
        cursor.executemany(
            "INSERT OR IGNORE INTO inventory (item_name, category, quantity, unit, unit_price, reorder_level) VALUES (?, ?, ?, ?, ?, ?)",
            inventory_items
        )

    conn.commit()
    conn.close()

def save_bill(bill_no: str, customer_name: str, items: list, subtotal: float, tax: float, total: float, payment_status: str = "UDHAAR") -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO bills (bill_no, customer_name, items, subtotal, tax, total, payment_status)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (bill_no, customer_name, json.dumps(items), subtotal, tax, total, payment_status))
    bill_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return {
        "id": bill_id,
        "bill_no": bill_no,
        "customer_name": customer_name,
        "items": items,
        "subtotal": subtotal,
        "tax": tax,
        "total": total,
        "payment_status": payment_status,
        "created_at": datetime.now().strftime("%d %b %Y, %I:%M %p")
    }

def get_recent_bills(limit: int = 10) -> List[Dict[str, Any]]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM bills ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d["items"] = json.loads(d["items"])
        result.append(d)
    return result

def get_all_customers() -> List[Dict[str, Any]]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM customers ORDER BY updated_at DESC, id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_recent_transactions(limit: int = 25) -> List[Dict[str, Any]]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM transactions ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_inventory() -> List[Dict[str, Any]]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM inventory ORDER BY quantity <= reorder_level DESC, item_name ASC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_pending_approvals() -> List[Dict[str, Any]]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM approvals WHERE status = 'PENDING' ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_business_kpis() -> Dict[str, Any]:
    conn = get_connection()
    total_udhaar = conn.execute("SELECT COALESCE(SUM(balance), 0) FROM customers WHERE balance > 0").fetchone()[0]
    total_items = conn.execute("SELECT COUNT(*) FROM inventory").fetchone()[0]
    low_stock = conn.execute("SELECT COUNT(*) FROM inventory WHERE quantity <= reorder_level").fetchone()[0]
    today_transactions = conn.execute("SELECT COUNT(*), COALESCE(SUM(amount), 0) FROM transactions").fetchone()
    pending_approvals = conn.execute("SELECT COUNT(*) FROM approvals WHERE status = 'PENDING'").fetchone()[0]
    total_bills = conn.execute("SELECT COUNT(*) FROM bills").fetchone()[0]
    conn.close()

    return {
        "total_udhaar": round(total_udhaar, 2),
        "total_inventory_items": total_items,
        "low_stock_alerts": low_stock,
        "total_transactions_count": today_transactions[0],
        "total_transaction_volume": round(today_transactions[1], 2),
        "pending_approvals_count": pending_approvals,
        "total_bills_generated": total_bills
    }
