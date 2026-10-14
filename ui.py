import requests
import streamlit as st

API = "http://127.0.0.1:8000"

st.title("Portfolio Tracker")

st.header("New Transaction")
with st.form("purchase_form"):
    ticker = st.text_input("Ticker", "VUAA").upper()
    side = st.selectbox("Side", ["BUY", "SELL"])
    quantity = st.number_input("Quantity", min_value=0.01, step=0.1)
    price = st.number_input("Price", min_value=0.01, step=0.01)
    purchase_date = st.date_input("Date")
    submitted = st.form_submit_button("Save")

if submitted:
    response = requests.post(f"{API}/purchases", json={
        "ticker": ticker,
        "quantity": quantity,
        "price": price,
        "purchase_date": purchase_date.isoformat(),
        "side": side,
    })
    if response.status_code == 200:
        st.success("The transaction has been saved.")
    else:
        st.error(response.json()["detail"])

st.header("My positions")
positions = requests.get(f"{API}/positions").json()
if positions:
    st.dataframe(positions)
else:
    st.info("You currently don't have any open positions")