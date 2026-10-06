-- Deliberately awkward but contract-preserving legacy procedure.
-- Do not add NOLOCK: this teaching fixture is a static snapshot.
CREATE OR ALTER PROCEDURE dbo.sp_daily_customer_metrics @ReportDate date
AS
BEGIN
 SET NOCOUNT ON;
 DECLARE @D1 datetime2 = CONVERT(datetime2, @ReportDate);
 DECLARE @D2 datetime2 = DATEADD(day, 1, @D1);
 DECLARE @UnusedMode int = 0;
 -- Old comment: "only settled". Wrong! Both POSTED and CANCELLED remain in history.
 SELECT * INTO #TMP_01 FROM (
  SELECT t.*, ROW_NUMBER() OVER (PARTITION BY transaction_id ORDER BY updated_at DESC, source_row DESC) R1
  FROM dbo.transactions t
 ) x WHERE R1 = 1;
 SELECT * INTO #TMP_02 FROM (
  SELECT c.*, ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY updated_at DESC, source_row DESC) R2
  FROM dbo.customers c
 ) x WHERE R2 = 1;
 SELECT * INTO #TMP_03 FROM (
  SELECT m.*, ROW_NUMBER() OVER (PARTITION BY merchant_id ORDER BY updated_at DESC, source_row DESC) R3
  FROM dbo.merchants m
 ) x WHERE R3 = 1;
 -- Invalid input is quarantined by the ingestion contract (see BUSINESS_CONTRACT.md).
 -- This SELECT yields the valid daily snapshot. Currency totals belong in a later stage.
 SELECT t.transaction_id, t.account_id, a.customer_id,
  NULLIF(t.merchant_id, '') merchant_id, m.merchant_name, c.segment,
  CONVERT(varchar(19), TRY_CONVERT(datetime2, t.event_ts, 126), 126) event_ts,
  CONVERT(bigint, TRY_CONVERT(decimal(18,2), t.amount) * 100) amount_minor,
  t.currency, t.status
 INTO #TMP_04
 FROM #TMP_01 t
 INNER JOIN dbo.accounts a ON a.account_id = t.account_id
 INNER JOIN #TMP_02 c ON c.customer_id = a.customer_id
 LEFT JOIN #TMP_03 m ON m.merchant_id = t.merchant_id
 WHERE LEN(t.event_ts) = 19
  AND TRY_CONVERT(datetime2, t.event_ts, 126) >= @D1
  AND TRY_CONVERT(datetime2, t.event_ts, 126) < @D2
  AND TRY_CONVERT(decimal(18,2), t.amount) IS NOT NULL
  AND t.currency IN ('COP', 'USD')
  AND t.status IN ('POSTED', 'CANCELLED');
 -- Legacy shortcut is valid only because exported baseline amount strings have two decimals.
 -- For new formats, use the stricter contract before this stage.
 SELECT transaction_id, account_id, customer_id, merchant_id, merchant_name,
        segment, event_ts, amount_minor, currency, status
 FROM #TMP_04 ORDER BY transaction_id;
END;
GO
