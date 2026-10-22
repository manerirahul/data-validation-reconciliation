"""Reconcile orders vs payments and write a break report.

Run from the repo root:
    python python/reconcile.py

Reads data/orders_synthetic.csv and data/payments_synthetic.csv,
writes reconciliation_report.csv next to this script's parent folder,
and prints a summary. All data is synthetic.
"""

import csv
import os
from collections import Counter

import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    orders = pd.read_csv(os.path.join(BASE, "data", "orders_synthetic.csv"))
    payments = pd.read_csv(os.path.join(BASE, "data", "payments_synthetic.csv"))

    breaks = []

    # 1. Missing payment: order exists, no payment found.
    paid_ids = set(payments["order_id"])
    for _, o in orders.iterrows():
        if o["order_id"] not in paid_ids:
            breaks.append({
                "break_type": "MISSING_PAYMENT",
                "order_id": o["order_id"],
                "order_amount": o["amount"],
                "payment_amount": "",
                "difference": o["amount"],
                "detail": "Order has no matching payment.",
            })

    # 2. Orphan payment: payment exists, no order found.
    order_ids = set(orders["order_id"])
    for _, p in payments.iterrows():
        if p["order_id"] not in order_ids:
            breaks.append({
                "break_type": "ORPHAN_PAYMENT",
                "order_id": p["order_id"],
                "order_amount": "",
                "payment_amount": p["amount"],
                "difference": p["amount"],
                "detail": "Payment has no matching order.",
            })

    # 3. Amount mismatch + 4. Duplicate payment, per matched order.
    order_amount = dict(zip(orders["order_id"], orders["amount"]))
    counts = Counter(payments["order_id"])
    for order_id, group in payments.groupby("order_id"):
        if order_id not in order_amount:
            continue
        if counts[order_id] > 1:
            breaks.append({
                "break_type": "DUPLICATE_PAYMENT",
                "order_id": order_id,
                "order_amount": order_amount[order_id],
                "payment_amount": round(group["amount"].sum(), 2),
                "difference": round(group["amount"].sum() - order_amount[order_id], 2),
                "detail": f"{counts[order_id]} payments found for one order.",
            })
            continue
        paid = group.iloc[0]["amount"]
        if round(paid - order_amount[order_id], 2) != 0:
            breaks.append({
                "break_type": "AMOUNT_MISMATCH",
                "order_id": order_id,
                "order_amount": order_amount[order_id],
                "payment_amount": paid,
                "difference": round(paid - order_amount[order_id], 2),
                "detail": "Payment amount differs from order amount.",
            })

    report = pd.DataFrame(breaks).sort_values(["break_type", "order_id"])
    out_path = os.path.join(BASE, "reconciliation_report.csv")
    report.to_csv(out_path, index=False)

    print(f"Orders checked:   {len(orders)}")
    print(f"Payments checked: {len(payments)}")
    print(f"Breaks found:     {len(report)}")
    print(report["break_type"].value_counts().to_string())
    print(f"\nReport written to: {out_path}")


if __name__ == "__main__":
    main()
