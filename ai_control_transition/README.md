# AI Control Installer

Este é um micro-servidor efêmero para guiar a instalação segura do AI Control e autogerar variáveis criptográficas obrigatórias antes de subir os containers.

## Como Executar

1. Dê permissão de execução:
   ```bash
   chmod +x ai_control_transition/setup.sh
   ```
2. Execute o instalador:
   ```bash
   ./ai_control_transition/setup.sh
   ```
3. O terminal exibirá um link seguro com um token OTP (One-Time Password).
4. Clique no link para abrir a interface no navegador.
5. Verifique e salve as configurações (variáveis de ambiente do `.env`).
6. Acompanhe a instalação em tempo real pelo painel de logs.
7. Quando finalizado, você pode fechar o navegador e o terminal do instalador de forma segura.
