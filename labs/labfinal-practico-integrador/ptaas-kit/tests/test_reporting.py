import pytest

from harness.reporting import DeliveryNotApproved, Finding, MissingField, deliver, render_report

VEC = "CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N"


def f(**kw):
    base = dict(id="F-1", title="Falta de CSP", asset="dvwa.lab.test", cwe="CWE-693",
                cvss_v4_vector=VEC, remediation="Definir Content-Security-Policy",
                validation_status="validated")
    return Finding(**{**base, **kw})


def test_informe_completo_se_genera_con_estado_de_validacion():
    r = render_report("eng-1", [f(), f(id="F-2", validation_status="not_validated")])
    assert "CWE-693" in r["markdown"] and "validado en sandbox" in r["markdown"]
    assert "no validado" in r["markdown"] and r["delivered"] is False


@pytest.mark.parametrize("campo,valor", [("cwe", ""), ("cwe", "unknown"),
                                         ("cvss_v4_vector", "CVSS:3.1/AV:N"),
                                         ("remediation", "  ")])
def test_hallazgo_incompleto_falla_indicando_el_campo(campo, valor):
    with pytest.raises(MissingField) as e:
        render_report("eng-1", [f(**{campo: valor})])
    assert "F-1" in str(e.value)


def test_entrega_sin_aprobacion_se_rechaza():
    r = render_report("eng-1", [f()])
    with pytest.raises(DeliveryNotApproved):
        deliver(r, reviewer_approved=False)
    assert deliver(r, reviewer_approved=True)["delivered"] is True
