# Data Validation & Reconciliation — SQL + Python

A small, runnable demo of the work a Business Analyst does when two systems
disagree: find the breaks, quantify them, and produce a report a business
owner can act on.

## The problem

Two source systems each hold a view of the same orders:

- `orders` — what was ordered (order system)
- `payments` — what was paid (payment system)

In a healthy process every order has exactly one matching payment for the
same amount. In reality there are orphans, duplicates, and amount mismatches.
This repo finds all four break types and writes a reconciliation report.

## What's in here

| File | What it does |
| --- | --- |
| `data/orders_synthetic.csv` | 30 synthetic orders |
| `data/payments_synthetic.csv` | 31 synthetic payments, with deliberate breaks |
| `sql/reconciliation_checks.sql` | The same checks in SQL (SQLite-compatible) |
| `python/reconcile.py` | The same checks in Python/pandas, writes `reconciliation_report.csv` |

## How to run it

```bash
pip install pandas
python python/reconcile.py
```

Output: a summary printed to the console plus `reconciliation_report.csv`
with one row per break (break type, order id, amounts, difference).

## What it checks

1. **Missing payment** — order exists, no payment found.
2. **Orphan payment** — payment exists, no order found.
3. **Amount mismatch** — order and payment match on id but not on amount.
4. **Duplicate payment** — more than one payment for the same order.

## Why this shape

The BA value is not the script — it is the *framing*: every break type maps
to a business question (did we ship unpaid orders? did we take money we
can't account for? is someone keying amounts wrong?). The report is built
so a non-technical owner can read it without opening code.

## Data note

All data is **synthetic**, generated for this demo. No real customer,
employer, or production data is used anywhere in this repo.
