# PCI Stage 12 changelog

- Extended **actual Stage11 source**, preserved all 10 routes, existing research/data assets, and original permanent IDs.
- Theater: template/phase-specific default and nonvisual guidance; private scene data rehydrated from stable `scene_id` and displayed safely as React text at the appropriate phase; missing scene fallback; corrected template selection button.
- Feedback Lab: working private goals, action/prediction/observation separation, review dates, multiple feedback cycles, revision history, linked sources/beliefs/rehearsals, deletion and event deduplication.
- Scenario Simulator: all 16 real authored scenarios validated for valid graph edges, two choices per decision, reachability and non-identical consequences; progress, backtracking, safe exit, completion and saved history.
- Added `learning-events.ts` transactional idempotency helper reusing inherited IndexedDB v2 stores.
- Added schema contracts, test suites, source checks and mobile-responsive styles.
- Deferred timing and global hash dirty-navigation defects to Stage14 by explicit tickets.
- No modifications to canonical research dossiers, copyrighted source PDFs, public rehearsal datasets, or pre-existing user records.
