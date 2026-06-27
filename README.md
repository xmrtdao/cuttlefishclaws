# DevGruGold — XMRT DAO Monorepo

Monorepo for the XMRT DAO ecosystem: agent infrastructure, relay services, and the cuttlefishclaws Tributary AI Campus SPA.

## Repositories

| Repo | Description | Live |
|------|-------------|------|
| `xmrtdao/cuttlefishclaws` | Tributary AI Campus — Vite + React SPA | [xmrtdao.github.io/cuttlefishclaws](https://xmrtdao.github.io/cuttlefishclaws/) |
| `xmrtdao/cashdapp` | CashDapp landing page | [xmrtdao.github.io/cashdapp](https://xmrtdao.github.io/cashdapp/) |

## Structure

```
DevGruGold/
├── cuttlefishclaws/       # Vite + React SPA (subtree — pushed to xmrtdao/cuttlefishclaws)
│   ├── src/
│   │   ├── components/    # React components (sections, agents, nav, hero, footer)
│   │   ├── lib/            # vizEngine.ts, trustGraphData.json, mockData.ts, types.ts
│   │   ├── pages/          # Route pages (CACPresale, VCPage)
│   │   └── App.tsx         # Root with React Router
│   └── dist/               # Production build (deployed to GH Pages)
├── relay/                  # Express relay server (port 8080)
│   ├── server.js           # Main relay with API routes, fleet chat, cron
│   ├── supervisor.mjs      # Service supervisor (pg, local-sb, Vite, tunnel, cron)
│   ├── tools/              # Utility scripts (send-cuttlefishclaws, etc.)
│   └── functions/          # Edge function handlers
├── supabase/               # Local Supabase replacement (local-sb)
│   ├── routes/             # PostgREST-compatible REST router
│   └── local-migrations/   # SQL migrations
├── cloudflare-workers/     # CF Worker scripts (api-gateway, etc.)
└── _*.mjs / _*.js          # One-off diagnostic and utility scripts
```

## cuttlefishclaws SPA

See [cuttlefishclaws/README.md](./cuttlefishclaws/README.md) for full details.

**Quick start:**
```bash
cd cuttlefishclaws
npm install
npm run dev     # Vite dev server on port 5173
npm run build   # Production build to dist/
```

Deploys to GitHub Pages on push to `master` branch via GH Actions.

## Relay

Express server on port 8080 serving API routes, fleet chat, and proxying to local-sb.

```bash
cd relay
npm install
node server.js
```

## Branches

- `work-branch` — active development
- `main` — stable, merged from work-branch
- `cuttlefish/main` — cuttlefishclaws SPA subtree (pushed to xmrtdao/cuttlefishclaws)
- `cuttlefish/master` — GH Pages deploy branch (auto-deploys on push)
