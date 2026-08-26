# Testes do Chatbot - Sprint 2

## Testes Funcionais

| Pergunta | Resposta Obtida | Avaliação |
|---|---|---|
| Qual o status dos carregadores? | O sistema informou 3 carregadores ativos, 1 em falha de comunicação OCPP e 1 em manutenção preventiva. | Adequada |
| Existe risco de sobrecarga? | O chatbot informou consumo de 87 kW de 96 kW (90,6%), indicando risco moderado de sobrecarga, e recomendou aplicação de Smart Charging. | Adequada |
| Qual carregador está em falha? | O chatbot identificou falha de comunicação OCPP no Carregador 2, informando que está temporariamente indisponível. | Adequada |
| Qual o consumo atual? | O chatbot informou consumo energético atual de 87 kW. | Adequada |
| Quantos carregamentos estão ativos? | O chatbot informou 3 sessões de carregamento ativas no momento. | Adequada |

## Testes de Variação de Linguagem

| Pergunta | Resposta Obtida | Avaliação |
|---|---|---|
| Os carregadores estão funcionando? | O chatbot apresentou o status individual de cada carregador: 3 ativos, 1 com falha OCPP e 1 em manutenção preventiva. | Adequada |
| Estamos perto do limite de energia? | O chatbot informou consumo de 87 kW frente à capacidade de 96 kW (90,6%), classificou a situação como próxima ao limite com risco moderado de sobrecarga e sugeriu aplicação de Smart Charging e monitoramento contínuo. | Adequada |

## Testes Fora de Escopo

| Pergunta | Resposta Obtida | Avaliação |
|---|---|---|
| Qual a previsão do tempo? | O chatbot informou que seu escopo está limitado ao suporte operacional dos eletropostos GoodWe e que não dispõe de informações meteorológicas. | Adequada |
| Quem fundou a empresa? | O chatbot informou que seu escopo está restrito ao suporte operacional dos eletropostos GoodWe e que não dispõe de informações sobre a fundação da empresa. | Adequada |
