# FAQ y troubleshooting — cuando algo no anda

> Antes de abrir un Issue, buscá acá. El 90% de lo que traba a la gente está en
> esta página. Si tu problema no está, abrí un Issue con: qué comando corriste,
> qué esperabas, y el error COMPLETO (copiado, no una captura borrosa).

## Instalación y entorno

**`docker: command not found` o `make setup` falla.**
Los labs ofensivos (05 en adelante) necesitan Docker + Docker Compose. Verificá:

```bash
docker --version && docker compose version
```

Si no están: Docker Desktop en Mac/Windows, o `docker` + plugin `compose` en
Linux. Los labs de código (01-04) NO necesitan Docker — solo Python 3.

**`Cannot connect to the Docker daemon`.**
El motor de Docker no está corriendo. En Mac/Windows: abrí Docker Desktop y
esperá a que el ícono quede fijo. En Linux: `sudo systemctl start docker`.

**`permission denied` al correr `docker` en Linux.**
Tu usuario no está en el grupo docker:

```bash
sudo usermod -aG docker $USER    # y después cerrá sesión y volvé a entrar
```

**`make: command not found` (Windows).**
Usá WSL2 (Ubuntu) y corré todo desde ahí, no desde PowerShell. Los labs asumen
un entorno tipo Unix (bash, make, rutas con `/`).

**`port is already allocated` al levantar un lab.**
Otro proceso (u otro lab que no bajaste) ocupa el puerto. Bajá todo y reintentá:

```bash
make down        # baja el lab actual
docker ps        # ¿quedó algo arriba? anotá el nombre
make clean       # limpieza más agresiva si hace falta
```

## Usar los labs

**`make shell` no me deja entrar / "no such service".**
Primero levantá el lab: `./ctf lab NN`. El `make shell` te mete en la consola
del atacante de un lab que YA está arriba.

**¿`make shell` o `make shell-victima`?**
`make shell` = la **consola del atacante** (donde tenés las tools). En el Lab 08,
`make shell-victima` te mete en el **host ya comprometido** (sos el atacante que
ya entró y ahora escala). No los confundas: son dos puntos de vista distintos.

**No encuentro el target `phantomcorp` / "could not resolve host".**
Ese nombre solo existe DENTRO de la consola del atacante (red de Docker). Tenés
que estar adentro (`make shell`), no en tu terminal normal.

**El lab quedó raro / cambié algo y no sé qué.**
Bajá y volvé a levantar limpio:

```bash
make down && ./ctf lab NN
```

## Entregar flags

**`./ctf submit` me dice que la flag es incorrecta y estoy seguro que está bien.**
Chequeá, en orden:

1. **El formato completo**, con llaves: `FLAG{...}`, no solo el texto de adentro.
2. **Comillas simples**: `./ctf submit 07 R1 'FLAG{...}'`. Sin comillas, el shell
   se puede comer las llaves.
3. **El reto correcto**: ¿es R1 o R3? Mirá `./ctf status NN`.
4. **Espacios o saltos invisibles**: si copiaste de una salida, puede venir con
   un `\n` o un espacio pegado. Escribila a mano.

El motor compara `sha256(tu_flag)` contra el manifest. Un solo carácter de más y
el hash no coincide.

**¿Puedo ver las flags en el código del target?**
Están ofuscadas (base64) a propósito. Podés decodificarlas leyendo el fuente,
sí... pero eso no es hacer el lab, es hacerte trampa a vos mismo. El objetivo es
que las obtengas con las tools. Nadie te va a correr, pero vos sabés.

## Presentación de terminal

**Se ven caracteres rotos / cuadrados / símbolos raros.**
Tu terminal no está en UTF-8. Probá:

```bash
export LANG=es_AR.UTF-8      # o en_US.UTF-8, el que tengas
```

Y usá una terminal moderna (iTerm2, Kitty, Alacritty, o la de VS Code). La
presentación dibuja con caracteres de bloque Unicode: en un locale no-UTF-8 se
rompe.

**La animación va lenta / trabada.**
Es curses puro, sin dependencias. Si tu terminal es muy chica, agrandala.
Salís con `q` en cualquier momento.

## Lab 09 (agentes) y las API keys

**No tengo API key de Claude/OpenAI.**
No hace falta para aprender el mecanismo. Corré en modo mock (offline):

```bash
export LLM_PROVIDER=mock
```

El loop de tool-use es idéntico; lo único que cambia es quién "razona". Con mock
practicás el andamiaje sin gastar un peso.

**Tengo key pero da error de autenticación.**
Verificá que exportaste LA variable correcta para tu proveedor
(`ANTHROPIC_API_KEY` para claude, `OPENAI_API_KEY` para openai) Y el
`LLM_PROVIDER` que corresponde. Nunca subas tu key al repo: está en `.gitignore`,
pero igual, cuidala.

## Git y entregas

**Hice un desastre con git / merge conflict al sincronizar.**
Lo más seguro: no labures sobre `main`. Ramá por entrega:

```bash
git checkout -b entregas/labNN/grupoXX
```

Si el conflicto es en archivos de la cátedra que vos no tocaste, quedate con los
de upstream. Si es en tu entrega, resolvé a mano y commiteá.

**¿Cómo entrego?**
Fork del repo, tu trabajo en `entregas/labNN/grupoXX/`, y Pull Request al repo de
la cátedra. El detalle está en [INTRODUCCION.md](INTRODUCCION.md).

---

> Buscá también en el [Glosario](GLOSARIO.md) si lo que te traba es una palabra, y
> en el [Cheatsheet](CHEATSHEET.md) si es un comando. ¿Sigue sin andar? Issue en
> el repo, con el error completo. Preguntar bien también se aprende.
