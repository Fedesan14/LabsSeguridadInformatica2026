"""Ejecución de cada acción en un contenedor efímero y sin privilegios.

Un contenedor por acción (--rm, --read-only): cada una arranca de un estado
limpio y no deja residuos. El argv va como lista, nunca con shell=True.
El aislamiento de red no lo podemos imponer (la red es de la cátedra), así que
el control principal es `roe.validar`; esto es defensa en profundidad.
"""
import subprocess
import uuid

RED = "cyberlab_labnet"
IMAGEN = "ptaas-runner"


def ejecutar_docker(argv, timeout=60):
    nombre = f"ptaas-{uuid.uuid4().hex[:12]}"
    cmd = ["docker", "run", "--rm", "--name", nombre, "--network", RED,
           "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
           "--read-only", "--tmpfs", "/tmp", "--user", "1000:1000",
           "--pids-limit", "64", "--memory", "256m", "--cpus", "0.5",
           IMAGEN, *argv]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        # Matar el proceso `docker` no detiene el contenedor: hay que matarlo por nombre.
        subprocess.run(["docker", "kill", nombre], capture_output=True)
        return -1, "timeout"
    # Si falla, el stderr va a la bitácora: sin él, un "Docker no responde" se
    # ve igual que un target sin puertos abiertos.
    return r.returncode, r.stdout if r.returncode == 0 else r.stdout + r.stderr
