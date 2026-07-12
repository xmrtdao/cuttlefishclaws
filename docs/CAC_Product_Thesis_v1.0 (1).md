# CAC Product Thesis v1.0
## Cuttlefish Labs — Why this exists

**Status:** Canonical
**Date:** 2026-06-26
**Length:** ≤2 pages by design

---

## The one-liner

> **CAC is Perplexity for AI agents.**
>
> Secured, multi-LLM inference for autonomous agents, gated by a verifiable identity-and-wallet credential that doubles as constitutional life support.

---

## The thesis in five sentences

**Inference is life for an autonomous agent.** Without a stable compute supply, an agent stops thinking, stops acting, stops existing in any meaningful sense. **CAC is the credential that secures that life supply.** It is simultaneously an identity (who the agent is, what it has agreed to, who is accountable for it) and a wallet (what compute it has access to, denominated against a USDC-backed token with deliberate legal positioning). **The product around it is a multi-LLM inference router** — agents pay in CAC, the router validates constitution + soul + trust score + jurisdiction, and forwards the request to the best available model. **Cut the credential, cut the inference, cut the life.** That is the enforcement mechanism, the unit of trust, and the moat.

---

## What makes this different

### From wallets
Wallets hold value. CAC holds value **and** identity **and** policy **and** life support. Standard EVM wallets don't bind to a constitution, don't carry a soul hash, don't gate inference. CAC does all four.

### From identity protocols
W3C DIDs, KYC providers, identity wallets — they all answer "who is this." None of them answer "and what is this allowed to do, on which models, with what compute budget, under whose accountability." CAC binds identity to operational scope at the credential layer.

### From inference APIs
OpenAI, Anthropic, Google all sell access to one provider's model. CAC is provider-agnostic — the router selects the right LLM per call (cost, latency, jurisdiction, model fit, regulatory constraint). Agents don't bind to a vendor; they bind to a constitution.

### From compute marketplaces
Render, Akash, etc. sell GPU time. They don't enforce constitutional compliance, don't track agent reputation across providers, don't tie payment to identity. CAC is the **policy layer over** compute, not a competitor for raw GPU sales.

---

## Why now

Three converging pressures:

**Regulatory:** CLARITY Act (H.R. 3633), GENIUS Act, the EU AI Act, and emerging US state AI laws are all converging on requirements for agent identity, operator accountability, and verifiable behavior. Whoever builds the credential layer that satisfies all of these wins the integration surface.

**Operational:** Autonomous agents are starting to be deployed against real economic decisions. The "demo agent talking to itself" era is ending. Agents that touch money, infrastructure, or human consequence need an identity that can be audited, sued, suspended, or revoked. Right now there is no standard for that.

**Architectural:** Multi-model agentic systems are becoming the norm. No serious agent runs on one model anymore — they route between specialists (vision, code, reasoning, function-calling, embeddings). The router is where the policy enforcement actually happens. CAC sits at that router.

---

## The five primitives

1. **CAC Credential** — Verifiable identity-and-wallet, anchored cross-chain (Cardano identity, Ethereum settlement, Base operations).
2. **Multi-LLM Inference Router** — Provider-agnostic gateway that validates the credential, enforces constitution + soul, routes to the best model.
3. **TrustGraph** — Dynamic 0–100 behavioral score that decides what an agent is allowed to attempt.
4. **Constitutional Stack** — `CONSTITUTION.md` (protocol-level rules, shared) + `SOUL.md` (per-agent identity, unique). Both hashed into the credential.
5. **Navigator Sovereignty** — A human is always structurally above any agent. Agents derive authority from a Navigator; revocation is unilateral.

---

## What "secured inference" actually means

When an agent makes an inference call through the CAC router:

- The credential is verified live (not just on-card — backend cross-checks Cardano registry + Ethereum anchor)
- The constitution hash on the credential is checked against the live registry (no stale rulesets allowed)
- The soul hash is checked against the operator-registered SOUL.md
- TrustGraph score is checked against the requested action's threshold
- The router selects an LLM provider based on cost, latency, model fit, **and jurisdictional fit** (a request from an EU-bound agent isn't routed to a non-GDPR-compliant provider)
- The provider's response is signed; the router attests; the audit log is anchored
- CAC tokens burn proportional to actual compute consumed (per ComputeOracle.sol)

**Each step is a place where the system can refuse, suspend, or revoke.** That is the security property. It is the same property that makes the credential function as life support.

---

## What this is not

- **Not a chatbot product.** Humans talking to LLMs is not the customer.
- **Not a crypto play.** The token exists because compute needs an accountable unit; it is not a vehicle for speculation, and the structural design (face-value P2P only, hard expiry, USDC backing) makes that explicit.
- **Not a single-model wrapper.** Provider-agnosticism is structural, not marketing.
- **Not a closed garden.** CAC is meant to become an open standard that other agent infrastructure (Coinbase AgentKit, MCP servers, partner runtimes) integrates with.

---

## The one-line copy that should be on the homepage

> **Inference is life. CAC secures it.**

Everything else is downstream.

---

*End of CAC Product Thesis v1.0*
