"""
Gera os 4 documentos da base de conhecimento (data/knowledge_base/) usados
pelo pipeline RAG da Sprint 04.

Conteúdo FICTÍCIO, criado para fins acadêmicos (EV Challenge GoodWe), mas
mantendo consistência com os dados já usados no chatbot desde a Sprint 2
(5 carregadores, 87 kW de consumo, 96 kW de capacidade contratada, etc.).
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem

styles = getSampleStyleSheet()
titulo = ParagraphStyle("T", parent=styles["Title"], fontSize=15, spaceAfter=6)
h1 = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=12, spaceBefore=12, spaceAfter=5)
h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=10.5, spaceBefore=8, spaceAfter=4)
corpo = ParagraphStyle("C", parent=styles["Normal"], fontSize=9.5, leading=13, spaceAfter=6)

from pathlib import Path

PASTA = Path(__file__).parent / "data" / "knowledge_base"
PASTA.mkdir(parents=True, exist_ok=True)


def gerar_manual_produto():
    story = [
        Paragraph("Manual do Produto - ChargeGrid EV ChargeOps", titulo),
        Paragraph("GoodWe Brasil - Documentação Técnica - Versão 2.3 (2026)", corpo),
        Paragraph("1. Visão geral do sistema", h1),
        Paragraph(
            "O ChargeGrid EV ChargeOps é a plataforma de gestão de eletropostos comerciais "
            "da GoodWe, projetada para orquestrar múltiplos pontos de recarga simultaneamente. "
            "O sistema padrão de referência opera com 5 carregadores por estação, com "
            "capacidade contratada de 96 kW e suporte a Smart Charging dinâmico.",
            corpo
        ),
        Paragraph("2. Especificações técnicas dos carregadores", h1),
        Paragraph(
            "Cada carregador ChargeGrid suporta os protocolos OCPP 1.6J e OCPP 2.0.1 para "
            "comunicação com o sistema de gestão central. A potência máxima por carregador "
            "é de 22 kW em corrente alternada (AC) ou 60 kW em corrente contínua (DC), "
            "dependendo do modelo instalado. O tempo médio de resposta a comandos remotos "
            "(iniciar/parar sessão) é de até 3 segundos em condições normais de rede.",
            corpo
        ),
        Paragraph("3. Smart Charging", h1),
        Paragraph(
            "O módulo de Smart Charging ajusta dinamicamente a potência entregue a cada "
            "carregador com base na demanda total da estação e na capacidade contratada. "
            "Quando o consumo agregado ultrapassa 90% da capacidade contratada, o sistema "
            "reduz automaticamente a potência de carregadores em sessões de menor prioridade "
            "para evitar sobrecarga e cobrança de multa por ultrapassagem de demanda junto "
            "à concessionária de energia.",
            corpo
        ),
        Paragraph("4. Diagnóstico de falhas", h1),
        Paragraph(
            "Falhas de comunicação OCPP são o tipo de falha mais comum reportado pelos "
            "carregadores ChargeGrid. Quando um carregador perde a comunicação com o "
            "sistema central por mais de 60 segundos, ele é automaticamente marcado como "
            "'falha de comunicação OCPP' no painel do operador. O operador deve verificar "
            "a conectividade de rede (Wi-Fi ou 4G, dependendo do modelo) e, caso a falha "
            "persista, abrir chamado técnico -- a reinicialização do módulo de comunicação "
            "deve ser feita apenas por um técnico habilitado, não pelo operador da estação.",
            corpo
        ),
        Paragraph("5. Manutenção preventiva", h1),
        Paragraph(
            "A manutenção preventiva dos carregadores ChargeGrid deve ser realizada a cada "
            "6 meses ou 5.000 sessões de carregamento, o que ocorrer primeiro. Durante a "
            "manutenção, o carregador é colocado no status 'manutenção preventiva' e fica "
            "indisponível para novas sessões. A manutenção inclui inspeção do cabo de "
            "carregamento, calibração do medidor de energia e atualização de firmware.",
            corpo
        ),
    ]
    doc = SimpleDocTemplate(str(PASTA / "manual_chargegrid.pdf"), pagesize=A4,
                             topMargin=2*cm, bottomMargin=2*cm, leftMargin=2*cm, rightMargin=2*cm)
    doc.build(story)


def gerar_regimento_condominial():
    story = [
        Paragraph("Regimento de Carregamento Compartilhado em Condomínios", titulo),
        Paragraph("GoodWe Brasil - Modelo de Regimento Interno - Versão 1.4 (2026)", corpo),
        Paragraph("1. Finalidade", h1),
        Paragraph(
            "Este regimento estabelece as regras de uso compartilhado dos carregadores "
            "ChargeGrid instalados em áreas comuns de condomínios residenciais e comerciais, "
            "garantindo acesso justo a todos os moradores/usuários cadastrados.",
            corpo
        ),
        Paragraph("2. Reserva de horário", h1),
        Paragraph(
            "Cada unidade cadastrada pode reservar um carregador por até 4 horas consecutivas "
            "através do aplicativo do condomínio. Reservas não utilizadas nos primeiros 15 "
            "minutos do horário reservado são automaticamente canceladas, liberando o "
            "carregador para uso por outro morador.",
            corpo
        ),
        Paragraph("3. Uso justo (fair use)", h1),
        Paragraph(
            "É vedado o uso do carregador além do horário reservado quando houver fila de "
            "espera de outros moradores. O sistema envia uma notificação ao usuário 10 "
            "minutos antes do fim do horário reservado. Em caso de reincidência (3 ou mais "
            "ocorrências no mês), a unidade pode ter a prioridade de reserva reduzida por "
            "30 dias, mediante decisão do síndico.",
            corpo
        ),
        Paragraph("4. Faturamento e rateio", h1),
        Paragraph(
            "O consumo de energia de cada sessão é registrado individualmente por unidade "
            "e faturado de acordo com a tarifa vigente (ver tabela tarifária). Não há "
            "rateio do custo de energia entre unidades que não utilizam os carregadores -- "
            "o custo de manutenção da infraestrutura, porém, é rateado entre todas as "
            "unidades do condomínio conforme convenção condominial.",
            corpo
        ),
        Paragraph("5. Prioridades e exceções", h1),
        Paragraph(
            "Veículos de emergência ou de uso profissional comprovado (entrega, serviço de "
            "saúde) têm prioridade de uso sobre reservas comuns, mediante cadastro prévio "
            "junto à administração do condomínio. Situações de falha do carregador (ver "
            "manual técnico ChargeGrid) não geram direito a compensação de horário, mas "
            "devem ser reportadas à administração para abertura de chamado técnico.",
            corpo
        ),
    ]
    doc = SimpleDocTemplate(str(PASTA / "regimento_condominial.pdf"), pagesize=A4,
                             topMargin=2*cm, bottomMargin=2*cm, leftMargin=2*cm, rightMargin=2*cm)
    doc.build(story)


def gerar_faq():
    perguntas = [
        ("Como inicio uma sessão de carregamento?",
         "Aproxime o cartão RFID ou use o aplicativo ChargeGrid para autenticar no "
         "carregador desejado. A sessão inicia automaticamente após a autenticação e a "
         "conexão do cabo ao veículo."),
        ("O que fazer se o carregador estiver com falha?",
         "Verifique se o status exibido é 'falha de comunicação OCPP'. Nesse caso, aguarde "
         "alguns minutos e tente novamente; se persistir, reporte pelo aplicativo ou entre "
         "em contato com o operador da estação. Não tente reiniciar o equipamento "
         "manualmente sem orientação de um técnico."),
        ("Como funciona o Smart Charging?",
         "O Smart Charging ajusta automaticamente a potência entregue a cada carregador "
         "conforme a demanda total da estação, evitando ultrapassar a capacidade "
         "contratada. Isso pode reduzir temporariamente a velocidade de carregamento em "
         "horários de pico."),
        ("Posso agendar um horário de carregamento?",
         "Sim, em estações com o módulo de reserva habilitado (ver regimento de "
         "carregamento compartilhado, quando aplicável). O agendamento é feito pelo "
         "aplicativo, com até 4 horas de duração por reserva."),
        ("Como é calculado o valor da minha sessão de carregamento?",
         "O valor é calculado multiplicando a energia consumida (em kWh) pela tarifa "
         "vigente no horário da sessão (normal ou pico). Consulte a tabela tarifária "
         "para os valores atualizados."),
        ("O que acontece se eu ultrapassar meu horário reservado?",
         "Se houver fila de espera, você recebe uma notificação 10 minutos antes do fim do "
         "horário. Reincidências podem afetar sua prioridade de reserva nos próximos 30 "
         "dias, conforme o regimento de carregamento compartilhado."),
    ]
    story = [
        Paragraph("Perguntas Frequentes - Carregamento ChargeGrid", titulo),
        Paragraph("GoodWe Brasil - FAQ para Operadores e Usuários - Versão 1.1 (2026)", corpo),
    ]
    for pergunta, resposta in perguntas:
        story.append(Paragraph(pergunta, h2))
        story.append(Paragraph(resposta, corpo))
    doc = SimpleDocTemplate(str(PASTA / "faq_carregamento.pdf"), pagesize=A4,
                             topMargin=2*cm, bottomMargin=2*cm, leftMargin=2*cm, rightMargin=2*cm)
    doc.build(story)


def gerar_tabela_tarifaria():
    story = [
        Paragraph("Tabela Tarifária - Estações ChargeGrid", titulo),
        Paragraph("GoodWe Brasil - Vigência 2026 - Versão 1.2", corpo),
        Paragraph("1. Tarifas por horário", h1),
        Paragraph(
            "As tarifas de energia para sessões de carregamento variam conforme o horário "
            "do dia, refletindo o custo de demanda da concessionária local.",
            corpo
        ),
    ]
    dados = [
        ["Faixa horária", "Horário", "Tarifa (R$/kWh)"],
        ["Normal", "00h às 18h", "R$ 1,20"],
        ["Pico", "18h às 21h", "R$ 1,65"],
        ["Normal (noite)", "21h às 00h", "R$ 1,20"],
    ]
    tabela = Table(dados, colWidths=[5*cm, 6*cm, 5*cm])
    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(tabela)
    story.append(Spacer(1, 10))
    story.append(Paragraph("2. Capacidade contratada e multas por ultrapassagem", h1))
    story.append(Paragraph(
        "A capacidade contratada padrão de uma estação ChargeGrid de 5 carregadores é de "
        "96 kW. Ultrapassagens da demanda contratada junto à concessionária geram multa "
        "adicional de R$ 15,00 por kW excedente, registrada no ciclo de faturamento "
        "seguinte. O módulo de Smart Charging existe justamente para minimizar o risco "
        "dessa ultrapassagem.",
        corpo
    ))
    story.append(Paragraph("3. Taxa de manutenção da infraestrutura", h1))
    story.append(Paragraph(
        "Em condomínios, uma taxa mensal de R$ 25,00 por unidade cadastrada é cobrada para "
        "manutenção da infraestrutura de carregamento compartilhado, independentemente do "
        "uso efetivo no mês, conforme previsto no regimento de carregamento compartilhado.",
        corpo
    ))
    doc = SimpleDocTemplate(str(PASTA / "tabela_tarifaria.pdf"), pagesize=A4,
                             topMargin=2*cm, bottomMargin=2*cm, leftMargin=2*cm, rightMargin=2*cm)
    doc.build(story)


if __name__ == "__main__":
    gerar_manual_produto()
    gerar_regimento_condominial()
    gerar_faq()
    gerar_tabela_tarifaria()
    print("4 PDFs gerados em", PASTA)