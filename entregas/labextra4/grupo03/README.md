# Lab Extra 4 — Grupo 03

Entrega de cracking de contraseñas, basada en `labs/labextra4-cracking/`.

- [Informe](informe.md): resultados, mediciones reales, P1–P5, loot, flags, captura y declaración de IA.
- [Research, opción B](research.md): hashcat, GPU, tipos de ataque, rainbow tables y k-anonymity.
- [Cracker](cracker.py): diccionario, reglas y descifrado; Python 3.9 o superior, solo biblioteca estándar.
- [Evidencia](evidencia/comandos.txt): comandos, salidas crudas, huellas de los archivos de entrada y estado CTF **3/3**.

Todos los comandos siguientes se ejecutan **desde la raíz del repositorio**:

```powershell
python -X utf8 entregas/labextra4/grupo03/cracker.py crackear labs/labextra4-cracking/caso/sombra.txt labs/labextra4-cracking/caso/diccionario.txt
python -X utf8 entregas/labextra4/grupo03/cracker.py crackear labs/labextra4-cracking/caso/sombra.txt labs/labextra4-cracking/caso/diccionario.txt --reglas
python -X utf8 entregas/labextra4/grupo03/cracker.py descifrar labs/labextra4-cracking/caso/loot/admin.enc --password phantom2026
python -X utf8 entregas/labextra4/grupo03/test_cracker.py
```

El ataque prueba también PBKDF2: la corrida con reglas tarda aproximadamente **80 segundos** en el equipo medido. No agrega a los candidatos la clave de referencia de root que aparece en el generador.

Para repetir mediciones, ataques, descifrados, entregas al CTF local y captura:

```powershell
python -X utf8 entregas/labextra4/grupo03/reproducir.py
```

Esto sobrescribe la evidencia de ejecución; los tiempos del informe corresponden a la corrida original del 19/11/2026. El progreso CTF se guarda localmente en `.progreso/`, que no se versiona. Para completar solo las etapas posteriores a los ataques guardados, usar `reproducir.py --continuar`.

En Linux/macOS, el CTF se puede usar directamente:

```bash
bash ./ctf submit extra4 R1 'FLAG{crack_diccionario_md5}'
bash ./ctf submit extra4 R2 'FLAG{crack_sha256_diccionario}'
bash ./ctf submit extra4 R3 'FLAG{crack_reglas_mangling}'
bash ./ctf status extra4
```

En Windows, `reproducir.py` localiza Git Bash y utiliza [ctf_windows.sh](ctf_windows.sh) para el checkout CRLF. También se puede ejecutar desde una terminal de Git Bash:

```bash
bash -o igncr entregas/labextra4/grupo03/ctf_windows.sh status extra4
```

La captura [ctf-status.png](evidencia/ctf-status.png) muestra la salida cruda del CTF en un visor HTML local. Para generarla automáticamente hace falta Chrome, Chromium o Edge; no interviene en el ataque. Las funciones, subcomandos y pruebas del cracker funcionan sin dependencias adicionales.

Se utilizó OpenAI Codex para la implementación, ejecución, investigación y redacción; las declaraciones completas están en el informe y en el research. Los originales de la cátedra permanecen sin cambios.
