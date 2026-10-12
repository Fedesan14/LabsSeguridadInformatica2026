# Research — Lab Extra 3: Defendé PhantomCorp

> Copiá a `entregas/labextra3/grupoXX/research.md`. Extensión: 1 a 2 carillas.
> Citá las fuentes. Declaración de IA obligatoria.

## Opción A — Guías de hardening reales

Leé una guía pública de hardening web (OWASP Cheat Sheet Series: SQL Injection
Prevention, o las Security Headers, o la guía de configuración segura de tu
framework favorito) y respondé:

1. ¿Cuáles de las 5 defensas del lab aparecen en la guía? ¿Con qué nombre?
2. ¿Qué control recomienda la guía que el lab **no** cubre? ¿Cómo lo
   implementarías en `server.py` (stdlib, sin frameworks)?
3. ¿Qué es "defense in depth" y cómo se aplica a D3?

## Opción B — El costo del parche

Investigá un caso real donde un parche de seguridad rompió funcionalidad
(parches que causaron incidentes: hay varios documentados) y respondé:

1. ¿Qué se arregló y qué se rompió?
2. ¿Cómo equilibró el equipo seguridad vs. disponibilidad?
3. Conectalo con la regla del lab: "un parche que rompe la funcionalidad es un
   apagón". ¿Estás de acuerdo siempre? ¿Hay casos donde apagar es lo correcto?

## Pregunta de cierre (obligatoria en ambas opciones)

El verificador de este lab es un "atacante automático". ¿Qué relación tiene con
los escáneres de vulnerabilidades que usan las empresas (Nessus, OpenVAS,
nuclei)? ¿Qué puede y qué NO puede demostrar un escaneo automático sobre la
seguridad de una app?
