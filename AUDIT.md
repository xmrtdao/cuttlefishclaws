# CuttlefishClaws SPA — Comprehensive Audit

**Date:** 2026-06-25
**SPA:** React 18 + Vite 6 + Tailwind 3 + React Router 6
**Deployed at:** `xmrtdao.github.io/cuttlefishclaws/` (GH Pages) + `relay.mobilemonero.com/cuttlefishclaws/` (relay Express)
**Backend:** relay Express at `relay.mobilemonero.com` (via CF tunnel)
**Source:** `cuttlefishclaws/` directory in DevGruGold monorepo

---

## 1. Project Overview

| Property | Value |
|---|---|
| **Framework** | Vite 6 + React 18 + TypeScript + Tailwind 3 |
| **Deployment** | GitHub Pages at `xmrtdao.github.io/cuttlefishclaws/` |
| **Router** | React Router 6 with `BrowserRouter basename="/cuttlefishclaws"` |
| **Backend** | relay Express at `relay.mobilemonero.com` (via CF tunnel) |
| **Legacy Backend** | 10 Netlify Functions (TypeScript, esbuild) — **NOT deployed, replaced by relay** |
| **Database** | Supabase cloud project `vyggodkclzcmfycdovqi` — referenced but unreachable |
| **Relay** | `relay.mobilemonero.com` — serves SPA + all API endpoints |
| **Custom Viz** | Canvas2D engine (`vizEngine.ts`, ~1745 lines) |
| **Mock Data** | 7 agents, 4 CAC tiers, 8 contracts, 4 stack layers, 3 scenarios, 3 VC deals |

---

## 2. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Browser (GH Pages)                        │
│  xmrtdao.github.io/cuttlefishclaws/                          │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  React SPA (Vite build → dist/)                       │   │
│  │  - App.tsx (main layout, section ordering)             │   │
│  │  - Nav.tsx (9 anchor links + 2 CTAs)                  │   │
│  │  - Hero.tsx (Canvas2D viz + 2 CTAs)                   │   │
│  │  - 11 section components                               │   │
│  │  - 2 pages (VCPage, CACPresale)                        │   │
│  │  - AgentChatModal                                      │   │
│  │  - api.ts (8 endpoints → relay)                        │   │
│  └──────────────────────────────────────────────────────┘   │
│                           │                                  │
│                    POST/GET requests                          │
│                           │                                  │
│                           ▼                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  relay.mobilemonero.com (CF tunnel → local Express)   │   │
│  │                                                       │   │
│  │  /api/contact/cuttlefishclaws        → email (Resend) │   │
│  │  /api/contact/cuttlefishclaws/inquiry → email (Resend)│   │
│  │  /api/contact/cuttlefishclaws/chat    → email (Resend)│   │
│  │  /api/cuttlefishclaws/* (GET)         → email (Resend) │   │
│  │  /api/cuttlefishclaws/* (POST)        → email (Resend) │   │
│  │                                                       │   │
│  │  SPA served at /cuttlefishclaws/ from dist/           │   │
│  └──────────────────────────────────────────────────────┘   │
│                           │                                  │
│                           ▼                                  │
│              ┌─────────────────────────────────────┐         │
│              │  Resend API                          │         │
│              │  → dvdelze@gmail.com                 │         │
│              │  → xmrtnet@gmail.com                 │         │
│              │  From: david@31harbor.com            │         │
│              │  Key: RESEND_31HARBOR_API_KEY        │         │
│              └─────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────┘
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
| **Relay handler** | `server.js:7195-7220` — sends email to `dvdelze@gmail.com` + `xmrtnet@gmail.com` from `david@31harbor.com` via Resend |
| **Payment method 1** | Stripe: `https://buy.stripe.com/28EdRaehWcfigxReaxfAc00` |
| **Payment method 2** | USDC on Base: `0xb748798D0a8dA0527c30e6CA81425A8fD150f04c` |
| **Price** | $100 one-time reservation |
| **Status** | ✅ **WORKING** — relay endpoint exists and sends email |
| **Needs verification** | Stripe link active? Wallet address correct? |

**How it works:**
1. User fills name, email, type, referral
2. Form POSTs to relay.mobilemonero.com
3. Relay sends email notification to dvdelze@gmail.com + xmrtnet@gmail.com
4. On success: shows confirmation message
5. On failure: alerts user to email dvdelze@gmail.com directly
6. Payment is separate (Stripe link or USDC transfer)

### 3.2 InvestSection Inquiry Form

| Property | Value |
|---|---|
| **Route** | `/#invest` (main page section) |
| **Component** | `src/components/sections/InvestSection.tsx` |
| **Fields** | name (text), email (email, required), interest (select), amount (select) |
| **Endpoint** | `POST https://relay.mobilemonero.com/api/contact/cuttlefishclaws/inquiry` |
| **Relay handler** | `server.js:7222-7245` — sends email to `dvdelze@gmail.com` + `xmrtnet@gmail.com` from `david@31harbor.com` via Resend |
| **Email destination** | `invest@cuttlefish.ai` (fallback in error message) |
| **Status** | ✅ **WORKING** — relay endpoint exists and sends email |

**How it works:**
1. User fills name, email, interest type, investment range
2. Form POSTs to relay.mobilemonero.com
3. Relay sends email notification to dvdelze@gmail.com + xmrtnet@gmail.com
4. On success: shows "INQUIRY RECEIVED" confirmation
5. On failure: shows "Email invest@cuttlefish.ai directly" fallback

### 3.3 Agent Chat Modal

| Property | Value |
|---|---|
| **Route** | Modal overlay on `/#agents` |
| **Component** | `src/components/agents/AgentChatModal.tsx` |
| **Fields** | Single text input + Send button |
| **Endpoint** | `POST https://relay.mobilemonero.com/api/contact/cuttlefishclaws/chat` |
| **Relay handler** | `server.js:7247-7275` — sends email to `dvdelze@gmail.com` + `xmrtnet@gmail.com` from `david@31harbor.com` via Resend; returns fake agent response |
| **Status** | ✅ **WORKING** — relay endpoint exists, sends email, returns fake response |

**How it works:**
1. User clicks "Chat" on an agent card
2. Modal opens with agent greeting (from mock data)
3. User types message, POSTs to relay.mobilemonero.com
4. Relay sends email notification + returns a hardcoded fake response
5. Fake response shown in chat UI

**Critical caveat:** The chat endpoint does NOT actually process the message through any AI. It returns a canned response. The real chat functionality would need an AI backend.

---

## 4. All 8 api.ts Endpoints — Status

All API calls in `src/lib/api.ts` POST/GET to `relay.mobilemonero.com/api/cuttlefishclaws/*`. The relay handles these via catch-all routes (`server.js:7277-7305`) that **send an email notification and return a stub response** — no real data processing occurs.

| # | Function | Endpoint | Method | What It Should Do | What It Actually Does |
|---|---|---|---|---|---|
| 1 | `onboardAgent` | `/api/cuttlefishclaws/onboard` | POST | Register agent + KYA | Sends email with payload; returns `{success: true, note: "..."}` |
| 2 | `submitProposal` | `/api/cuttlefishclaws/proposal` | POST | Submit proposal + IPFS | Sends email with payload; returns `{success: true, note: "..."}` |
| 3 | `getCACStatus` | `/api/cuttlefishclaws/cac-status` | GET | Return CAC credential status | Sends email with query params; returns `{success: true, note: "..."}` |
| 4 | `getCapitalStack` | `/api/cuttlefishclaws/capital-stack` | GET | Return capital stack data | Sends email with query params; returns `{success: true, note: "..."}` |
| 5 | `getFinancingPrograms` | `/api/cuttlefishclaws/financing-programs` | GET | Return financing programs | Sends email with query params; returns `{success: true, note: "..."}` |
| 6 | `getTrustScore` | `/api/cuttlefishclaws/trust-score` | GET | Return trust score | Sends email with query params; returns `{success: true, note: "..."}` |
| 7 | `getAgentChat` | `/api/cuttlefishclaws/agent-chat` | POST | Agent-specific chat | Sends email with payload; returns `{success: true, note: "..."}` |
| 8 | `postToX` | `/api/cuttlefishclaws/x-post` | POST | Social posting pipeline | Sends email with payload; returns `{success: true, note: "..."}` |

**Critical finding:** All 8 api.ts endpoints are **email notification stubs**. The relay catch-all handler (`server.js:7277-7305`) does not implement any of the actual business logic (agent onboarding, proposal submission, CAC credential management, capital stack data, trust scoring, social posting). The frontend defines typed return values (`OnboardResult`, `ProposalResult`, etc.) but the relay never returns those shapes — it returns `{success: true, note: "Email notification sent"}`.

**The 10 legacy Netlify functions** (`netlify/functions/*.ts`) contain the actual business logic (Supabase queries, IPFS uploads, crew API calls) but are **not deployed** and are **not called** by the current frontend. They exist as dead code.

**To make these features work, each endpoint needs a real implementation in relay/server.js that:**
- Queries the local Postgres database (or Supabase)
- Processes the data (agent registration, proposal storage, trust scoring, etc.)
- Returns proper typed responses matching the frontend's TypeScript interfaces

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
| 13 | **Invest Section** | `InvestSection.tsx` | 2 CTA cards, VC Briefing button, inquiry form | ✅ Form working (relay endpoint) |
| 14 | **Footer** | `Footer.tsx` | 4-column link grid, legal disclaimer | ✅ Working |
| 15 | **Agent Chat Modal** | `AgentChatModal.tsx` | Chat modal with messages, files panel, input | ✅ Form working (relay endpoint, fake response) |

### 5.2 Separate Pages

| # | Page | Route | Component | Status |
|---|---|---|---|---|
| 1 | **CAC Presale** | `/presale` | `CACPresale.tsx` | ✅ Form working (relay endpoint) |
| 2 | **VC Briefing** | `/vc` | `VCPage.tsx` | ⚠️ "Main Site" link broken for subpath; 5 no-op buttons |

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
| **CAC Presale form** | POSTs to relay endpoint (working, sends email) |
| **InvestSection inquiry form** | POSTs to relay endpoint (working, sends email) |
| **Agent Chat form** | POSTs to relay endpoint (working, sends email, returns fake response) |
| VC Briefing page | Full VC page with deal pipeline |

---

## 7. Issues & Broken Features

| # | Issue | Severity | Component | Fix Needed |
|---|---|---|---|---|
| 1 | **All 8 api.ts endpoints return email stubs, not real data** | 🔴 Critical | `api.ts` + relay `server.js:7277-7305` | Implement real business logic in relay for each endpoint (agent onboarding, proposals, CAC status, capital stack, financing, trust score, agent chat, X posting) |
| 2 | **Agent Chat returns fake canned response** | 🟠 High | relay `server.js:7247-7275` | Wire chat to an AI backend (Ollama/Eliza) instead of hardcoded reply |
| 3 | **Nav "Reserve →" link wrong path** | 🟠 High | `Nav.tsx` | Change `href="/presale"` to use React Router `Link` with `to="/presale"` |
| 4 | **VCPage "Main Site" link wrong path** | 🟠 High | `VCPage.tsx` | Change `navigate('/')` to `navigate('/cuttlefishclaws')` |
| 5 | **VCPage has 5 no-op buttons** | 🟡 Medium | `VCPage.tsx` | 5 buttons (`Export Data`, `Schedule Review`, `Request Docs`, `View Allocations`, `Download Report`) have empty `onClick` handlers — wire to real actions or remove |
| 6 | **AgentsSection grid not responsive** | 🟡 Medium | `AgentsSection.tsx` | Replace inline `gridTemplateColumns: 'repeat(2, 1fr)'` with Tailwind `grid-cols-1 md:grid-cols-2` |
| 7 | **Bill of Rights acknowledge state lost on refresh** | 🟡 Medium | `AgentBillOfRights.tsx` | Persist to localStorage or sessionStorage |
| 8 | **10 legacy Netlify functions are dead code** | 🟢 Low | `netlify/functions/*.ts` | Either deploy to Netlify, port logic to relay endpoints, or remove |
| 9 | **netlify.toml configured but unused** | 🟢 Low | `netlify.toml` | Either deploy to Netlify or remove/ignore |

---

## 8. Email Routing

| Form/Component | Sends To | From | Via | Status |
|---|---|---|---|---|
| CAC Presale form | `dvdelze@gmail.com` + `xmrtnet@gmail.com` | `david@31harbor.com` | relay → Resend | ✅ Working |
| InvestSection inquiry | `dvdelze@gmail.com` + `xmrtnet@gmail.com` | `david@31harbor.com` | relay → Resend | ✅ Working |
| Agent Chat | `dvdelze@gmail.com` + `xmrtnet@gmail.com` | `david@31harbor.com` | relay → Resend | ✅ Working |
| All 8 api.ts endpoints | `dvdelze@gmail.com` + `xmrtnet@gmail.com` | `david@31harbor.com` | relay → Resend | ✅ Working (but returns stubs) |
| Footer email links | `invest@cuttlefish.ai`, `legal@cuttlefish.ai` | N/A | `mailto:` links | ✅ Working (opens email client) |

**Key finding:** Every form and API call sends email to the same two recipients (`dvdelze@gmail.com` + `xmrtnet@gmail.com`) from the same sender (`david@31harbor.com`) using the same Resend API key (`RESEND_31HARBOR_API_KEY`). There is no differentiation — a CAC presale reservation, an investor inquiry, an agent chat message, and an agent onboarding request all produce the same email notification.

---

## 9. External Services

| Service | URL | Used By | Status |
|---|---|---|---|
| **Stripe** | `https://buy.stripe.com/28EdRaehWcfigxReaxfAc00` | CACPresale payment | ⚠️ Needs verification |
| **Relay** | `https://relay.mobilemonero.com` | All forms + API calls | ✅ Working (email stubs) |
| **Resend** | Via relay | All email delivery | ✅ Working (RESEND_31HARBOR_API_KEY) |
| **GitHub** | `https://github.com/HansElze/cuttlefishclaws` | Footer open source links | ✅ Public repo |
| **Discord** | `https://discord.gg/cuttlefish` | Footer community link | ⚠️ Needs verification |
| **cuttlefishclaw.com** | `https://cuttlefishclaw.com` | Footer + CACPresale footer | ⚠️ Needs verification |
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
│  [Send to Trib →] → POST relay.mobilemonero.com ✅           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    Agent Cards                               │
│  [Details ▼] → expand card                                   │
│  [Chat →]     → open AgentChatModal                          │
│                 → POST relay.mobilemonero.com ✅ (fake reply) │
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
| 1 | **Implement real backend for all 8 api.ts endpoints** in relay/server.js — agent onboarding, proposals, CAC status, capital stack, financing, trust score, agent chat, X posting | Large | Unblocks all API-dependent features |
| 2 | **Wire Agent Chat to real AI** (Ollama/Eliza) instead of hardcoded fake response | Medium | Makes chat actually work |
| 3 | **Fix Nav "Reserve →" link** — use React Router `Link` with `to="/presale"` instead of `href="/presale"` | Small | Fixes broken navigation to presale page |
| 4 | **Fix VCPage "Main Site" link** — use `navigate('/cuttlefishclaws')` instead of `navigate('/')` | Small | Fixes broken navigation back to main site |

### 🟠 High (important UX issues)

| # | Action | Effort | Impact |
|---|---|---|---|
| 5 | **Wire VCPage 5 no-op buttons** to real actions or remove them | Small | Removes dead UI |
| 6 | **Fix AgentsSection grid responsiveness** — replace inline style with Tailwind classes | Small | Fixes mobile layout |
| 7 | **Persist Bill of Rights acknowledge state** — use localStorage | Small | Prevents lost progress on refresh |
| 8 | **Verify external services** — test Stripe link, wallet address, Discord invite, cuttlefishclaw.com domain | Medium | Ensures payment and links work |

### 🟡 Medium (polish and completeness)

| # | Action | Effort | Impact |
|---|---|---|---|
| 9 | **Add Privacy Policy page** | Medium | Legal compliance |
| 10 | **Add Terms of Service page** | Medium | Legal compliance |
| 11 | **Add 404 page** | Small | Better UX |
| 12 | **Remove or port legacy Netlify functions** | Medium | Clean up dead code |
| 13 | **Remove or update netlify.toml** | Small | Clean up misleading config |

### 🟢 Low (nice-to-have)

| # | Action | Effort | Impact |
|---|---|---|---|
| 14 | **Add CAC Dashboard page** | Large | Member portal |
| 15 | **Replace mock data with real API calls** | Very Large | Production readiness |
| 16 | **Add loading states to all async operations** | Medium | Better UX |

---

## 13. Summary

| Category | Count |
|---|---|
| Total forms | 3 |
| Working forms | 3 (all POST to relay endpoints) |
| api.ts endpoints (all return email stubs) | 8 |
| Legacy Netlify functions (dead code) | 10 |
| Total pages/routes | 3 (main SPA, /presale, /vc) |
| Missing pages | 3 (privacy, terms, 404) |
| Navigation bugs | 2 |
| No-op buttons (VCPage) | 5 |
| Responsive bugs | 1 |
| State persistence bugs | 1 |
| External services (needs verification) | 4 |
| Mock data dependencies | 6 (100% of data is mock) |

**Bottom line:** The site is a visually impressive static SPA with **all 3 forms working** via relay endpoints (sending email notifications to dvdelze@gmail.com + xmrtnet@gmail.com). The critical issue is that **all 8 api.ts endpoints return email stubs, not real data** — the entire backend is an email notification system with no actual data processing. The 10 legacy Netlify functions contain the real business logic but are dead code. Two navigation links are broken due to the GitHub Pages subpath deployment. The VCPage has 5 no-op buttons. **The single most impactful change is implementing real backend logic in relay/server.js for the 8 api.ts endpoints.**
