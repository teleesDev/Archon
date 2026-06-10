"""
seed_demo.py
────────────
Popula o banco do Archon com dados 100% FICTÍCIOS para screenshots,
GIFs e demonstrações públicas (GitHub / LinkedIn).

ATENÇÃO:
    - Apague (ou renomeie) o advocacia.db real antes de rodar,
      para o demo começar limpo:  ren advocacia.db advocacia_REAL.db
    - Depois das capturas, restaure o banco real.

Uso:
    python seed_demo.py
"""

import os
import sys
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

from database.database import (
    criar_tabelas,
    criar_tabela_agenda,
    adicionar_cliente,
    adicionar_processo,
    adicionar_transacao,
    adicionar_evento_agenda,
    sincronizar_associacoes,
    buscar_processos,
    conectar,
)


# ── Clientes fictícios ────────────────────────────────────────────────────────
# (tipo, nome, doc, rg, telefone, email, profissao, est_civil, naturalidade, endereco, estado, tipo_unidade, responsavel, obs)

CLIENTES = [
    ("Pessoa Física", "Ricardo Albuquerque Neves", "111.222.333-44", "22.333.444-5",
     "(11) 98765-1234", "ricardo.neves@email.com", "Engenheiro Civil", "Casado",
     "São Paulo - SP", "Rua das Acácias, 120 - Vila Mariana", "", "", "",
     "Cliente indicado pelo Dr. Fonseca. Prefere contato por e-mail."),

    ("Pessoa Física", "Camila Duarte Fontes", "222.333.444-55", "33.444.555-6",
     "(11) 97654-2345", "camila.fontes@email.com", "Arquiteta", "Solteira",
     "Campinas - SP", "Av. Brigadeiro Luís Antônio, 890 - Bela Vista", "", "", "", ""),

    ("Pessoa Física", "Eduardo Sampaio Lins", "333.444.555-66", "44.555.666-7",
     "(11) 96543-3456", "edu.lins@email.com", "Professor", "Divorciado",
     "Santos - SP", "Rua Itororó, 45 - Gonzaga", "", "", "", ""),

    ("Pessoa Física", "Beatriz Moura Castellano", "444.555.666-77", "55.666.777-8",
     "(11) 95432-4567", "bia.castellano@email.com", "Médica", "Casada",
     "Ribeirão Preto - SP", "Al. Santos, 1200 - Jardim Paulista", "", "", "", ""),

    ("Pessoa Física", "Henrique Vasconcelos Prado", "555.666.777-88", "66.777.888-9",
     "(11) 94321-5678", "henrique.prado@email.com", "Empresário", "Casado",
     "São Paulo - SP", "Rua Oscar Freire, 300 - Pinheiros", "", "", "",
     "Possui dois processos em andamento. Atenção aos prazos de maio."),

    ("Pessoa Física", "Larissa Quintela Ramos", "666.777.888-99", "77.888.999-0",
     "(11) 93210-6789", "lari.ramos@email.com", "Designer", "Solteira",
     "Sorocaba - SP", "Rua Augusta, 2500 - Consolação", "", "", "", ""),

    ("Pessoa Física", "Otávio Bezerra Caldas", "777.888.999-00", "88.999.000-1",
     "(11) 92109-7890", "otavio.caldas@email.com", "Contador", "Viúvo",
     "São Paulo - SP", "Av. Paulista, 1500 - Bela Vista", "", "", "", ""),

    ("Pessoa Física", "Sofia Mendonça Leite", "888.999.000-11", "99.000.111-2",
     "(11) 91098-8901", "sofia.leite@email.com", "Jornalista", "Casada",
     "Guarulhos - SP", "Rua Haddock Lobo, 80 - Cerqueira César", "", "", "", ""),

    ("Pessoa Jurídica", "NovaTech Sistemas LTDA", "11.222.333/0001-44", "",
     "", "contato@novatech.com.br", "", "", "", "", "São Paulo", "Matriz",
     "Marcos Vinícius Teixeira", "Contrato de assessoria mensal desde 2024."),

    ("Pessoa Jurídica", "Construtora Alvorada S/A", "22.333.444/0001-55", "",
     "", "juridico@alvorada.com.br", "", "", "", "", "São Paulo", "Filial",
     "Fernanda Costa Ribeiro", ""),
]


# ── Processos fictícios ───────────────────────────────────────────────────────
# (nome, cnj, razao, atuacao, vara, tipo_v, pct, proveito, conversao, v_fixo, parcelas, parc_pagas, status, obs)

PROCESSOS = [
    ("Ricardo Albuquerque Neves", "1000001-10.2024.8.26.0100",
     "Ação de Cobrança", "Processo completo", "3ª Vara Cível (Centro)",
     "Porcentagem", 10.0, 45000.00, 4500.00, 0, 0, 0,
     "Concluído,Pagos,Certidão Emitida",
     "Acordo homologado em audiência. Valores recebidos integralmente."),

    ("Ricardo Albuquerque Neves", "1000002-20.2024.8.26.0100",
     "Execução de Título Extrajudicial", "Negociação e Execução", "3ª Vara Cível (Centro)",
     "Porcentagem", 12.0, 30000.00, 3600.00, 0, 0, 0,
     "Em Andamento,Não Pagos,Certidão Não-Emitida", ""),

    ("Camila Duarte Fontes", "1000003-30.2024.8.26.0200",
     "Divórcio Consensual", "Processo completo", "2ª Vara de Família",
     "Fixo", 0, 0, 0, 6000.00, 6, 3,
     "Em Andamento,Não Pagos,Certidão Não-Emitida",
     "Partilha de bens em fase final de definição."),

    ("Eduardo Sampaio Lins", "1000004-40.2024.8.26.0300",
     "Indenização por Danos Morais", "Processo completo", "1ª JEC (Centro)",
     "Porcentagem", 20.0, 15000.00, 3000.00, 0, 0, 0,
     "Concluído,Pagos,Certidão Emitida", ""),

    ("Beatriz Moura Castellano", "1000005-50.2024.8.26.0400",
     "Inventário e Partilha", "Processo completo", "4ª Vara de Família",
     "Fixo", 0, 0, 0, 12000.00, 12, 12,
     "Concluído,Pagos,Certidão Emitida",
     "Inventário concluído. Formal de partilha expedido."),

    ("Henrique Vasconcelos Prado", "1000006-60.2025.8.26.0500",
     "Revisão Contratual", "Consultoria e Processo", "5ª Vara Cível",
     "Porcentagem", 15.0, 80000.00, 12000.00, 0, 0, 0,
     "Em Andamento,Não Pagos,Certidão Solicitada,Certidão Não-Emitida", ""),

    ("Henrique Vasconcelos Prado", "1000007-70.2025.8.26.0500",
     "Ação Renovatória de Aluguel", "Processo completo", "5ª Vara Cível",
     "Fixo", 0, 0, 0, 8000.00, 4, 1,
     "Em Andamento,Não Pagos,Certidão Não-Emitida", ""),

    ("Larissa Quintela Ramos", "1000008-80.2025.8.26.0600",
     "Defesa do Consumidor - Produto não entregue", "Processo completo", "2ª JEC",
     "Pro Bono", 0, 0, 0, 0, 0, 0,
     "Em Andamento,Não Pagos,Certidão Não-Emitida",
     "Atendimento pro bono. Audiência de conciliação marcada."),

    ("Otávio Bezerra Caldas", "1000009-90.2024.8.26.0700",
     "Usucapião Extraordinária", "Processo completo", "6ª Vara de Registros Públicos",
     "Fixo", 0, 0, 0, 9500.00, 10, 10,
     "Concluído,Pagos,Certidão Emitida", ""),

    ("Sofia Mendonça Leite", "1000010-01.2025.8.26.0800",
     "Ação de Alimentos", "Processo completo", "1ª Vara de Família",
     "Pro Bono", 0, 0, 0, 0, 0, 0,
     "Em Andamento,Não Pagos,Certidão Não-Emitida", ""),

    ("NovaTech Sistemas LTDA", "1000011-11.2024.8.26.0900",
     "Cobrança de Inadimplente", "Processo completo", "7ª Vara Cível Empresarial",
     "Porcentagem", 10.0, 120000.00, 12000.00, 0, 0, 0,
     "Concluído,Pagos,Certidão Emitida",
     "Recuperação integral do crédito via penhora online."),

    ("NovaTech Sistemas LTDA", "1000012-21.2025.8.26.0900",
     "Disputa Contratual - Fornecedor", "Consultoria e Processo", "7ª Vara Cível Empresarial",
     "Porcentagem", 12.0, 65000.00, 7800.00, 0, 0, 0,
     "Em Andamento,Não Pagos,Certidão Não-Emitida", ""),

    ("Construtora Alvorada S/A", "1000013-31.2025.8.26.1000",
     "Ação de Despejo por Falta de Pagamento", "Processo completo", "8ª Vara Cível",
     "Fixo", 0, 0, 0, 15000.00, 5, 2,
     "Em Andamento,Não Pagos,Certidão Não-Emitida", ""),

    ("Construtora Alvorada S/A", "1000014-41.2024.8.26.1000",
     "Embargos à Execução", "Defesa em Execução", "8ª Vara Cível",
     "Fixo", 0, 0, 0, 18000.00, 6, 6,
     "Concluído,Pagos,Certidão Emitida", ""),
]


# ── Estratégias fictícias (titulo, cnj_vinculado, prioridade, descricao) ──────

ESTRATEGIAS = [
    ("Plano de execução — NovaTech vs Fornecedor", "1000012-21.2025.8.26.0900", "Alta",
     "Descreva aqui o planejamento.\n\nCHECKLIST:\n- [x] Notificação extrajudicial enviada\n- [x] Tentativa de acordo (recusada)\n- [ ] Protocolar petição inicial\n- [ ] Requerer tutela de urgência\n- [ ] Audiência de conciliação"),

    ("Estratégia de defesa — Despejo Alvorada", "1000013-31.2025.8.26.1000", "Moderada",
     "Descreva aqui o planejamento.\n\nCHECKLIST:\n- [x] Levantamento de comprovantes de pagamento\n- [ ] Contestação com pedido de purgação da mora\n- [ ] Proposta de acordo parcelado"),

    ("Revisão contratual — Henrique Prado", "1000006-60.2025.8.26.0500", "Baixa",
     "Descreva aqui o planejamento.\n\nCHECKLIST:\n- [x] Análise das cláusulas abusivas\n- [x] Parecer técnico contábil\n- [ ] Réplica à contestação"),
]


# ── Eventos de agenda (tipo, nome, obs, dia, mes, ano) ────────────────────────

EVENTOS = [
    ("Compromisso", "Audiência — Ricardo Neves",     "Fórum Central, sala 304. Levar procuração.", 12, 6, 2026),
    ("Compromisso", "Reunião NovaTech",              "Alinhamento mensal de contratos.",           15, 6, 2026),
    ("Importante",  "Prazo — Réplica H. Prado",      "Último dia para protocolar.",                18, 6, 2026),
    ("Compromisso", "Conciliação — Larissa Ramos",   "2ª JEC, 14h.",                               22, 6, 2026),
    ("Importante",  "Vencimento OAB",                "",                                           25, 6, 2026),
]


def seed():
    print("Criando tabelas...")
    criar_tabelas()
    criar_tabela_agenda()

    print(f"Inserindo {len(CLIENTES)} clientes fictícios...")
    for c in CLIENTES:
        adicionar_cliente(*c)

    print(f"Inserindo {len(PROCESSOS)} processos fictícios...")
    for p in PROCESSOS:
        nome, cnj, razao, atuacao, vara, tipo_v, pct, prov, conv, fixo, parc, parc_p, status, obs = p
        adicionar_processo(nome, cnj, razao, atuacao, vara, tipo_v,
                           pct, prov, conv, fixo, parc, parc_p, status, obs)

        if "Pagos" in status and tipo_v != "Pro Bono":
            valor = conv if tipo_v == "Porcentagem" else fixo
            if valor > 0:
                adicionar_transacao(f"| {cnj}", valor, "Receita (+)", "")

    # Despesa manual para o financeiro não ficar só com receitas
    adicionar_transacao("Aluguel do escritório — Junho", 4500.00, "Despesa (-)", "01/06/2026")
    adicionar_transacao("Anuidade OAB", 980.00, "Despesa (-)", "05/06/2026")

    print("Criando associações entre processos...")
    sincronizar_associacoes("1000006-60.2025.8.26.0500", ["1000007-70.2025.8.26.0500"])
    sincronizar_associacoes("1000011-11.2024.8.26.0900", ["1000012-21.2025.8.26.0900"])

    print(f"Inserindo {len(ESTRATEGIAS)} estratégias fictícias...")
    conn = conectar()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS estrategias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            processo_id INTEGER,
            titulo TEXT NOT NULL,
            descricao TEXT,
            fase TEXT DEFAULT 'Ativa',
            prioridade TEXT DEFAULT 'Normal',
            data_criacao TEXT,
            FOREIGN KEY (processo_id) REFERENCES processos (id)
        )
    ''')
    mapa_cnj_id = {p[2]: p[0] for p in buscar_processos()}
    data_hoje = datetime.now().strftime("%d/%m/%Y")
    for titulo, cnj, prio, desc in ESTRATEGIAS:
        proc_id = mapa_cnj_id.get(cnj)
        cur.execute(
            "INSERT INTO estrategias (processo_id, titulo, descricao, fase, prioridade, data_criacao) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (proc_id, titulo, desc, "Ativa", prio, data_hoje)
        )
    conn.commit()
    conn.close()

    print(f"Inserindo {len(EVENTOS)} eventos de agenda...")
    for ev in EVENTOS:
        adicionar_evento_agenda(*ev)

    print("\n✅ Demo pronto! Abra o Archon e tire as capturas.")
    print("   Lembre-se de restaurar o banco real depois.")


if __name__ == "__main__":
    seed()
