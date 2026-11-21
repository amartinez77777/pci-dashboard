# PCI Stage 05 data and migration contract

- `schema_version=1.0.0` unchanged; `research_data_version=1.3.0` inherited; `canonical_pack_version=1.0.0` first unified release.
- Every inherited record ID and original object value is retained. Stage 05 **appends** issue IDs `PCI-ISS-048` to `PCI-ISS-055`, never overwrites a previous ID.
- `PCI_ID_REGISTRY.json` has 1,676 IDs; `PCI_RECORD_PROVENANCE.json` records each original package member hash and canonical JSON value hash.
- No duplicate retirement, redirects, or tombstones were necessary. If an approved future merge retires an ID, add `PCI_ID_REDIRECTS.json` mapping old->new and retain the historical original in provenance. Do not renumber IDs.
- Chapter object includes inherited section arrays with varying shapes. `data/PCI_SECTIONS.json` preserves actual registered source sections, while `indexes/PCI_SECTIONS_APP_VIEW.json` provides normalized, non-authoritative UI geometry. The view does not alter original chapter records.
- UI / exercise design should consume the canonical collection and typed interfaces. Search documents, themes and cross-links are derived and may be rebuilt without changing permanent IDs; they are not part of the edition's source evidence.
- `learning/` stores Stage03 scenario/quiz *candidates* with noncanonical candidate keys. Stage06 must issue stable IDs only after accepted exercise design; do not treat candidate keys as permanent existing records.
- User-private data is not part of this public research ZIP. Stage06 needs a separate IndexedDB database with explicit versioned export/import and no incorporation into static assets.
