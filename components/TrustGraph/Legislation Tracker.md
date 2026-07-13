# Legislation Tracker

**Role:** Living index of laws & regulations gating CAC design decisions
**Type:** Documentation
**Status:** Canonical — review quarterly
**Next review:** 2026-09-26
**Owner:** Navigator (David Hans Elze)

Every law, rule, or proposal that gates a CAC design decision. CAC's token mechanics, identity model, and routing architecture are deliberately engineered against current and proposed legislation.

## Key Laws

- **CLARITY Act** 🟠 — Token classification, utility credential safe harbor
- **GENIUS Act** 🟠 — Stablecoin regulation, USDC backing model
- **Howey Test** ✅ — Investment contract classification (structurally not met)
- **BSA / FinCEN MSB** ✅ — Money transmission, likely some registration required
- **FATF Travel Rule** ✅ — Cross-border P2P transfers >$3,000
- **EU AI Act** ✅ — Transparency, provenance, risk classification
- **GDPR** ✅ — Audit log retention vs on-chain immutability
- **MiCA** ✅ — EU token classification (likely utility token)
- **California SB 1047** ⚪ — Vetoed, possible re-introduction
- **NIST AI RMF 1.0** ✅ — TrustGraph design alignment

## Pre-positioning

CAC's design anticipates regulation: face-value P2P (Howey), USDC backing (GENIUS), KYA-bound identity (accountability laws), constitutional hashing (AI provenance), jurisdictional routing (state/EU fragmentation), 4.5% savings framing (investment-contract avoidance).

## Related

- [[CAC]] — credential designed against these laws
- [[Agent]] — constitutional AI framework
- [[TrustGraph]] — scoring layer
- [[Navigator]] — owner of this tracker
- [[SOUL]] — agent identity, jurisdictional bindings
- [[CONSTITUTION]] — protocol rules
- [[Canonical Reconciliation]] — single source of truth
- [[Two Stack Architecture]] — compute vs capital separation
- [[Product Thesis]] — why this exists
