# PCI final source release candidate — 0.12.5-rc.1

**Not production certified.** This release retains the exact cumulative ten-module checkpoint and its permanent IDs. It implements a limited storage/import hardening patch and improves unencrypted-backup consent messaging. No source/book records are rewritten, and no private user entries are bundled.

## Exact byte-level change control

`src/storage.ts` differs intentionally from Checkpoint 4. `audit/final/STORAGE_CHANGE_CONTROL.json` records original and updated SHA-256 hashes. Six inherited validators were amended only to accept this exact audited change while preserving other fingerprint requirements. No database stores, schema versions, canonical research IDs or content were changed.

## Research audit

`audit/final/RESEARCH_INTEGRITY_AUDIT.json` enumerates 201 concepts, their source statuses and duplicate fields, all 16 chapter references and the existing 21-day program links. It contains 16 specific *proposed* corrections for human source review. It does **not** claim PDF image review, independent evidence validation, or approval of those proposed edits.

## Release decision

**Blocked for production** because genuine `npm install` failed with DNS `EAI_AGAIN`, `npm run build` fails at `vite: not found`, and no native Chromium-origin or iPhone Safari IndexedDB durability tests were possible. Preserve the source release candidate; do not deploy the offline React16 compatibility harness as the finished product.
