# ChargeGrid Assistant — GoodWe EV Challenge 2026
Chatbot inteligente voltado ao suporte operacional de eletropostos comerciais no contexto do EV Challenge 2026 proposto pela GoodWe.

---
## INTEGRANTES:
- Pedro Ferreras — RM 568713
- Pedro Santos — RM 571017
- Victor Binot — RM 571499
- Gustavo Kunitaki — RM 571400
- Kauanne Oliveira - RM 574191
- Nayhely Estela - 571416

---
## PROBLEMA ABORDADO:
Com o crescimento da mobilidade elétrica, eletropostos comerciais passaram a operar múltiplos carregadores simultaneamente, gerando desafios relacionados à gestão energética e operacional.
O desafio ChargeGrid Intelligence destaca a ausência de mecanismos integrados capazes de:

- Orquestrar potência elétrica entre carregadores
- Monitorar ciclos de carregamento
- Apoiar processos de faturamento
- Centralizar comunicação operacional
---
## PROPOSTA DO CHATBOT:
O chatbot permitirá interação em linguagem natural para:

- Consultar status dos carregadores;
- Monitorar consumo energético;
- Apoiar decisões de Smart Charging;
- Identificar falhas operacionais;
- Auxiliar operadores na gestão diária do eletroposto.

O objetivo é centralizar informações técnicas e facilitar decisões operacionais em tempo real.

---

## PERSONA DEFINIDA:
Operador Comercial de Eletroposto
Profissional responsável pela operação diária de estações de carregamento em ambientes comerciais, realizando monitoramento dos carregadores, acompanhamento do consumo energético e tomada de decisões para evitar sobrecarga elétrica e garantir eficiência operacional.

---

## TECNOLOGIAS SELECIONADAS E JUSTIFICATIVA TÉCNICA: 

| Tecnologia | Justificativa Técnica |
|------------|-----------------------|
| OpenAI API | Modelo de linguagem avançado para compreensão e geração de respostas contextualizadas |
| Python | Linguagem flexível para integração entre APIs e serviços |
| OCPP 1.6J / 2.0.1 | Protocolo padrão de comunicação entre carregadores e sistemas de gestão |
| Smart Meter | Monitoramento contínuo da demanda energética |
| GitHub | Organização, versionamento e documentação do projeto |

---

---

## FUNCIONALIDADES IMPLEMENTADAS NA SPRINT 2:

- Chatbot funcional em Python
- Memória de contexto com histórico de mensagens
- Injeção de contexto via system prompt
- Few-shot prompting
- Registro automático de conversas em arquivo TXT
- Simulação operacional de eletroposto comercial
- Respostas contextualizadas para operadores comerciais

---

## ESTRUTURA DO PROJETO:

```bash
Sprint--Chatbot/
│
├── chatbot.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
│
├── docs/
│   ├── ChargeGrid.draw.io.png
│   ├── modelo_teste.md
│   ├── system_prompt.md
│   └── testes.md
```

---

## EXECUÇÃO DO PROJETO:

1. Instalar as dependências:

```bash
pip install -r requirements.txt
```

2. Criar um arquivo `.env` utilizando o modelo disponível em:

```bash
.env.example
```

Substituir:

```env
OLLAMA_API_KEY=sua_chave_aqui
```

pela chave válida da API utilizada.

3. Executar o chatbot:

```bash
python chatbot.py
```

---

## EXEMPLOS DE PERGUNTAS:

```text
Qual o status dos carregadores?
```

```text
Existe risco de sobrecarga?
```

```text
Qual carregador está em falha?
```

```text
Qual o consumo atual?
```

```text
Quantos carregamentos estão ativos?
```

---

## CONTEXTO OPERACIONAL SIMULADO:

- Carregador 1: ativo
- Carregador 2: falha de comunicação OCPP
- Carregador 3: ativo
- Carregador 4: ativo
- Carregador 5: manutenção preventiva

Consumo energético atual: 87 kW  
Capacidade contratada: 96 kW  
Sessões de carregamento ativas: 3

---

## DOCUMENTAÇÃO:

- Fluxograma do sistema:

```bash
docs/ChargeGrid.draw.io.png
```

- Modelo de testes:

```bash
docs/modelo_teste.md
```

- System prompt:

```bash
docs/system_prompt.md
```

- Testes executados:

```bash
docs/testes.md
```

---

## OBSERVAÇÕES:

O arquivo `.env` não deve ser enviado ao GitHub por conter informações sensíveis da API.
