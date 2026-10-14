from datetime import date
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from db import (
    init_db,
    add_purchase,
    get_positions,
    get_purchases,
    delete_purchase,
    get_pnl,
    InsufficientQuantityError,
)

app = FastAPI()
init_db()

class Purchase(BaseModel):
    ticker: str
    quantity: float = Field(gt=0)
    price: float = Field(gt=0)
    purchase_date: date
    side: Literal["BUY", "SELL"] = "BUY"

@app.post("/purchases")
def create_purchase(purchase: Purchase):
    try:
        add_purchase(
            purchase.ticker,
            purchase.quantity,
            purchase.price,
            purchase.purchase_date.isoformat(),
            purchase.side
        )
    except InsufficientQuantityError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return {"status": "ok"}

@app.get("/positions")
def read_positions():
    return get_positions()

@app.get("/purchases")
def read_purchases():
    return get_purchases()

@app.delete("/purchases/{purchase_id}")
def remove_purchase(purchase_id: int):
    deleted = delete_purchase(purchase_id)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Purchase not found")
    return {"status": "deleted"}

@app.get("/pnl/{ticker}")
def read_pnl(ticker: str, current_price: float = Query(gt=0)):
    result = get_pnl(ticker.upper(), current_price)
    if result is None:
        raise HTTPException(status_code=404, detail="No open position for this ticker")
    return result