# SECURITY — quant-specific
- Không commit key data vendor / broker. Secrets qua env, parse ở config boundary.
- Parquet vendor không chứa PII; log không ghi order-id thật.
- Linter chặn `api_key=` hardcoded.
