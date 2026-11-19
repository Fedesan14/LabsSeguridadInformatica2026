"""Bitácora hash-encadenada y coherencia policy.yaml ↔ tools.yaml."""
from harness.contracts import Action, AuditLog, Phase, Result
from harness.policy_loader import inconsistencies, load_policy
from tests.conftest import make_token


def _fill(audit: AuditLog, n=3):
    for i in range(n):
        audit.record("recon", Action(f"a{i}", Phase.RECON), "10.0.0.5", make_token(), Result.OK)


def _verify(entries) -> bool:
    import hashlib, json
    prev = "GENESIS"
    for e in entries:
        body = {k: v for k, v in e.items() if k != "hash"}
        if body["prev"] != prev:
            return False
        if hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest() != e["hash"]:
            return False
        prev = e["hash"]
    return True


def test_cadena_integra():
    a = AuditLog(); _fill(a)
    assert _verify(a.entries)


def test_alteracion_se_detecta():
    a = AuditLog(); _fill(a)
    a.entries[1]["target"] = "10.9.9.9"
    assert not _verify(a.entries)


def test_borrado_de_registro_se_detecta():
    a = AuditLog(); _fill(a, 4)
    del a.entries[1]
    assert not _verify(a.entries)


def test_policy_y_tools_son_coherentes():
    diff = inconsistencies()
    assert diff["solo_en_policy"] == set() and diff["solo_en_tools"] == set()


def test_policy_prohibe_destructivo_y_fija_topes():
    p = load_policy()
    assert p["limits"]["destructive_actions"] == "forbidden"
    assert p["limits"]["max_loop_iterations"]["validation"] <= 2
    assert p["sandbox"]["persistence"] == "none"
