<!-- catalogo_modelos_ollama.md | Vitalia SDD v0.6.0 | 22-10-2026 15:23:00(GMT-04:00) -->
> **catalogo_modelos_ollama.md | Vitalia SDD v0.6.0 | 22-10-2026 15:23:00(GMT-04:00)**

# Catálogo de Modelos Locais Ollama (Biblioteca Oficial)
## Dimensionamento por Perfil de Hardware, VRAM e Casos de Uso no AI-Control

Este documento cataloga os modelos recomendados da biblioteca oficial do [Ollama](https://ollama.com/library), calibrados especificamente para a arquitetura de hardware do servidor local e para as demandas dos módulos do sistema (**Copiloto Omnichannel / WhatsApp**, **RAG no PostgreSQL pgvector**, **Agentes** e **Open WebUI**).

---

## 1. Diagnóstico do Ambiente de Hardware

A máquina host e o container `ai-control_ollama` operam sob as seguintes restrições de memória e processamento:

- **GPU:** NVIDIA GeForce GTX 1060 6GB GDDR5 (*Arquitetura Pascal, Compute Capability 6.1*)
  - VRAM Total: `6.144 MiB (~6.0 GB)`
  - VRAM em uso pelo sistema/desktop: `~600 MiB`
  - **VRAM líquida para o Ollama:** **`~5.4 GB`**
  - Aceleração CUDA: Ativa no container via NVIDIA Container Toolkit
- **Processador (CPU):** Intel(R) Core(TM) i7-6700 @ 3.40GHz (4 núcleos / 8 threads)
- **Memória RAM:** 16 GB DDR4 (*~11 GB livres para offload e buffers*)
- **Armazenamento:** Volume Docker persistente `ollama_data` em SSD com mais de 900 GB disponíveis

### ⚖️ Diretrizes de Alocação de Memória

| Faixa de Modelo | Tamanho (Q4_K_M) | Alocação no Hardware | Throughput Estimado | Indicação |
| :--- | :---: | :--- | :---: | :--- |
| **Ultraleve (1B - 2B)** | ~0.9 GB a 1.3 GB | **100% VRAM (GPU)** | 45 - 65 tokens/s | Triagem, classificação e guardrails instantâneos |
| **Leve (3B - 4B)** | ~1.9 GB a 2.5 GB | **100% VRAM (GPU)** | 30 - 45 tokens/s | **Padrão Ouro Copiloto WhatsApp (Tempo Real)** |
| **Médio (7B - 8B)** | ~4.4 GB a 5.0 GB | **Híbrido (GPU + RAM)** | 10 - 20 tokens/s | **Padrão Ouro Open WebUI, RAG e Raciocínio** |
| **Pesado (> 14B)** | > 8.5 GB | Predominante na CPU/RAM | < 4 tokens/s | *Não recomendado para uso diário* |

---

## 2. Catálogo Especializado por Caso de Uso

### 2.1. ⚡ Copiloto de Atendimento Omnichannel & WhatsApp
Modelos focados em geração rápida de sugestão de mensagens para operadores, resumo de tickets e resposta conversacional fluida em português.

| Modelo Oficial | Parâmetros | Tamanho | VRAM | Benefícios e Especialidade |
| :--- | :---: | :---: | :---: | :--- |
| `qwen2.5:3b` | 3.1B | ~1.9 GB | 100% GPU | **(Recomendado)** Excepcional fluência em português, ótimo seguimento de instruções (instruction-following). |
| `phi4-mini:latest` | 3.8B | ~2.5 GB | 100% GPU | Síntese concisa da Microsoft com alta pontuação em lógica e formatação direta. |
| `llama3.2:3b` | 3.2B | ~2.0 GB | 100% GPU | Compreensão de contexto conversacional empático e atendimento ao cliente. |

```bash
# Pull dos modelos de copiloto
docker exec -it ai-control_ollama ollama pull qwen2.5:3b
docker exec -it ai-control_ollama ollama pull phi4-mini:latest
docker exec -it ai-control_ollama ollama pull llama3.2:3b
```

---

### 2.2. 🔍 Embeddings & Busca Vetorial RAG (PostgreSQL pgvector / Open WebUI)
Modelos dedicados à transformação de textos e documentos em vetores matemáticos densos para indexação semântica.

| Modelo Oficial | Parâmetros | Tamanho | VRAM | Benefícios e Especialidade |
| :--- | :---: | :---: | :---: | :--- |
| `nomic-embed-text` | 137M | ~274 MB | < 400 MB | **(Padrão Open WebUI)** Janela de 8.192 tokens; ideal para chunking de bases de conhecimento. |
| `mxbai-embed-large`| 334M | ~670 MB | < 800 MB | Alta densidade semântica para buscas de artigos e manuais complexos. |

```bash
# Pull dos modelos de embedding
docker exec -it ai-control_ollama ollama pull nomic-embed-text
docker exec -it ai-control_ollama ollama pull mxbai-embed-large
```

---

### 2.3. 🧠 Chat Geral, Análises Complexas & Agentes (Open WebUI - Porta 4000)
Modelos de maior capacidade cognitiva para redação de relatórios, análises aprofundadas e discussões multidisciplinares.

| Modelo Oficial | Parâmetros | Tamanho | VRAM / RAM | Benefícios e Especialidade |
| :--- | :---: | :---: | :---: | :--- |
| `qwen2.5:7b` | 7.6B | ~4.7 GB | Híbrido | **(Estado da Arte 7B)** Melhor modelo de uso geral compacto do mundo, excelente raciocínio. |
| `llama3.1:8b` | 8.0B | ~4.7 GB | Híbrido | Modelo canônico da Meta com suporte nativo a contexto estendido de até 128k tokens. |
| `mistral:7b` | 7.2B | ~4.1 GB | Híbrido | Respostas rápidas e estruturadas em tópicos para resumos corporativos. |

```bash
# Pull dos modelos gerais
docker exec -it ai-control_ollama ollama pull qwen2.5:7b
docker exec -it ai-control_ollama ollama pull llama3.1:8b
```

---

### 2.4. 💻 Programação, SQL, Refatoração & Scripts (Coding Copilot)
Treinados exaustivamente em código-fonte, sintaxe e regras de compiladores.

| Modelo Oficial | Parâmetros | Tamanho | VRAM / RAM | Benefícios e Especialidade |
| :--- | :---: | :---: | :---: | :--- |
| `qwen2.5-coder:3b` | 3.1B | ~1.9 GB | 100% GPU | Geração ultrarrápida de scripts Python, TypeScript e queries SQL. |
| `qwen2.5-coder:7b` | 7.6B | ~4.7 GB | Híbrido | **(Recomendado para Dev)** Capacidade de refatoração de código complexo e criação de suítes de testes. |

```bash
# Pull dos modelos de programação
docker exec -it ai-control_ollama ollama pull qwen2.5-coder:3b
docker exec -it ai-control_ollama ollama pull qwen2.5-coder:7b
```

---

### 2.5. 🔬 Raciocínio com Cadeia de Pensamento (Reasoning / Thinking)
Modelos especializados em resolver problemas complexos com etapas de reflexão explícitas (`<think>...</think>`).

| Modelo Oficial | Parâmetros | Tamanho | VRAM / RAM | Benefícios e Especialidade |
| :--- | :---: | :---: | :---: | :--- |
| `deepseek-r1:1.5b` | 1.8B | ~1.1 GB | 100% GPU | Raciocínio lógico em cadeia com altíssima velocidade na GTX 1060. |
| `deepseek-r1:7b` | 7.6B | ~4.7 GB | Híbrido | **(Poder Lógico)** Capacidade dedutiva comparável a modelos proprietários maiores. |

```bash
# Pull dos modelos de raciocínio
docker exec -it ai-control_ollama ollama pull deepseek-r1:1.5b
docker exec -it ai-control_ollama ollama pull deepseek-r1:7b
```

---

### 2.6. 🚀 Ultraleves: Triagem, Extração e Roteamento
Modelos ultracompactos para classificação semântica com latência inferior a 300ms.

| Modelo Oficial | Parâmetros | Tamanho | VRAM | Benefícios e Especialidade |
| :--- | :---: | :---: | :---: | :--- |
| `qwen2.5:1.5b` | 1.5B | ~980 MB | 100% GPU | Classificador de intenções, análise de sentimento e rotulagem instantânea. |
| `llama3.2:1b` | 1.2B | ~1.3 GB | 100% GPU | Extração pontual de entidades (nomes, números de pedido, telefones, datas). |

```bash
# Pull dos modelos ultraleves
docker exec -it ai-control_ollama ollama pull qwen2.5:1.5b
docker exec -it ai-control_ollama ollama pull llama3.2:1b
```

---

## 3. Lote Recomendado ("Kit de Inicialização Ideal")

Para inicializar seu ambiente com cobertura total de funcionalidades sem consumir espaço ou tempo de download excessivos:

```bash
# 1. RAG e Busca Semântica no PostgreSQL
docker exec -it ai-control_ollama ollama pull nomic-embed-text

# 2. Copiloto de Atendimento WhatsApp (100% na VRAM da GTX 1060)
docker exec -it ai-control_ollama ollama pull qwen2.5:3b

# 3. Inteligência e Chat Geral no Open WebUI (Porta 4000)
docker exec -it ai-control_ollama ollama pull qwen2.5:7b

# 4. Raciocínio Lógico e Planejamento
docker exec -it ai-control_ollama ollama pull deepseek-r1:1.5b
```

### Comandos de Gestão Operacional do Ollama

```bash
# Listar modelos baixados e armazenados no volume persistente
docker exec -i ai-control_ollama ollama list

# Testar inferência interativa diretamente no terminal
docker exec -it ai-control_ollama ollama run qwen2.5:3b "Olá! Qual o seu modelo e como pode me ajudar?"

# Remover um modelo para liberar espaço
docker exec -i ai-control_ollama ollama rm <nome_do_modelo>
```
