# Laboratorios — Seguridad Informática 2026

Repositorio de trabajos prácticos de laboratorio de la asignatura **Seguridad
Informática**, carrera de Ingeniería en Sistemas de Información.

| | |
|---|---|
| **Institución** | UTN — Facultad Regional Villa María |
| **Asignatura** | Seguridad Informática (Quinto nivel) |
| **Docente** | Ing. Fernando Boiero — Prof. Adj. Int. Simple |
| **Ciclo lectivo** | 2026 |
| **Carga horaria** | 96 h totales · 6 h semanales · 16 semanas |

---

## Cómo se trabaja

Los laboratorios se entregan mediante **fork + Pull Request** contra este
repositorio. El procedimiento completo, paso a paso, está en
[`CONTRIBUTING.md`](CONTRIBUTING.md). **Leelo antes de tocar nada.**

Reglas que valen para todos los labs:

1. **Grupos de 4 a 5 integrantes.** El grupo se mantiene durante todo el
   cuatrimestre salvo autorización expresa del docente.
2. Cada grupo entrega dentro de su propio directorio:
   `entregas/labNN/grupoXX/`. **Nunca** modifiquen archivos de otro grupo ni
   del enunciado.
3. El historial de commits es parte de la evaluación. Se espera ver
   **contribuciones de todos los integrantes** desde sus propias cuentas de
   GitHub.
4. Todo uso de asistentes de IA debe declararse. No está prohibido: está
   **obligatoriamente documentado**. Ver la sección correspondiente en cada
   plantilla de entregable.

> **Advertencia legal.** Todo el material de esta asignatura se practica sobre
> entornos propios, entornos de laboratorio provistos por la cátedra o
> aplicaciones deliberadamente vulnerables de uso público. Ejecutar cualquier
> técnica de las que se estudian contra sistemas de terceros sin autorización
> escrita constituye delito en la República Argentina (Ley 26.388). Ver
> [`CONTRIBUTING.md`](CONTRIBUTING.md) § Uso responsable.

---

## Índice de laboratorios

| Lab | Unidad | Tema | Estado |
|---|---|---|---|
| [01](labs/lab01-introduccion/) | 1 | Introducción: la tríada CIA, historia de la seguridad informática e integridad con funciones de hash | **Publicado** |
| [02](labs/lab02-criptografia/) | 2 | Criptografía: romper un cifrado clásico y MAC con HMAC | **Publicado** |
| [03](labs/lab03-autenticacion/) | 3 | Autenticación y control de acceso: PBKDF2 y TOTP (2FA) | **Publicado** |
| [04](labs/lab04-marcos-normativos/) | 4 | Marcos normativos y gestión: aplicar ISO/NIST y cuantificar riesgo | **Publicado** |
| [05](labs/lab05-reconocimiento/) | 5 | Reconocimiento: identificación y clasificación de la superficie de ataque | **Publicado** |
| [06](labs/lab06-enumeracion-de-servicios/) | 6 | Enumeración de servicios: directorios, `.git`, métodos HTTP, APIs y fingerprinting | **Publicado** |
| [07](labs/lab07-explotacion/) | 7 | Explotación: SQLi, inyección de comandos, path traversal e IDOR | **Publicado** |
| [08](labs/lab08-postexplotacion/) | 8 | Post-explotación y automatización: loot, SUID, pivoting y scripting | **Publicado** |
| [09](labs/lab09-agentes/) | 9 | Agentes de pentest: tool-use, guardrails y APIs de LLM (Claude/OpenAI/mock) | **Publicado** |
| [10](labs/lab10-deteccion-evasion/) | 10 | Detección y evasión: la vista del defensor (Blue vs Red) | **Publicado** |
| [★ Final](labs/labfinal-practico-integrador/) | — | **Práctico final integrador**: engagement completo + informe de pentest profesional | **Publicado** |

Cada laboratorio se habilita al inicio de la unidad correspondiente. Los
títulos marcados *«según programa analítico»* se completan al publicarse el
enunciado.

Los laboratorios de la **primera mitad** son de teoría y código (Python). A
partir de la Unidad 5 son **ofensivos**: operás herramientas reales contra
objetivos deliberadamente vulnerables que **se levantan solos en Docker**, dentro
de tu máquina. La dificultad y la autonomía crecen lab a lab, hasta cerrar con
agentes de pentest en las últimas unidades.

---

## El motor de laboratorios — `./ctf`

Los labs ofensivos son **autodescubribles**: no hay que adivinar qué hacer.
Desde la raíz del repo:

```bash
./ctf                 # muestra el plan de labs y tu progreso
./ctf lab 05          # arranca un lab: levanta su entorno y abre la guía
./ctf status 05       # tus retos resueltos
./ctf submit 05 R1 'FLAG{...}'   # entregás una flag que encontraste
```

Cada lab esconde **flags** en los servicios del objetivo. Las descubrís operando
las tools (nmap, curl, etc.) y las entregás para llevar tu progreso. **Las flags
te enganchan; el informe es lo que evalúa la rúbrica.** Todas las herramientas
viven dentro de un contenedor "atacante": tu máquina queda limpia.

---

## Requisitos técnicos

- **Python 3.10 o superior.** Los laboratorios de código usan exclusivamente la
  **biblioteca estándar** salvo indicación contraria. No hay que instalar
  dependencias.
- **Docker** y **Docker Compose** — para los labs ofensivos (Unidad 5 en
  adelante). Docker Desktop en Mac/Windows; `docker` + plugin `compose` en Linux.
- **Git** y una cuenta de **GitHub** por integrante.
- Un editor de texto o IDE. Cualquiera sirve.

Verificá tu entorno:

```bash
python3 --version
docker --version && docker compose version
```

---

## Estructura del repositorio

```
LabsSeguridadInformatica2026/
├── ctf                      # Punto de entrada autodescubrible (./ctf)
├── Makefile                 # make setup / make lab N=05 / make shell
├── CONTRIBUTING.md          # Flujo de trabajo: fork, rama, PR
├── bin/                     # Motor del curso (ASCII, verificador de flags)
├── entorno/                 # Consola del atacante (Docker) compartida
├── labs/                    # Enunciados y esqueletos (NO modificar)
│   ├── _plantilla/          # Molde para crear labs nuevos
│   ├── lab01-introduccion/  # Teoría + código (Python stdlib)
│   │   ├── README.md · src/ · data/ · docs/
│   └── lab05-reconocimiento/# Primer lab ofensivo (Docker + flags)
│       ├── README.md        # Enunciado (Teoría → Ejemplos → Tools → Práctica)
│       ├── entorno/         # Target vulnerable (PhantomCorp) en Docker
│       ├── src/             # Ampliación opcional (mini-escáner a completar)
│       ├── retos.manifest   # Flags del lab (hasheadas)
│       └── docs/            # Entregable, research y rúbrica
└── entregas/                # Acá va el trabajo de cada grupo
    └── lab05/
        └── grupo01/         # Lo crea el grupo
```

---

## Documentación

- [Guía del curso](docs/GUIA-DEL-CURSO.md) — qué es el práctico, el arco completo y cómo se trabaja.
- [Guía para docentes](docs/PARA-DOCENTES.md) — diseño pedagógico, corrección y cómo crear labs nuevos.
- [Arquitectura del motor](docs/ARQUITECTURA.md) — cómo funciona por dentro.
- [Presentación (terminal)](docs/presentacion.py) — deck ASCII **bien hacker** (Python/curses): intro con lluvia de Matrix, `./docs/presentacion.py` (← → navegar · `q` salir).
- [Presentación (HTML)](docs/presentacion.html) — deck para presentar el práctico (abrila en el navegador).
- [Presentación (PPT)](docs/CyberLab-UTN.pptx) — la misma, en PowerPoint editable, como respaldo.

---

## Contacto

Consultas sobre los enunciados: por el canal de la cátedra o abriendo un
**Issue** en este repositorio. Los Issues son públicos y la respuesta le sirve
a todos — usalos.
