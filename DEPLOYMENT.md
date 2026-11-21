# PCI Stage08 deployment checklist

1. On a machine with npm registry access, run `npm install`; commit the genuine generated lockfile.
2. Run `npm run lint`, `npm run build`, `npm run test:repo`, and structural tests. Fix any React18 or Vite asset resolution errors before deployment. Production build not tested in the current environment.
3. Deploy only the `dist/` contents to HTTPS static hosting. Do not upload `reference/`, `offline-vendor/`, `dist-static/`, private backups or source PDF as public assets.
4. Confirm each of the 10 hash routes and back navigation on the actual hosted origin. Source asset fetches use relative paths to support GitHub Pages subpaths.
5. In modern Chrome, Safari iPhone and Firefox, verify IndexedDB v2 creates and persists records after reload; test create, read, update, delete, backup and restore; test import with duplicate ID and bad schema.
6. Use VoiceOver and keyboard-only navigation to inspect all form controls, dialogs, focus order, status indicators and 320/390px widths.
7. Document a retention and recovery policy for local-only IndexedDB; account sync, backend and AI features do not exist by default.
8. Remove the Stage08 production-readiness blockers in `PCI_ISSUES.json` only with test evidence and a migration note.

The offline build is an accessible development fallback, not certification of production readiness.
