CREATE OR ALTER PROCEDURE dbo.sp_daily_customer_metrics_refactored @ReportDate date
AS
BEGIN
 SET NOCOUNT ON;
 ;WITH tx AS (
   SELECT *, ROW_NUMBER() OVER (PARTITION BY transaction_id ORDER BY updated_at DESC, source_row DESC) rn FROM dbo.transactions
 ), customer AS (
   SELECT *, ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY updated_at DESC, source_row DESC) rn FROM dbo.customers
 ), merchant AS (
   SELECT *, ROW_NUMBER() OVER (PARTITION BY merchant_id ORDER BY updated_at DESC, source_row DESC) rn FROM dbo.merchants
 )
 SELECT t.transaction_id, t.account_id, a.customer_id,
   NULLIF(t.merchant_id, '') merchant_id, m.merchant_name, c.segment,
   CONVERT(varchar(19), TRY_CONVERT(datetime2, t.event_ts, 126), 126) event_ts,
   CONVERT(bigint, TRY_CONVERT(decimal(18,2), t.amount) * 100) amount_minor,
   t.currency, t.status
 FROM tx t JOIN dbo.accounts a ON a.account_id = t.account_id
 JOIN customer c ON a.customer_id = c.customer_id AND c.rn = 1
 LEFT JOIN merchant m ON t.merchant_id = m.merchant_id AND m.rn = 1
 WHERE t.rn = 1 AND LEN(t.event_ts) = 19
   AND TRY_CONVERT(datetime2, t.event_ts, 126) >= CONVERT(datetime2, @ReportDate)
   AND TRY_CONVERT(datetime2, t.event_ts, 126) < DATEADD(day, 1, CONVERT(datetime2, @ReportDate))
   AND TRY_CONVERT(decimal(18,2), t.amount) IS NOT NULL
   AND t.currency IN ('COP', 'USD') AND t.status IN ('POSTED', 'CANCELLED')
 ORDER BY t.transaction_id;
END;
GO
