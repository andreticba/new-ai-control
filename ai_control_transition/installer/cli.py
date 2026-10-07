# installer/cli.py | Vitalia SDD v0.6.0 | 06-10-2026 16:05(GMT-04:00)
import argparse
import uuid
import os
import uvicorn

def main():
    parser = argparse.ArgumentParser(description="AI Control Installer CLI")
    parser.add_argument("--host", default="0.0.0.0", help="Host para rodar o servidor")
    parser.add_argument("--port", type=int, default=8000, help="Porta para rodar o servidor")
    args = parser.parse_args()
    
    otp_token = str(uuid.uuid4())
    os.environ["AI_CONTROL_OTP"] = otp_token
    
    print("\n" + "="*60)
    print("=> Iniciando configuração do AI Control Installer...")
    print("=> ACESSE ESTE LINK PARA CONTINUAR A INSTALAÇÃO:")
    print(f"=> http://{args.host}:{args.port}/?token={otp_token}")
    print("="*60 + "\n")
    
    uvicorn.run("ai_control_transition.installer.server:app", host=args.host, port=args.port, reload=False)

if __name__ == "__main__":
    main()
