# SECURITY — Quant-specific

- Never commit data-vendor or broker API keys. Load secrets from environment
  variables and parse them at the configuration boundary.
- Vendor Parquet files must not contain personally identifiable information
  (PII); logs must not record real order IDs.
- Linters reject hard-coded secrets such as `api_key=...`.
