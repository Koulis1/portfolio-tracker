# Portfolio Tracker

A small portfolio tracker for recording ETF buys and sells (e.g. VUAA) and viewing open positions with average cost and unrealized profit/loss.

> Learning project, built with heavy AI guidance (Claude) while studying databases and data structures.

## Tech stack

- Python
- FastAPI (REST API)
- SQLite (`sqlite3` module)
- Streamlit (web UI)

## Features

- Record BUY and SELL transactions
- Input validation (positive quantities and prices, valid dates)
- Overselling protection (HTTP 409 if you sell more than you hold)
- Positions with average cost, calculated chronologically
- Unrealized P&L for a given current price
- Delete a transaction by id

## Setup

```
pip install -r requirements.txt
```

## Run

Terminal 1 (API):

```
python -m uvicorn api:app --reload
```

Terminal 2 (UI):

```
python -m streamlit run ui.py
```

The API docs are available at http://127.0.0.1:8000/docs and the UI at http://localhost:8501.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /purchases | Add a BUY or SELL transaction |
| GET | /purchases | List all transactions |
| DELETE | /purchases/{id} | Delete a transaction |
| GET | /positions | Open positions with average price |
| GET | /pnl/{ticker}?current_price=... | Unrealized P&L for a ticker |

## Notes

Average cost is used as the cost basis method. Other methods (FIFO, LIFO) would give different results.