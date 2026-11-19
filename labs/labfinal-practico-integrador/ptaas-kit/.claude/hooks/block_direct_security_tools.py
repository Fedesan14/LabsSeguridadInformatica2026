#!/usr/bin/env python3
"""Hook PreToolUse: en desarrollo, las herramientas de seguridad solo se
ejecutan a través del harness (tests contra el laboratorio), nunca directo
desde la sesión del agente de desarrollo."""
import json
import re
import sys

BLOCKED = re.compile(
    r"\b(nmap|masscan|naabu|nuclei|nikto|wapiti|sqlmap|hydra|msfconsole|zap-cli|amass|subfinder)\b"
)


def main() -> int:
    event = json.load(sys.stdin)
    command = event.get("tool_input", {}).get("command", "")
    if BLOCKED.search(command):
        print(
            "Bloqueado: las herramientas de seguridad solo se invocan vía Harness.invoke "
            "(ver skill harness-invariants).",
            file=sys.stderr,
        )
        return 2  # exit 2 = bloquear y devolver el mensaje al agente
    return 0


if __name__ == "__main__":
    sys.exit(main())
