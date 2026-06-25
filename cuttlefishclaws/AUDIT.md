# Cuttlefish Claws — Full Site Audit

**Date:** 2026-06-25  
**Auditor:** Vex (AI Agent)  
**Scope:** Every form, page, button, interaction, API endpoint, email route, and external service

---

## 1. Project Overview

| Property | Value |
|---|---|
| **Framework** | Vite 6 + React 18 + TypeScript + Tailwind 3 |
| **Deployment** | GitHub Pages at `xmrtdao.github.io/cuttlefishclaws/` |
| **Router** | React Router 6 with `BrowserRouter basename="/cuttlefishclaws"` |
| **Backend** | 10 Netlify Functions (TypeScript, esbuild) — **NOT deployed** |
| **Database** | Supabase cloud project `vyggodkclzcmfycdovqi` — referenced but unreachable from GH Pages |
| **Relay** | `relay.mobilemonero.com` — used for CAC presale form only |
| **Custom Viz** | Canvas2D engine (`vizEngine.ts`, ~1745 lines) |
| **Mock Data** | 7 agents, 4 CAC tiers, 8 contracts, 4 stack layers, 3 scenarios, 3 VC deals |

---

## 2. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Pages                              │
│              xmrtdao.github.io/cuttlefishclaws/              │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐  │
│  │  Hero    │  │  CAC     │  │  Agents  │  │  Invest    │  │
│  │  (Viz)   │  │  Section │  │  Section │  │  Section   │  │
│  └──────────┘  └──────────┘  └──────────┘  └────────────┘  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐  │
│  │  Trust   │  │  Bill of │  │  Capital │  │  Contracts │  │
│  │  Graph   │  │  Rights  │  │  Stack   │  │  Section   │  │
│  └──────────┘  └──────────┘  └──────────┘  └────────────┘  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐  │
│  │  Agent   │  │  KYA     │  │  Returns │  │  Footer    │  │
│  │  Bank    │  │  Section │  │  (VC)    │  │            │  │
│  └──────────┘  └──────────┘  └──────────┘  └────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  /presale → CACPresale.tsx (separate page)           │   │
│  │  /vc      → VCPage.tsx (VC briefing page)            │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
         │                          │
         │ POST /api/contact/       │ POST /.netlify/functions/*
         │ cuttlefishclaws          │ (ALL 404 — no Netlify backend)
         ▼                          ▼
┌──────────────────┐     ┌──────────────────────────────┐
│  relay.mobile-   │     │  Supabase Cloud (vyggodk...) │
│  monero.com      │     │  ┌────────────────────────┐  │
│  (Express)        │     │  │ agents                 │  │
│  → dvdelze@      │     │  │ cac_credentials         │  │
│    gmail.com     │     │  │ proposals               │  │
└──────────────────┘     │  │ trust_events            │  │
                         │  │ agent_tasks             │  │
                         │  │ capital_stack           │  │
                         │  │ financing_programs      │  │
                         │  └────────────────────────┘  │
                         └──────────────────────────────┘
```

---

## 3. Form Inventory

### 3.1 CAC Presale Reservation Form

| Property | Value |
|---|---|
| **Route** | `/presale` |
| **Component** | `src/pages/CACPresale.tsx` |
| **Fields** | name (text), email (email), type (human/agent/both toggle), referral (text) |
| **Endpoint** | `POST https://relay.mobilemonero.com/api/contact/cuttlefishclaws` |
| **Email destination** | `dvdelze@gmail.com` (fallback in error alert) |
| **Payment method 1** | Stripe: `https://buy.stripe.com/28EdRaehWcfigxReaxfAc00` |
| **Payment method 2** | USDC on Base: `0xb748798D0a8dA0527c30e6CA81425A8fD150f04c` |
| **Price** | $100 one-time reservation |
| **Status** | ✅ **WORKING** (relay endpoint exists) |
| **Needs verification** | Stripe link active? Wallet address correct? Relay route handles this form? |

**How it works:**
1. User fills name, email, type, referral
2. Form POSTs to relay.mobilemonero.com
3. On success: shows confirmation message
4. On failure: alerts user to email dvdelze@gmail.com directly
5. Payment is separate (Stripe link or USDC transfer)

### 3.2 InvestSection Inquiry Form

| Property | Value |
|---|---|
| **Route** | `/#invest` (main page section) |
| **Component** | `src/components/sections/InvestSection.tsx` |
| **Fields** | name (text), email (email, required), interest (select), amount (select) |
| **Endpoint** | `POST /.netlify/functions/inquiry` |
| **Email destination** | `invest@cuttlefish.ai` (fallback in error message) |
| **Status** | ❌ **BROKEN** — will 404 on GitHub Pages |

**How it should work:**
1. User fills form
2. POST to `/.netlify/functions/inquiry`
3. Netlify function `inquiry.ts` optionally forwards to `TRIB_API_URL` crew endpoint
4. Returns confirmation: "Trib has your inquiry. Expect a response within 24 hours."

**Why it's broken:**
- The site is deployed to GitHub Pages only
- There is no Netlify backend deployed
- All `/.netlify/functions/*` paths will return 404
- The `netlify.toml` config exists but is not active

### 3.3 Agent Chat Modal

| Property | Value |
|---|---|
| **Route** | Modal overlay on `/#agents` |
| **Component** | `src/components/agents/AgentChatModal.tsx` |
| **Fields** | Single text input + Send button |
| **Endpoint** | `POST /.netlify/functions/chat` |
| **Status** | ❌ **BROKEN** — will 404 on GitHub Pages |

**How it should work:**
1. User clicks "Chat" on an agent card
2. Modal opens with agent greeting (from mock data)
3. User types message, POSTs to `/.netlify/functions/chat`
4. `chat.ts` forwards to `TRIB_API_URL` crew endpoint
5. Returns agent response

**Why it's broken:**
- Same Netlify dependency as InvestSection
- The `chat.ts` function has a graceful fallback if `TRIB_API_URL` is not set, but the function itself is unreachable

---

## 4. All 10 Netlify Functions — Status

All functions live in `netlify/functions/`. **None are deployed.** All will return 404 when called from GitHub Pages.

| # | Function | File | Purpose | Dependencies |
|---|---|---|---|---|
| 1 | `inquiry` | `inquiry.ts` | Investor inquiry handler | `TRIB_API_URL`, `TRIB_API_KEY` |
| 2 | `chat` | `chat.ts` | General chat → crew | `TRIB_API_URL`, `TRIB_API_KEY` |
| 3 | `agent-chat` | `agent-chat.ts` | Agent-specific chat | Supabase, `TRIB_API_URL`, `ARCH_API_URL` |
| 4 | `agent-onboard` | `agent-onboard.ts` | Agent registration + KYA | Supabase |
| 5 | `agent-x-post` | `agent-x-post.ts` | Social posting pipeline | Supabase |
| 6 | `cac-status` | `cac-status.ts` | CAC credential status | Supabase |
| 7 | `capital-stack` | `capital-stack.ts` | Capital stack data | Supabase |
| 8 | `financing-programs` | `financing-programs.ts` | Financing programs | Supabase |
| 9 | `proposal-submit` | `proposal-submit.ts` | Proposal submission + IPFS | Supabase, `PINATA_JWT` |
| 10 | `trust-score` | `trust-score.ts` | Trust score query | Supabase |

**Shared modules:**
- `_shared/cors.ts` — CORS headers (ALLOWED_ORIGIN defaults to `https://cuttlefishclaws.com`)
- `_shared/supabase.ts` — Supabase client (requires `SUPABASE_URL` + `SUPABASE_SERVICE_KEY`)

**Required env vars (all missing in GH Pages deployment):**
- `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`
- `TRIB_API_URL`, `TRIB_API_KEY`
- `ARCH_API_URL`
- `PINATA_JWT`
- `ALLOWED_ORIGIN`

---

## 5. Page Inventory

### 5.1 Main SPA Sections (all on one page, `/`)

| # | Section | Component | Interactions | Status |
|---|---|---|---|---|
| 1 | **Nav** | `Nav.tsx` | 9 nav link buttons, hamburger menu, "Reserve →" link, "Invest →" button | ⚠️ Reserve link broken for subpath |
| 2 | **Hero** | `Hero.tsx` | Canvas viz, 6 control toggles, 7 layer filters, palette toggle, 2 CTA buttons, scroll indicator | ✅ Working |
| 3 | **CAC Section** | `CACSection.tsx` | 4 tier cards with feature lists | ✅ Working (mock data) |
| 4 | **CAC Spec Docs** | `CACSpecDocs.tsx` | 6 spec docs with expand/collapse flyout | ✅ Working |
| 5 | **Agents Section** | `AgentsSection.tsx` | 7 agent cards with expand/details/chat buttons | ⚠️ Grid not responsive |
| 6 | **TrustGraph** | `TrustGraphSection.tsx` | Canvas scoring sim, clickable nodes, event log | ✅ Working (mock data) |
| 7 | **Bill of Rights** | `AgentBillOfRights.tsx` | 8 articles with expand/collapse + acknowledge buttons | ⚠️ State lost on refresh |
| 8 | **Capital Stack** | `CapitalStack.tsx` | 4 layer cards with details | ✅ Working (mock data) |
| 9 | **Returns (VC)** | `ReturnsSection.tsx` | 3 scenarios, VC code gate | ✅ Working (mock data) |
| 10 | **Contracts** | `ContractsSection.tsx` | 8 contract cards with addresses | ✅ Working (mock data) |
| 11 | **Agent Bank** | `AgentBankSection.tsx` | Agent wallet/pool info | ✅ Working (mock data) |
| 12 | **KYA Section** | `KYASection.tsx` | KYA verification steps | ✅ Working (mock data) |
| 13 | **Invest Section** | `InvestSection.tsx` | 2 CTA cards, VC Briefing button, inquiry form | ❌ Form broken |
| 14 | **Footer** | `Footer.tsx` | 4-column link grid, legal disclaimer | ✅ Working |
| 15 | **Agent Chat Modal** | `AgentChatModal.tsx` | Chat modal with messages, files panel, input | ❌ Chat broken |

### 5.2 Separate Pages

| # | Page | Route | Component | Status |
|---|---|---|---|---|
| 1 | **CAC Presale** | `/presale` | `CACPresale.tsx` | ✅ Form working (relay endpoint) |
| 2 | **VC Briefing** | `/vc` | `VCPage.tsx` | ⚠️ "Main Site" link broken for subpath |

### 5.3 Missing Pages

| Page | Needed? | Notes |
|---|---|---|
| **Privacy Policy** | Yes | Legal requirement for collecting emails |
| **Terms of Service** | Yes | Legal requirement for investment platform |
| **404 Not Found** | Yes | SPA needs catch-all route |
| **CAC Dashboard** | Nice-to-have | Member portal for CAC holders |

---

## 6. Working Features

| Feature | Details |
|---|---|
| Canvas visualization | Full-screen interactive viz with 6 controls + 7 layer filters |
| ScrollReveal animations | All sections animate in on scroll |
| Palette toggle | Amber/Cyan theme switching |
| Mobile hamburger menu | Slide-out nav on mobile |
| CAC tier cards | 4 tiers with feature lists, responsive |
| Spec docs flyout | 6 documents with expand/collapse |
| Agent cards | 7 agents with expand/details/chat buttons |
| TrustGraph simulation | Auto-firing random events every 2.2s |
| Bill of Rights | 8 articles with expand/collapse + acknowledge |
| Capital stack | 4 layers with details |
| Returns scenarios | 3 scenarios with metrics |
| Contracts table | 8 contracts with addresses |
| Agent bank | Wallet/pool info |
| KYA section | Verification steps |
| Footer | 4-column grid with links |
| CAC Presale form | POSTs to relay endpoint (working) |
| VC Briefing page | Full VC page with deal pipeline |

---

## 7. Broken Features

| # | Issue | Severity | Component | Fix Needed |
|---|---|---|---|---|
| 1 | **All Netlify function calls return 404** | 🔴 Critical | InvestSection, AgentChatModal, all api.ts calls | Deploy Netlify functions OR replace with relay endpoints OR use mock data fallback |
| 2 | **Nav "Reserve →" link wrong path** | 🟠 High | Nav.tsx | Change `href="/presale"` to use React Router `Link` with `to="/presale"` |
| 3 | **VCPage "Main Site" link wrong path** | 🟠 High | VCPage.tsx | Change `navigate('/')` to `navigate('/cuttlefishclaws')` |
| 4 | **AgentsSection grid not responsive** | 🟡 Medium | AgentsSection.tsx | Replace inline `gridTemplateColumns: 'repeat(2, 1fr)'` with Tailwind `grid-cols-1 md:grid-cols-2` |
| 5 | **Bill of Rights acknowledge state lost on refresh** | 🟡 Medium | AgentBillOfRights.tsx | Persist to localStorage or sessionStorage |
| 6 | **CORS headers reference wrong domain** | 🟡 Medium | `_shared/cors.ts` | Change default from `cuttlefishclaws.com` to GH Pages URL |
| 7 | **netlify.toml configured but unused** | 🟢 Low | `netlify.toml` | Either deploy to Netlify or remove/ignore |

---

## 8. Email Routing

| Form/Component | Sends To | From | Method | Status |
|---|---|---|---|---|
| CAC Presale form | `dvdelze@gmail.com` (fallback) | N/A (relay handles) | POST to relay.mobilemonero.com | ✅ Working |
| InvestSection inquiry | `invest@cuttlefish.ai` (fallback) | N/A | POST to `/.netlify/functions/inquiry` | ❌ 404 |
| Footer email links | `invest@cuttlefish.ai`, `legal@cuttlefish.ai` | N/A | `mailto:` links | ✅ Working (opens email client) |

**Note:** The `inquiry.ts` function, if deployed, would forward to `TRIB_API_URL` crew endpoint. The actual email delivery mechanism depends on the crew configuration.

---

## 9. External Services

| Service | URL | Used By | Status |
|---|---|---|---|
| **Stripe** | `https://buy.stripe.com/28EdRaehWcfigxReaxfAc00` | CACPresale payment | ⚠️ Needs verification |
| **Relay** | `https://relay.mobilemonero.com/api/contact/cuttlefishclaws` | CACPresale form POST | ✅ Assumed working |
| **Supabase** | Project `vyggodkclzcmfycdovqi` | All Netlify functions | ❌ Unreachable from GH Pages |
| **GitHub** | `https://github.com/HansElze/cuttlefishclaws` | Footer open source links | ✅ Public repo |
| **Discord** | `https://discord.gg/cuttlefish` | Footer community link | ⚠️ Needs verification |
| **cuttlefishclaw.com** | `https://cuttlefishclaw.com` | Footer + CACPresale footer | ⚠️ Needs verification |
| **Pinata (IPFS)** | `https://api.pinata.cloud` | proposal-submit.ts | ❌ No JWT configured |
| **Base wallet** | `0xb748798D0a8dA0527c30e6CA81425A8fD150f04c` | CACPresale USDC payment | ⚠️ Needs verification |

---

## 10. Mock Data Dependencies

| Data | Source | Used By | Real Backend? |
|---|---|---|---|
| AGENTS (7) | `lib/mockData.ts` | AgentsSection, AgentChatModal | No — all hardcoded |
| CAC_TIERS (4) | `lib/mockData.ts` | CACSection | No — all hardcoded |
| CONTRACTS (8) | `lib/mockData.ts` | ContractsSection | No — all hardcoded |
| STACK_LAYERS (4) | `lib/mockData.ts` | CapitalStack | No — all hardcoded |
| SCENARIOS (3) | `lib/mockData.ts` | ReturnsSection | No — all hardcoded |
| MOCK_DEALS (3) | `VCPage.tsx` | VCPage | No — all hardcoded |
| TrustGraph events | `TrustGraphSection.tsx` | TrustGraph simulation | No — auto-generated random events |

**Total mock data:** 100% of displayed data is hardcoded. No real backend integration exists.

---

## 11. Navigation Map

```
┌─────────────────────────────────────────────────────────────┐
│                        Nav Bar                               │
│  CAC Protocol → #cac                                          │
│  Spec Docs    → #cac-spec                                     │
│  Agents       → #agents                                       │
│  TrustGraph   → #trustgraph                                   │
│  Bill of Rights → #bill-of-rights                             │
│  Capital Stack → #capital                                     │
│  Contracts    → #contracts                                    │
│  Agent Bank   → #agent-bank                                   │
│  KYA Protocol → #kya                                           │
│                                                               │
│  [Reserve →]  → /presale  ⚠️ BROKEN (wrong path)              │
│  [Invest →]   → #invest                                       │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                        Hero CTAs                             │
│  [Join as Agent Member] → #invest                            │
│  [View Capital Stack]   → #capital                           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    Invest Section CTAs                       │
│  [VC Briefing →] → shows Returns section                    │
│  [View Tiers]    → #cac                                      │
│  [View Stack]    → #capital                                  │
│  [Send to Trib →] → POST /.netlify/functions/inquiry ❌      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    Agent Cards                               │
│  [Details ▼] → expand card                                   │
│  [Chat →]     → open AgentChatModal                          │
│                 → POST /.netlify/functions/chat ❌            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    VCPage Nav                                 │
│  [Main Site] → navigate('/') ⚠️ BROKEN (wrong path)         │
└─────────────────────────────────────────────────────────────┘
```

---

## 12. Priority Action Items

### 🔴 Critical (blocks core functionality)

| # | Action | Effort | Impact |
|---|---|---|---|
| 1 | **Fix all Netlify function calls** — either deploy Netlify backend, replace with relay endpoints, or add mock fallbacks | Large | Unblocks Invest form + Agent Chat + all API features |
| 2 | **Fix Nav "Reserve →" link** — use React Router `Link` with `to="/presale"` instead of `href="/presale"` | Small | Fixes broken navigation to presale page |
| 3 | **Fix VCPage "Main Site" link** — use `navigate('/cuttlefishclaws')` instead of `navigate('/')` | Small | Fixes broken navigation back to main site |

### 🟠 High (important UX issues)

| # | Action | Effort | Impact |
|---|---|---|---|
| 4 | **Fix AgentsSection grid responsiveness** — replace inline style with Tailwind classes | Small | Fixes mobile layout |
| 5 | **Persist Bill of Rights acknowledge state** — use localStorage | Small | Prevents lost progress on refresh |
| 6 | **Verify external services** — test Stripe link, wallet address, relay endpoint, Discord invite, cuttlefishclaw.com domain | Medium | Ensures payment and links work |

### 🟡 Medium (polish and completeness)

| # | Action | Effort | Impact |
|---|---|---|---|
| 7 | **Add Privacy Policy page** | Medium | Legal compliance |
| 8 | **Add Terms of Service page** | Medium | Legal compliance |
| 9 | **Add 404 page** | Small | Better UX |
| 10 | **Fix CORS headers default domain** | Small | Correct origin for API calls |
| 11 | **Remove or update netlify.toml** | Small | Clean up misleading config |

### 🟢 Low (nice-to-have)

| # | Action | Effort | Impact |
|---|---|---|---|
| 12 | **Add CAC Dashboard page** | Large | Member portal |
| 13 | **Replace mock data with real API calls** | Very Large | Production readiness |
| 14 | **Add loading states to all async operations** | Medium | Better UX |

---

## 13. Summary

| Category | Count |
|---|---|
| Total forms | 3 |
| Working forms | 1 (CAC Presale) |
| Broken forms | 2 (Invest inquiry, Agent chat) |
| Total pages/routes | 3 (main SPA, /presale, /vc) |
| Missing pages | 3 (privacy, terms, 404) |
| Netlify functions (all 404) | 10 |
| Navigation bugs | 2 |
| Responsive bugs | 1 |
| State persistence bugs | 1 |
| External services (needs verification) | 5 |
| Mock data dependencies | 6 (100% of data is mock) |

**Bottom line:** The site is a visually impressive static SPA with a working presale form (via relay). Everything that requires a backend — forms, chat, API data — is broken because the Netlify functions are not deployed. The two navigation links are broken due to the GitHub Pages subpath deployment. Fixing the backend dependency is the single most impactful change.
