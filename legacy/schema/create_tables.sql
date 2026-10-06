-- SQL Server 2017+. Run ONLY in a new, disposable workshop database.
-- Raw strings mirror Bronze ingestion; this schema is deliberately not a production design.
CREATE TABLE dbo.transactions (
 transaction_id varchar(32) NOT NULL, account_id varchar(16) NOT NULL,
 merchant_id varchar(16) NULL, event_ts varchar(32) NOT NULL,
 amount varchar(32) NOT NULL, currency varchar(3) NOT NULL,
 status varchar(16) NOT NULL, updated_at varchar(32) NOT NULL, source_row bigint NOT NULL
);
CREATE TABLE dbo.accounts (account_id varchar(16) PRIMARY KEY, customer_id varchar(16) NOT NULL);
CREATE TABLE dbo.customers (customer_id varchar(16) NOT NULL, segment varchar(32) NOT NULL, updated_at varchar(32) NOT NULL, source_row bigint NOT NULL);
CREATE TABLE dbo.merchants (merchant_id varchar(16) NOT NULL, merchant_name varchar(100) NOT NULL, updated_at varchar(32) NOT NULL, source_row bigint NOT NULL);
GO
