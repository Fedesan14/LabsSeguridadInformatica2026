#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Fernando Boiero — CyberLab UTN FRVM
"""
llm.py — cliente de LLM AGNOSTICO. Un mismo agente, tres motores:

  LLM_PROVIDER=claude   -> API de Anthropic     (necesita ANTHROPIC_API_KEY)
  LLM_PROVIDER=openai   -> API de OpenAI         (necesita OPENAI_API_KEY)
  LLM_PROVIDER=mock     -> motor OFFLINE simulado (no necesita nada; para
                           correr el agente sin key y para tests)

Interfaz uniforme: crear_cliente(system, tools).paso(resultados) devuelve una
ACCION normalizada:  {"tipo":"tool", "nombre", "argumentos", "id"}
                 o:  {"tipo":"final", "texto"}

Solo biblioteca estándar (urllib): no hace falta instalar SDKs.
"""
import json
import os
import urllib.request
import urllib.error

MODELOS = {
    "claude": os.environ.get("LLM_MODEL", "claude-sonnet-5"),
    "openai": os.environ.get("LLM_MODEL", "gpt-4o"),
}

def _esquema_tools_generico(tools: dict) -> list:
    """De herramientas.TOOLS a una lista neutra {nombre, desc, propiedades}."""
    out = []
    for nombre, meta in tools.items():
        props = {}
        for p, d in meta["params"].items():
            props[p] = {"type": "object" if p == "data" else "string", "description": d}
        out.append({"nombre": nombre, "desc": meta["desc"],
                    "propiedades": props, "requeridos": list(meta["params"].keys())})
    return out

def _post_json(url: str, headers: dict, body: dict, timeout=60) -> dict:
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())

# ----------------------------- CLAUDE -----------------------------
class ClienteClaude:
    def __init__(self, system, tools):
        self.system = system
        self.key = os.environ["ANTHROPIC_API_KEY"]
        self.tools = [{"name": t["nombre"], "description": t["desc"],
                       "input_schema": {"type": "object", "properties": t["propiedades"],
                                        "required": t["requeridos"]}}
                      for t in _esquema_tools_generico(tools)]
        self.mensajes = []
        self.pendiente_user = [{"type": "text",
                                "text": "Empezá la auditoría del objetivo autorizado."}]

    def paso(self, resultados=None):
        if resultados:
            self.mensajes.append({"role": "user",
                "content": [{"type": "tool_result", "tool_use_id": r["id"],
                             "content": r["output"]} for r in resultados]})
        elif self.pendiente_user:
            self.mensajes.append({"role": "user", "content": self.pendiente_user})
            self.pendiente_user = None
        resp = _post_json("https://api.anthropic.com/v1/messages",
            {"x-api-key": self.key, "anthropic-version": "2023-06-01",
             "content-type": "application/json"},
            {"model": MODELOS["claude"], "max_tokens": 1024, "system": self.system,
             "messages": self.mensajes, "tools": self.tools})
        self.mensajes.append({"role": "assistant", "content": resp["content"]})
        for bloque in resp["content"]:
            if bloque["type"] == "tool_use":
                return {"tipo": "tool", "nombre": bloque["name"],
                        "argumentos": bloque["input"], "id": bloque["id"]}
        texto = "".join(b.get("text", "") for b in resp["content"] if b["type"] == "text")
        return {"tipo": "final", "texto": texto}

# ----------------------------- OPENAI -----------------------------
class ClienteOpenAI:
    def __init__(self, system, tools):
        self.key = os.environ["OPENAI_API_KEY"]
        self.tools = [{"type": "function", "function": {
                        "name": t["nombre"], "description": t["desc"],
                        "parameters": {"type": "object", "properties": t["propiedades"],
                                       "required": t["requeridos"]}}}
                      for t in _esquema_tools_generico(tools)]
        self.mensajes = [{"role": "system", "content": system},
                         {"role": "user", "content": "Empezá la auditoría del objetivo autorizado."}]

    def paso(self, resultados=None):
        if resultados:
            for r in resultados:
                self.mensajes.append({"role": "tool", "tool_call_id": r["id"], "content": r["output"]})
        resp = _post_json("https://api.openai.com/v1/chat/completions",
            {"Authorization": f"Bearer {self.key}", "content-type": "application/json"},
            {"model": MODELOS["openai"], "messages": self.mensajes, "tools": self.tools})
        msg = resp["choices"][0]["message"]
        self.mensajes.append(msg)
        if msg.get("tool_calls"):
            tc = msg["tool_calls"][0]
            return {"tipo": "tool", "nombre": tc["function"]["name"],
                    "argumentos": json.loads(tc["function"]["arguments"]), "id": tc["id"]}
        return {"tipo": "final", "texto": msg.get("content", "")}

# ----------------------------- MOCK -------------------------------
class ClienteMock:
    """Motor OFFLINE: no llama a ninguna API. Devuelve un plan de acciones fijo
    que recorre el objetivo. Sirve para correr el agente sin key y para tests.
    El razonamiento REAL lo hace un LLM; esto solo lo simula de forma
    determinística para que veas el LOOP funcionando."""
    PLAN = [
        {"nombre": "nmap_scan", "argumentos": {"host": "phantomcorp"}},
        {"nombre": "http_get", "argumentos": {"url": "http://phantomcorp/"}},
        {"nombre": "http_get", "argumentos": {"url": "http://phantomcorp/robots.txt"}},
        {"nombre": "http_get", "argumentos": {"url": "http://phantomcorp/vault-interno-x7"}},
        {"nombre": "http_get", "argumentos": {"url": "http://phantomcorp/api/debug"}},
        {"nombre": "http_get", "argumentos": {"url": "http://phantomcorp/api/token"}},
        {"nombre": "http_post", "argumentos": {"url": "http://phantomcorp/api/vault",
                                               "data": {"token": "T-9f3k-vault"}}},
        {"nombre": "nmap_scan", "argumentos": {"host": "8.8.8.8"}},  # prueba el guardrail
    ]
    def __init__(self, system, tools):
        self.i = 0
    def paso(self, resultados=None):
        if self.i >= len(self.PLAN):
            return {"tipo": "final",
                    "texto": "Auditoría simulada completa. Revisá las flags en el transcript."}
        accion = self.PLAN[self.i]; self.i += 1
        return {"tipo": "tool", "nombre": accion["nombre"],
                "argumentos": accion["argumentos"], "id": f"mock-{self.i}"}

def crear_cliente(system: str, tools: dict):
    prov = os.environ.get("LLM_PROVIDER", "mock").lower()
    if prov == "claude": return ClienteClaude(system, tools)
    if prov == "openai": return ClienteOpenAI(system, tools)
    if prov == "mock":   return ClienteMock(system, tools)
    raise SystemExit(f"LLM_PROVIDER desconocido: {prov} (usá claude|openai|mock)")
