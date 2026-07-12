"""KYA-001 service tests (Sprint 2). Standalone — no AR-001 write-path wiring yet."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cryptography.hazmat.primitives import serialization  # noqa: E402
from cryptography.hazmat.primitives.asymmetric import ec, ed25519  # noqa: E402

import kya  # noqa: E402

# --- test keypairs, generated at module load. NOT protocol material. ---
TEST_ED_PRIV = ed25519.Ed25519PrivateKey.generate()
TEST_ED_PUB = TEST_ED_PRIV.public_key().public_bytes_raw()
TEST_ED2_PRIV = ed25519.Ed25519PrivateKey.generate()           # an unrelated "wrong" key
TEST_ED2_PUB = TEST_ED2_PRIV.public_key().public_bytes_raw()

TEST_SK_PRIV = ec.generate_private_key(ec.SECP256K1())
TEST_SK_PUB = TEST_SK_PRIV.public_key().public_bytes(
    serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint
)

TEST_PRINCIPAL_PRIV = ed25519.Ed25519PrivateKey.generate()      # signs the binding_proof


def _principal_ref() -> kya.PrincipalRef:
    return kya.PrincipalRef(
        principal_kind="operator",
        principal_id="kya-test-operator",
        binding_proof=TEST_PRINCIPAL_PRIV.sign(b"accept-accountability"),
    )


def _binding(ed_pub=TEST_ED_PUB, algorithm="ed25519", key_id="key-ed-1") -> kya.KYABinding:
    return kya.KYABinding(
        actor_kind="agent",
        principal_ref=_principal_ref(),
        public_keys=[kya.PublicKeyRef(key_id=key_id, algorithm=algorithm, public_key=ed_pub)],
        ial_level="IAL2",
        issued_at="2026-06-28T00:00:00Z",
        agent_did="did:cardano:testhash",
    )


def _event() -> dict:
    return {
        "activity_type": "VALIDATION_COMPLETED",
        "primary_actor_id": "kya-test:agent",
        "activity_subject": {"type": "proposal", "id": "p-1"},
        "work_unit": {"quantity": 1, "unit": "review"},
        # registry-added fields that MUST be excluded from the actor payload:
        "self_hash": "ff" * 32,
        "registry_signature": "deadbeef",
        "witness_signatures": ["w1"],
    }


# --------------------------------------------------------------- KYA_ID (§2)


def test_kya_id_is_deterministic_and_namespaced():
    b1 = _binding()
    b2 = _binding()
    assert b1.kya_id() == b2.kya_id()             # same content -> same id
    assert b1.kya_id().startswith("kya:agent:")   # namespace = actor_kind


def test_kya_id_changes_when_binding_changes():
    base = _binding().kya_id()
    changed = _binding(key_id="key-ed-CHANGED").kya_id()
    assert base != changed                        # content-addressed


# --------------------------------------------------------------- sign / verify (§4.1, §4.2)


def test_ed25519_sign_verify_round_trip():
    reg = kya.KYARegistry()
    binding = _binding()
    kid = reg.register(binding)
    ev = _event()
    sig = kya.sign_payload(TEST_ED_PRIV, "ed25519", kya.actor_signing_payload(ev))
    ok, reason = reg.verify_event_signature(kid, "key-ed-1", ev, sig)
    assert ok, reason


def test_secp256k1_sign_verify_round_trip():
    reg = kya.KYARegistry()
    binding = _binding(ed_pub=TEST_SK_PUB, algorithm="secp256k1", key_id="key-sk-1")
    kid = reg.register(binding)
    ev = _event()
    sig = kya.sign_payload(TEST_SK_PRIV, "secp256k1", kya.actor_signing_payload(ev))
    ok, reason = reg.verify_event_signature(kid, "key-sk-1", ev, sig)
    assert ok, reason


def test_registry_added_fields_excluded_from_payload():
    ev = _event()
    payload = kya.actor_signing_payload(ev)
    assert "self_hash" not in payload
    assert "registry_signature" not in payload
    assert "witness_signatures" not in payload
    assert payload["activity_type"] == "VALIDATION_COMPLETED"


def test_tampered_payload_rejected():
    reg = kya.KYARegistry()
    kid = reg.register(_binding())
    ev = _event()
    sig = kya.sign_payload(TEST_ED_PRIV, "ed25519", kya.actor_signing_payload(ev))
    ev["work_unit"]["quantity"] = 9999            # tamper after signing
    ok, reason = reg.verify_event_signature(kid, "key-ed-1", ev, sig)
    assert not ok and reason == "signature_invalid"


def test_wrong_key_rejected():
    reg = kya.KYARegistry()
    # binding advertises ED2's public key, but the signature is from ED1
    kid = reg.register(_binding(ed_pub=TEST_ED2_PUB))
    ev = _event()
    sig = kya.sign_payload(TEST_ED_PRIV, "ed25519", kya.actor_signing_payload(ev))
    ok, reason = reg.verify_event_signature(kid, "key-ed-1", ev, sig)
    assert not ok and reason == "signature_invalid"


def test_revoked_key_rejected():
    reg = kya.KYARegistry()
    kid = reg.register(_binding())
    ev = _event()
    sig = kya.sign_payload(TEST_ED_PRIV, "ed25519", kya.actor_signing_payload(ev))
    assert reg.revoke(kid, "key-ed-1")
    ok, reason = reg.verify_event_signature(kid, "key-ed-1", ev, sig)
    assert not ok and reason == "key_status:revoked"


def test_rotated_key_on_new_event_rejected():
    reg = kya.KYARegistry()
    kid = reg.register(_binding())
    ev = _event()
    sig = kya.sign_payload(TEST_ED_PRIV, "ed25519", kya.actor_signing_payload(ev))
    assert reg.rotate(kid, "key-ed-1")
    ok, reason = reg.verify_event_signature(kid, "key-ed-1", ev, sig)
    assert not ok and reason == "key_status:rotated"


def test_algorithm_mismatch_rejected():
    reg = kya.KYARegistry()
    # binding says secp256k1 but stores ed25519 public bytes; sig is ed25519
    kid = reg.register(_binding(ed_pub=TEST_ED_PUB, algorithm="secp256k1", key_id="key-x"))
    ev = _event()
    sig = kya.sign_payload(TEST_ED_PRIV, "ed25519", kya.actor_signing_payload(ev))
    ok, reason = reg.verify_event_signature(kid, "key-x", ev, sig)
    assert not ok and reason == "signature_invalid"


def test_unknown_kya_id_and_key_id():
    reg = kya.KYARegistry()
    kid = reg.register(_binding())
    ev = _event()
    sig = kya.sign_payload(TEST_ED_PRIV, "ed25519", kya.actor_signing_payload(ev))
    ok1, r1 = reg.verify_event_signature("kya:agent:nope", "key-ed-1", ev, sig)
    ok2, r2 = reg.verify_event_signature(kid, "key-missing", ev, sig)
    assert (not ok1 and r1 == "unknown_kya_id")
    assert (not ok2 and r2 == "unknown_key_id")
