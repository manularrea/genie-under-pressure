Read the supplied BUSINESS_CONTRACT.md and candidate before editing.
Preserve the half-open local business-day window, signed decimal minor amounts,
cancellation history, deterministic latest-row deduplication and optional merchant joins.
Do not aggregate different currencies together or multiply rows by dimension joins.
Malformed inputs need quarantine, not silent removal or zero substitution.
Explain every semantic transformation. Do not modify expected outputs.
