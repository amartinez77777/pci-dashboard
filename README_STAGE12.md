# PCI Stage 12 · Actual application source

This is an extension of the complete Stage11 source repository, **not** a new prototype.

## Run

With actual project dependencies installed via an authentic npm installation:

```sh
npm install
npm run typecheck
npm run build
npm run dev
```

The shipped environment could not install Vite, and therefore `npm run build` was **BLOCKED** with `vite: not found`. No package-lock.json was fabricated. `npm run build:offline` creates an offline React16 compatibility preview only; it is **not** official React18/Vite production verification.

## Verification

```sh
npm run test:repo
npm run test:vault
npm run test:labs
npm run test:theater
npm run test:stage12
npm run test:assets
npm run test:vault:assets
npm run test:stage10:assets
npm run test:stage11:assets
npm run test:stage12:assets
python tests/browser_stage11_smoke.py
python tests/browser_stage12_smoke.py
```

Browser scripts run an **in-memory compatibility runtime with synthetic IndexedDB**. They are not native-origin durability, offline service-worker or physical iPhone Safari tests.

## Privacy

All user-created goals, scenes, reflections, observations, and scenario paths remain in local IndexedDB; user data never belongs in `public/data` or the canonical research ZIP. Versioned JSON export/import is available from Settings, **not encrypted by default**. Avoid saving material you would not want in an unencrypted local backup.

## Scope

Stage12 has 2 high-priority Theater UX repairs, a functional Feedback Lab and a generic playable engine for all 16 authored scenarios. Stage14 owns remaining manual-timing and cross-route unsaved-navigation issues; Stage15/16 own actual build and native browser release QA.
