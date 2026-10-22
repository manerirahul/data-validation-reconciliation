-- Reconciliation checks: orders vs payments (SQLite-compatible).
-- Load the two CSVs into tables named orders and payments first, e.g.:
--   .import --csv data/orders_synthetic.csv orders
--   .import --csv data/payments_synthetic.csv payments
-- Then run this file. Each query returns one break type.

-- 1. Missing payment: order exists, no payment found.
SELECT 'MISSING_PAYMENT' AS break_type, o.order_id, o.amount AS order_amount,
       NULL AS payment_amount, o.amount AS difference
FROM orders o
LEFT JOIN payments p ON p.order_id = o.order_id
WHERE p.order_id IS NULL;

-- 2. Orphan payment: payment exists, no order found.
SELECT 'ORPHAN_PAYMENT' AS break_type, p.order_id, NULL AS order_amount,
       p.amount AS payment_amount, p.amount AS difference
FROM payments p
LEFT JOIN orders o ON o.order_id = p.order_id
WHERE o.order_id IS NULL;

-- 3. Amount mismatch: one payment, but the amount differs.
SELECT 'AMOUNT_MISMATCH' AS break_type, o.order_id, o.amount AS order_amount,
       p.amount AS payment_amount, ROUND(p.amount - o.amount, 2) AS difference
FROM orders o
JOIN payments p ON p.order_id = o.order_id
GROUP BY o.order_id
HAVING COUNT(*) = 1 AND ROUND(p.amount - o.amount, 2) <> 0;

-- 4. Duplicate payment: more than one payment for the same order.
SELECT 'DUPLICATE_PAYMENT' AS break_type, o.order_id, o.amount AS order_amount,
       ROUND(SUM(p.amount), 2) AS payment_amount,
       ROUND(SUM(p.amount) - o.amount, 2) AS difference
FROM orders o
JOIN payments p ON p.order_id = o.order_id
GROUP BY o.order_id
HAVING COUNT(*) > 1;

-- 5. Data-quality guardrails: nulls and non-positive amounts.
SELECT 'NULL_OR_INVALID' AS break_type, order_id, amount AS order_amount,
       NULL AS payment_amount, NULL AS difference
FROM orders
WHERE order_id IS NULL OR amount IS NULL OR amount <= 0;
