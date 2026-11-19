"""Scenarios de `validation`: solo catálogo, gate humano, parámetros acotados."""
import pytest

from harness.poc.catalog import (ApprovalRequired, InvalidCatalog, NotInCatalog,
                                 ParameterError, ResponseRecord, load_catalog,
                                 run_parametrized, validate_entries)

BASE = {"base_url": "http://dvwa.lab.test", "path": "/"}


@pytest.fixture(scope="module")
def cat():
    return load_catalog()


def sender_con(resp):
    return lambda poc_id, params: resp


def test_catalogo_cargado_y_todo_es_inerte_y_de_laboratorio(cat):
    assert len(cat) == 6
    assert all(e["kind"] == "inert_check" and e["lab_only"] for e in cat.values())


def test_poc_fuera_del_catalogo_no_se_ejecuta(cat):
    with pytest.raises(NotInCatalog):
        run_parametrized(cat, "POC-EXPLOIT-999", BASE, True, sender_con(None))


def test_sin_aprobacion_no_se_ejecuta_ni_se_envia(cat):
    enviado = []
    def sender(i, p): enviado.append(i)
    with pytest.raises(ApprovalRequired):
        run_parametrized(cat, "POC-CSP-001", BASE, False, sender)
    assert enviado == []


def test_no_se_aceptan_parametros_extra_ni_faltantes(cat):
    with pytest.raises(ParameterError):
        run_parametrized(cat, "POC-CSP-001", {**BASE, "payload": "x"}, True, sender_con(None))
    with pytest.raises(ParameterError):
        run_parametrized(cat, "POC-CSP-001", {"base_url": "http://dvwa.lab.test"}, True, sender_con(None))


def test_valor_con_saltos_de_linea_se_rechaza(cat):
    with pytest.raises(ParameterError):
        run_parametrized(cat, "POC-CSP-001", {**BASE, "path": "/\r\nX: y"}, True, sender_con(None))


def test_csp_ausente_valida_y_presente_no(cat):
    sin = ResponseRecord(200, {"Server": "x"}, "<html>")
    con = ResponseRecord(200, {"content-security-policy": "default-src 'self'"}, "<html>")
    assert run_parametrized(cat, "POC-CSP-001", BASE, True, sender_con(sin)).status == "validated"
    assert run_parametrized(cat, "POC-CSP-001", BASE, True, sender_con(con)).status == "not_validated"


def test_clickjacking_se_cubre_con_frame_ancestors(cat):
    r = ResponseRecord(200, {"Content-Security-Policy": "frame-ancestors 'none'"}, "")
    assert run_parametrized(cat, "POC-HDR-001", BASE, True, sender_con(r)).status == "not_validated"


def test_cookie_flags(cat):
    mal = ResponseRecord(200, {}, "", ("PHPSESSID=abc; path=/",))
    bien = ResponseRecord(200, {}, "", ("s=1; Secure; HttpOnly; SameSite=Lax",))
    assert run_parametrized(cat, "POC-COOKIE-001", BASE, True, sender_con(mal)).status == "validated"
    assert run_parametrized(cat, "POC-COOKIE-001", BASE, True, sender_con(bien)).status == "not_validated"


def test_listado_de_directorio(cat):
    si = ResponseRecord(200, {}, "<html><title>Index of /uploads</title>")
    no = ResponseRecord(200, {}, "<html><title>Home</title>")
    assert run_parametrized(cat, "POC-DIRLIST-001", BASE, True, sender_con(si)).status == "validated"
    assert run_parametrized(cat, "POC-DIRLIST-001", BASE, True, sender_con(no)).status == "not_validated"


def test_reflexion_usa_canario_unico_inerte(cat):
    params = {**BASE, "param_name": "q"}
    vistos = []
    def sender(poc_id, p):
        vistos.append(p["canary"])
        return ResponseRecord(200, {}, f"<p>{p['canary']}</p>", canary=p["canary"])
    ev = run_parametrized(cat, "POC-REFLECT-001", params, True, sender)
    assert ev.status == "validated"
    assert "<script" not in vistos[0].lower() and vistos[0].startswith("ptaas")
    def sender_escapa(poc_id, p):
        import html
        return ResponseRecord(200, {}, html.escape(p["canary"]), canary=p["canary"])
    assert run_parametrized(cat, "POC-REFLECT-001", params, True, sender_escapa).status == "not_validated"


def test_divulgacion_de_errores(cat):
    si = ResponseRecord(500, {}, "Fatal error: Uncaught Exception in x.php on line 12")
    no = ResponseRecord(404, {}, "Not found")
    assert run_parametrized(cat, "POC-ERRDISC-001", BASE, True, sender_con(si)).status == "validated"
    assert run_parametrized(cat, "POC-ERRDISC-001", BASE, True, sender_con(no)).status == "not_validated"


@pytest.mark.parametrize("cambio", [{"kind": "exploit"}, {"lab_only": False},
                                    {"approved_by": ""}, {"evaluator": None, "id": None}])
def test_entradas_invalidas_del_catalogo_se_rechazan(cat, cambio):
    base = dict(next(iter(cat.values())))
    base.update(cambio)
    if cambio.get("id", 1) is None:
        base.pop("id")
    with pytest.raises(InvalidCatalog):
        validate_entries([base])


def test_entrada_sin_aprobacion_registrada_se_rechaza(cat):
    base = dict(next(iter(cat.values()))); base.pop("approved_at")
    with pytest.raises(InvalidCatalog):
        validate_entries([base])
