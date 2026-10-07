# installer/orchestrator.py | Vitalia SDD v0.6.0 | 06-10-2026 16:05(GMT-04:00)
import subprocess
import os
import asyncio

LOG_FILE = os.path.join(os.path.dirname(__file__), "installer_output.log")
SCRIPT_FILE = os.path.join(os.path.dirname(__file__), "install_runner.sh")

def start_installation():
    # Assegura que o script de orquestração (agora separado) tenha permissão de execução
    if os.path.exists(SCRIPT_FILE):
        os.chmod(SCRIPT_FILE, 0o755)
    else:
        with open(LOG_FILE, "w") as out_file:
            out_file.write(f"Erro Crítico: O script {SCRIPT_FILE} não foi encontrado.\\n")
        return -1

    # Inicia de forma isolada (daemon) para não morrer com o webserver
    out_file = open(LOG_FILE, "w")
    proc = subprocess.Popen(
        [SCRIPT_FILE],
        stdout=out_file,
        stderr=subprocess.STDOUT,
        start_new_session=True
    )
    return proc.pid

async def stream_logs():
    if not os.path.exists(LOG_FILE):
        yield {"data": "Aguardando inicio da instalacao...\n"}
        while not os.path.exists(LOG_FILE):
            await asyncio.sleep(0.5)

    with open(LOG_FILE, "r") as f:
        while True:
            line = f.readline()
            if not line:
                await asyncio.sleep(0.5)
                continue
            
            yield {"data": line.strip()}
            if "Instalação concluída" in line:
                yield {"data": "INSTALLATION_COMPLETE"}
                break
