# installer/config_manager.py | Vitalia SDD v0.6.0 | 06-10-2026 17:08(GMT-04:00)
import os
import secrets
import shutil
from dotenv import dotenv_values, set_key

ENV_PATH = ".env"
EXAMPLE_PATH = ".env.example"

def _generate_secret():
    return secrets.token_hex(32)

def load_config():
    # Se .env não existe mas .env.example sim, copia o arquivo inteiro para preservar comentários
    if not os.path.exists(ENV_PATH) and os.path.exists(EXAMPLE_PATH):
        shutil.copy(EXAMPLE_PATH, ENV_PATH)

    # Carrega a base do .env.example para ter todas as chaves possíveis na UI
    config = dotenv_values(EXAMPLE_PATH) if os.path.exists(EXAMPLE_PATH) else {}
    # Atualiza com os valores reais que já estão no .env
    if os.path.exists(ENV_PATH):
        config.update(dotenv_values(ENV_PATH))

    # Auto-gerar chaves se ausentes
    keys_to_generate = ["CRYPTO_KEY_PATH", "CONTEXT_ENCRYPTION_KEY", "DJANGO_SECRET_KEY"]
    modified_keys = {}
    for key in keys_to_generate:
        if not config.get(key):
            new_val = _generate_secret()
            config[key] = new_val
            modified_keys[key] = new_val

    if modified_keys:
        save_config(modified_keys)

    return config

def save_config(config_dict):
    if not os.path.exists(ENV_PATH):
        open(ENV_PATH, 'a').close()
        
    # set_key atualiza o arquivo de forma cirúrgica, preservando TODOS os comentários e linhas em branco!
    for k, v in config_dict.items():
        set_key(ENV_PATH, k, str(v) if v is not None else "")
