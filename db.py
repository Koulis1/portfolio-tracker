import sqlite3

DB_NAME = "portfolio.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                quantity REAL NOT NULL,
                price REAL NOT NULL,
                purchase_date TEXT NOT NULL,
                side TEXT NOT NULL DEFAULT 'BUY'
            )
        """)

def add_purchase(ticker, quantity, price, purchase_date, side = "BUY"):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO purchases (ticker, quantity, price, purchase_date, side) VALUES (?, ?, ?, ?, ?)",
            (ticker, quantity, price, purchase_date, side)
        )

def get_positions():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT ticker, quantity, price, side
            FROM purchases
            ORDER BY purchase_date, id
        """).fetchall()

    state = {}  # ticker -> {"quantity": ..., "cost": ...}
    for ticker, qty, price, side in rows:
        pos = state.setdefault(ticker, {"quantity": 0, "cost": 0})
        if side == "BUY":
            pos["quantity"] += qty
            pos["cost"] += qty * price
        else:
            avg = pos["cost"] / pos["quantity"]
            pos["cost"] -= qty * avg
            pos["quantity"] -= qty

    return [
        {"ticker": t, "quantity": p["quantity"], "avg_price": p["cost"] / p["quantity"]}
        for t, p in state.items()
        if p["quantity"] > 1e-9
    ]

def get_purchases():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, ticker, quantity, price, purchase_date FROM purchases ORDER BY purchase_date"
        ).fetchall()
    return [
        {"id": i, "ticker": t, "quantity": q, "price": p, "purchase_date": d}
        for i, t, q, p, d in rows
    ]

def delete_purchase(purchase_id):
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM purchases WHERE id = ?",
            (purchase_id,)
        )
        return cursor.rowcount

class InsufficientQuantityError(Exception):
    pass

def get_held_quantity(conn, ticker):
    row = conn.execute("""
        SELECT COALESCE(SUM(CASE WHEN side = 'BUY' THEN quantity ELSE -quantity END), 0)
        FROM purchases
        WHERE ticker = ?
    """, (ticker,)).fetchone()
    return row[0]

def add_purchase(ticker, quantity, price, purchase_date, side="BUY"):
    with get_connection() as conn:
        if side == "SELL":
            held = get_held_quantity(conn, ticker)
            if quantity > held:
                raise InsufficientQuantityError(
                    f"Cannot sell {quantity} of {ticker}, only {held} held"
                )
        conn.execute(
            "INSERT INTO purchases (ticker, quantity, price, purchase_date, side) VALUES (?, ?, ?, ?, ?)",
            (ticker, quantity, price, purchase_date, side)
        )

def get_pnl(ticker, current_price):
    for pos in get_positions():
        if pos["ticker"] == ticker:
            cost = pos["quantity"] * pos["avg_price"]
            value = pos["quantity"] * current_price
            pnl = value - cost
            return {
                "ticker": ticker,
                "quantity": pos["quantity"],
                "avg_price": round(pos["avg_price"], 2),
                "current_price": current_price,
                "cost": round(cost, 2),
                "value": round(value, 2),
                "pnl": round(pnl, 2),
                "pnl_pct": round(pnl / cost * 100, 2),
            }
    return None