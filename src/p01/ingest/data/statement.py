INSERT = """
    insert or ignore into raw.invoice_lines (
        _ingest_id, _workbook_sha256, _source_sheet, _source_row, _ingested_at,
        invoice_no, stock_code, invoice_ts_local, quantity, unit_price,
        customer_id, country, raw_payload
    ) values (
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, cast(? as json)
    );
"""