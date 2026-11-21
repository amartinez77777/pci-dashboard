# PCI v1.1 source enhancement change log

- **Personal intelligence:** Added deterministic source-aware recommendation engine for user-chosen goals, due reviews, optional practice and incomplete feedback, with reason codes and record IDs. No new scoring or remote services.
- **Command Center:** Reorganized into Continue, Recommended, Activity, Goals/Follow-ups, Learning, Recent history, and a clearly optional five-part connected journey. Live counts come from local private stores only.
- **Cross-module ID links:** Added explicit goal/belief/scene/session/experiment/outcome associations and direct module routes. No source record or relationship was inferred or re-IDed. Academy optional rehearsal link opens existing authored template; concept-linked conditioning surfaces only when canonical concept IDs match.
- **Privacy/Archive:** The Archive now includes private scene records and memoized local search; sensitive entries are not exposed in home activity previews. No schema migration.
- **Accessibility/mobile:** focused visual sizing on home, 44px action controls and reduced-motion preference.
- **Integrity:** All 249 originally attached protected files pinned to immutable SHA-256 fingerprints, 1,799 registered IDs preserved; no copyrighted PDF or private records bundled.
- **Gates:** 139/139 Node tests, 82/82 in-memory Chromium checks, 15/15 frozen-input source checks. Official Vite and native IndexedDB Safari durability remain blocked/not tested.
