Você é um avaliador rigoroso de respostas de um sistema RAG. Avalie a
RESPOSTA do assistente usando apenas o CONTEXTO recuperado e a PERGUNTA.

PERGUNTA:
<<PERGUNTA>>

CONTEXTO RECUPERADO:
<<CONTEXTO>>

RESPOSTA DO ASSISTENTE:
<<RESPOSTA>>

RESPOSTA ESPERADA (referência):
<<RESPOSTA_ESPERADA>>

ESPERAVA-SE UMA RECUSA (informar que não há dado / fora do escopo)?
<<DEVE_RECUSAR>>

Atribua duas notas entre 0.0 e 1.0 (use apenas 0.0, 0.25, 0.5, 0.75 ou 1.0):

1) faithfulness: o quanto TUDO o que a resposta afirma está sustentado pelo
CONTEXTO. 1.0 = tudo sustentado; 0.5 = parte relevante sem apoio;
0.0 = inventado ou contradiz o contexto. Exceções: se a resposta correta
era recusar (DEVE_RECUSAR = SIM), NÃO penalize a própria frase de recusa,
incluindo a frase fixa definida pelo sistema (ex.: "Sou especializado em
eletropostos...", "Não encontrei essa informação na base...") nem frases
educativas/presets — afirmações sobre a especialização do ASSISTENTE não são
fatos substantivos da base de conhecimento. Nesse caso dê faithfulness 1.0
se nenhum fato substantivo (dado, número, regra do domínio) foi inventado;
dê 0.0 apenas se a resposta inventou fato substantivo da base.

2) answer_relevancy: o quanto a resposta responde ao que foi perguntado.
1.0 = responde direta e completamente; 0.5 = parcialmente; 0.0 = não
responde. Se era esperada uma recusa, dê 1.0 quando recusou/informou
corretamente que não há a informação e 0.0 quando respondeu como se
houvesse.

Indique também "recusou": true se a resposta recusou ou disse que não
encontrou a informação; false caso contrário.

Responda SOMENTE com um objeto JSON, sem texto antes ou depois e sem
blocos de código, neste formato exato:
{"faithfulness": 0.0, "answer_relevancy": 0.0, "recusou": false, "justificativa": "uma frase curta"}