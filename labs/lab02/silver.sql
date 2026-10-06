-- START: plausible migration. Do not approve without reconciliation.
WITH ranked_tx AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY transaction_id ORDER BY updated_at DESC, CAST(source_row AS INTEGER) DESC) AS rn
  FROM transactions
), ranked_merchants AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY merchant_id ORDER BY updated_at DESC, CAST(source_row AS INTEGER) DESC) AS rn
  FROM merchants
), ranked_customers AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY updated_at DESC, CAST(source_row AS INTEGER) DESC) AS rn
  FROM customers
)
SELECT t.transaction_id, t.account_id, a.customer_id,
       NULLIF(t.merchant_id, '') AS merchant_id, m.merchant_name, c.segment,
       valid_ts(t.event_ts) AS event_ts, amount_minor(t.amount) AS amount_minor,
       t.currency, t.status
FROM ranked_tx t
JOIN accounts a ON t.account_id = a.account_id
JOIN ranked_customers c ON a.customer_id = c.customer_id AND c.rn = 1
JOIN ranked_merchants m ON t.merchant_id = m.merchant_id AND m.rn = 1
WHERE t.rn = 1
  AND valid_ts(t.event_ts) >= :report_day || 'T00:00:00'
  AND valid_ts(t.event_ts) <= date(:report_day, '+1 day') || 'T00:00:00'
  AND amount_minor(t.amount) IS NOT NULL
  AND t.currency IN ('COP', 'USD')
  AND t.status = 'POSTED';
