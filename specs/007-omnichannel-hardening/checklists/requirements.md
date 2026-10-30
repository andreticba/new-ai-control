<!-- requirements.md | Vitalia SDD v0.6.0 | 21-10-2026 19:59:00(GMT-04:00) -->
> **requirements.md | Vitalia SDD v0.6.0 | 21-10-2026 19:59:00(GMT-04:00)**

# Checklist de Requisitos: 007-omnichannel-hardening

Este checklist valida se a especificação da feature `007-omnichannel-hardening` atende a todos os critérios de qualidade formal antes da aprovação e transição para o planejamento técnico.

---

## 1. Completude e Clareza

- [x] O documento possui cabeçalho formal com timestamp `DD-MM-YYYY HH:MM(GMT-04:00)` e versão do Vitalia SDD.
- [x] O objetivo da feature está claramente delimitado a partir dos diagnósticos empíricos reais dos testes com o smartphone.
- [x] Todos os Requisitos Funcionais (FR-001 a FR-007) possuem descrição inequívoca, declaração de impacto ao usuário (P02) e conformidade constitucional explícita.
- [x] Os Critérios de Sucesso (SC-001 a SC-006) são quantificáveis e testáveis.
- [x] Os Cenários de Aceitação seguem o formato formal Given / When / Then cobrindo o caminho feliz e os caminhos de falha (instância desconectada, segredos em log, leads globais).

## 2. Segurança, Privacidade e Não-Vazamento (P07, P12)

- [x] O mascaramento de query strings e headers com credenciais (`apikey`, `password`, `token`) está especificado para impedir vazamento em logs HTTP e Daphne.
- [x] A higienização de logs do Webhook Gateway protege estritamente números de telefone (PII) e tokens de instâncias.
- [x] A comunicação por WebSockets contempla proteção contra exposição de tokens JWT em URLs.

## 3. Resiliência Operacional e Performance (P04, P15)

- [x] O descarte silencioso em $O(1)$ de eventos de telemetria desnecessários (`presence.update`, etc.) previne sobrecarga inútil no Celery.
- [x] O tratamento de confirmação da Evolution API garante que nenhuma mensagem com falso status de entrega seja gerada em caso de falha de conexão.
- [x] A política de CORS é expandida para suportar `127.0.0.1:3000` e evitar que atendentes recebam "Network Error".

## 4. Integração Arquitetural e Suporte a Leads Globais

- [x] O modelo de dados especifica a governança de mensagens para conversas associadas à Organização Padrão da plataforma (P07).
- [x] O ciclo de vida do modal de pareamento WhatsApp contempla auto-close reativo e atualização limpa de QR Code.
- [x] O diagrama de sequência documenta com precisão o fluxo síncrono de confirmação da Evolution API.

## 5. Governança de Arquitetura Limpa e Princípio de Responsabilidade Única (SRP)

- [x] FR-008 e SC-007 delimitam a separação estrita de responsabilidades: Views DRF magras (< 35 linhas), Service Layer dedicada e middlewares desacoplados.
- [x] O frontend preserva componentes focados (< 120 linhas) com isolamento de efeitos colaterais e conexões em Custom Hooks reutilizáveis.
- [x] É proibida a criação de novos arquivos monolíticos ou mistura de chamadas de transporte em componentes visuais.
