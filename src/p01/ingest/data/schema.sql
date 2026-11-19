create schema if not exists raw;

create table if not exists raw.invoice_lines (
  _ingest_id          uuid primary key,
  _workbook_sha256    varchar(64) not null,
  _source_sheet       varchar not null,
  _source_row         integer not null,
  _ingested_at        timestamptz not null,
  invoice_no          varchar not null,
  stock_code          varchar not null,
  invoice_ts_local    timestamp not null,
  quantity            integer not null,
  unit_price          decimal(18,4) not null,
  customer_id         varchar,
  country             varchar,
  raw_payload         json not null,
  unique (_workbook_sha256, _source_sheet, _source_row)
);
create index if not exists raw_invoice_no_idx on raw.invoice_lines (invoice_no);
create index if not exists raw_invoice_ts_idx on raw.invoice_lines (invoice_ts_local);
