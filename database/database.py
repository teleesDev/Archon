import sqlite3
from datetime import datetime
import os

# Garante que a base de dados é criada na mesma pasta que este ficheiro
DB_PATH = os.path.join(os.path.dirname(__file__), "advocacia.db")

def conectar():
    return sqlite3.connect(DB_PATH)

def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    # TABELA DE CLIENTES
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_pessoa TEXT NOT NULL,
            nome TEXT NOT NULL,
            documento TEXT,
            rg TEXT,
            telefone TEXT,
            email TEXT,
            profissao TEXT,
            estado_civil TEXT,
            naturalidade TEXT,
            endereco TEXT,
            estado TEXT,
            tipo_unidade TEXT,
            responsavel TEXT,
            observacoes TEXT,
            data_cadastro TEXT
        )
    ''')

    # TABELA DE FINANCEIRO
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS financeiro (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            tipo TEXT NOT NULL, 
            data_lancamento TEXT NOT NULL
        )
    ''')

    # TABELA DE PROCESSOS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS processos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_contratante TEXT NOT NULL,
            num_acao TEXT NOT NULL,
            razao_contrato TEXT NOT NULL,
            atuacao TEXT NOT NULL,
            vara TEXT,
            tipo_valor TEXT NOT NULL,
            pct REAL,
            proveito REAL,
            conversao REAL,
            valor_fixo REAL,
            parcelas INTEGER,
            parcelas_pagas INTEGER,
            status TEXT NOT NULL,
            data_cadastro TEXT
        )
    ''')

    # Injeção segura da nova coluna caso o banco já exista
    try:
        cursor.execute("ALTER TABLE processos ADD COLUMN observacoes TEXT")
    except sqlite3.OperationalError:
        pass # A coluna já existe

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS processos_associados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        acao_principal TEXT NOT NULL,
        acao_associada TEXT NOT NULL,
        UNIQUE(acao_principal, acao_associada)
    )
''')
    conn.commit()
    conn.close()

def criar_tabela_agenda():
    conn = conectar()
    conn.cursor().execute('''
        CREATE TABLE IF NOT EXISTS agenda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT,
            nome TEXT,
            obs TEXT,
            dia INTEGER,
            mes INTEGER,
            ano INTEGER
        )
    ''')
    conn.commit()
    conn.close()

# ==========================================
# FUNÇÕES DE CLIENTES
# ==========================================
def adicionar_cliente(tipo_pessoa, nome, doc, rg, telefone, email, prof, est_civil, nat, endereco, estado, tipo_unidade, resp, obs):
    conn = conectar()
    cursor = conn.cursor()
    data_atual = datetime.now().strftime("%d/%m/%Y")
    cursor.execute('''
        INSERT INTO clientes (tipo_pessoa, nome, documento, rg, telefone, email, profissao, estado_civil, naturalidade, endereco, estado, tipo_unidade, responsavel, observacoes, data_cadastro)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (tipo_pessoa, nome, doc, rg, telefone, email, prof, est_civil, nat, endereco, estado, tipo_unidade, resp, obs, data_atual))
    conn.commit()
    conn.close()

def buscar_clientes(termo=""):
    conn = conectar()
    cursor = conn.cursor()
    padrao = f"%{termo}%"
    cursor.execute('''
        SELECT id, tipo_pessoa, nome, documento, rg, telefone, email, profissao, estado_civil, naturalidade, endereco, estado, tipo_unidade, responsavel, observacoes 
        FROM clientes 
        WHERE nome LIKE ? OR documento LIKE ?
        ORDER BY nome COLLATE NOCASE ASC
    ''', (padrao, padrao))
    clientes = cursor.fetchall()
    conn.close()
    return clientes

def atualizar_cliente_completo(id_c, tipo_pessoa, nome, doc, rg, tel, email, prof, est_civil, nat, endereco, estado, tipo_unidade, resp, obs):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE clientes SET 
        tipo_pessoa=?, nome=?, documento=?, rg=?, telefone=?, email=?, profissao=?, estado_civil=?, naturalidade=?, endereco=?, estado=?, tipo_unidade=?, responsavel=?, observacoes=?
        WHERE id=?
    ''', (tipo_pessoa, nome, doc, rg, tel, email, prof, est_civil, nat, endereco, estado, tipo_unidade, resp, obs, id_c))
    conn.commit()
    conn.close()

def deletar_cliente(id_cliente):
    conn = conectar()
    cursor = conn.cursor()
    
    # Pega o nome do cliente antes de apagá-lo
    cursor.execute("SELECT nome FROM clientes WHERE id = ?", (id_cliente,))
    resultado = cursor.fetchone()
    
    if resultado:
        nome_cliente = resultado[0]
        # Desvincula o cliente dos processos, colocando a etiqueta de alerta
        cursor.execute("UPDATE processos SET nome_contratante = '[Sem Cliente]' WHERE nome_contratante = ?", (nome_cliente,))
        
    cursor.execute("DELETE FROM clientes WHERE id = ?", (id_cliente,))
    conn.commit()
    conn.close()

def obter_nome_cliente_por_id(id_cliente):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM clientes WHERE id = ?", (id_cliente,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else ""

def sincronizar_nome_processos(nome_antigo, nome_novo):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE processos SET nome_contratante = ? WHERE nome_contratante = ?", (nome_novo, nome_antigo))
    conn.commit()
    conn.close()

# ==========================================
# FUNÇÕES DO FINANCEIRO
# ==========================================
def adicionar_transacao(descricao, valor, tipo, data_lancamento):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO financeiro (descricao, valor, tipo, data_lancamento) VALUES (?, ?, ?, ?)', (descricao, valor, tipo, data_lancamento))
    conn.commit()
    conn.close()

def resumo_financeiro():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(valor) FROM financeiro WHERE tipo = 'Receita (+)'")
    receitas = float(cursor.fetchone()[0] or 0.0)
    cursor.execute("SELECT SUM(valor) FROM financeiro WHERE tipo = 'Despesa (-)'")
    despesas = float(cursor.fetchone()[0] or 0.0)
    conn.close()
    return receitas, despesas, receitas - despesas

def listar_transacoes():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT id, descricao, data_lancamento, valor, tipo FROM financeiro ORDER BY id DESC')
    t = cursor.fetchall()
    conn.close()
    return t

def deletar_transacao(id_transacao):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM financeiro WHERE id = ?", (id_transacao,))
    conn.commit()
    conn.close()

def filtrar_financeiro(mes, ano):
    conn = conectar()
    cursor = conn.cursor()
    if mes == "Todos" and ano == "Todos": padrao = "%"
    elif mes == "Todos" and ano != "Todos": padrao = f"%/{ano}"
    elif mes != "Todos" and ano == "Todos": padrao = f"%/{mes}/%"
    else: padrao = f"%/{mes}/{ano}"
    
    cursor.execute('SELECT id, descricao, data_lancamento, valor, tipo FROM financeiro WHERE data_lancamento LIKE ? ORDER BY id DESC', (padrao,))
    transacoes = cursor.fetchall()
    
    cursor.execute("SELECT SUM(valor) FROM financeiro WHERE tipo = 'Receita (+)' AND data_lancamento LIKE ?", (padrao,))
    receitas = float(cursor.fetchone()[0] or 0.0)
    
    cursor.execute("SELECT SUM(valor) FROM financeiro WHERE tipo = 'Despesa (-)' AND data_lancamento LIKE ?", (padrao,))
    despesas = float(cursor.fetchone()[0] or 0.0)
    
    conn.close()
    return transacoes, receitas - despesas

def buscar_transacao_por_desc(desc):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM financeiro WHERE descricao = ?', (desc,))
    res = cursor.fetchone()
    conn.close()
    return res

def atualizar_data_transacao(id_t, nova_data):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('UPDATE financeiro SET data_lancamento = ? WHERE id = ?', (nova_data, id_t))
    conn.commit()
    conn.close()

def reverter_pagamento_processo(num_acao):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT id, status FROM processos WHERE num_acao = ?', (num_acao,))
    res = cursor.fetchone()
    if res:
        id_p, status = res
        status_list = [s.strip() for s in status.split(",") if s.strip()]
        if "Pagos" in status_list:
            status_list.remove("Pagos")
            if "Não Pagos" not in status_list:
                status_list.append("Não Pagos")
        novo_status = ",".join(status_list)
        cursor.execute('UPDATE processos SET status = ? WHERE id = ?', (novo_status, id_p))
        conn.commit()
    conn.close()

# ==========================================
# FUNÇÕES DE PROCESSOS
# ==========================================
def adicionar_processo(nome, acao, razao, atuacao, vara, tipo_v, pct, proveito, conversao, v_fixo, parcelas, parcelas_pagas, status, obs):
    conn = conectar()
    cursor = conn.cursor()
    data_atual = datetime.now().strftime("%d/%m/%Y")
    cursor.execute('''
        INSERT INTO processos (nome_contratante, num_acao, razao_contrato, atuacao, vara, tipo_valor, pct, proveito, conversao, valor_fixo, parcelas, parcelas_pagas, status, data_cadastro, observacoes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (nome, acao, razao, atuacao, vara, tipo_v, pct, proveito, conversao, v_fixo, parcelas, parcelas_pagas, status, data_atual, obs))
    conn.commit()
    conn.close()

def buscar_processos(termo=""):
    conn = conectar()
    cursor = conn.cursor()
    padrao = f"%{termo}%"
    cursor.execute('''
        SELECT id, nome_contratante, num_acao, razao_contrato, atuacao, vara, tipo_valor, pct, proveito, conversao, valor_fixo, parcelas, parcelas_pagas, status, data_cadastro, observacoes
        FROM processos 
        WHERE nome_contratante LIKE ? OR num_acao LIKE ?
        ORDER BY id DESC
    ''', (padrao, padrao))
    processos = cursor.fetchall()
    conn.close()
    return processos

def deletar_processo(id_processo):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM processos WHERE id = ?", (id_processo,))
    conn.commit()
    conn.close()

def atualizar_status_processo(id_processo, novo_status):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE processos SET status = ? WHERE id = ?", (novo_status, id_processo))
    conn.commit()
    conn.close()

def atualizar_processo_completo(id_processo, nome, acao, razao, atuacao, vara, tipo_v, pct, prov, conv, v_fixo, parc, parc_pagas, status, obs):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE processos SET 
        nome_contratante=?, num_acao=?, razao_contrato=?, atuacao=?, vara=?, 
        tipo_valor=?, pct=?, proveito=?, conversao=?, valor_fixo=?, parcelas=?, parcelas_pagas=?, status=?, observacoes=?
        WHERE id=?
    ''', (nome, acao, razao, atuacao, vara, tipo_v, pct, prov, conv, v_fixo, parc, parc_pagas, status, obs, id_processo))
    conn.commit()
    conn.close()

# ==========================================
# SISTEMA DE AGENDA / CALENDÁRIO
# ==========================================
def adicionar_evento_agenda(tipo, nome, obs, dia, mes, ano):
    conn = conectar()
    conn.cursor().execute("INSERT INTO agenda (tipo, nome, obs, dia, mes, ano) VALUES (?, ?, ?, ?, ?, ?)", (tipo, nome, obs, dia, mes, ano))
    conn.commit()
    conn.close()

def buscar_eventos_do_mes(mes, ano):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, tipo, nome, obs, dia, mes, ano FROM agenda WHERE (mes = ? AND ano = ?) OR (mes = ? AND tipo = 'Importante')", (mes, ano, mes))
    res = cursor.fetchall()
    conn.close()
    return res

def deletar_evento_agenda(id_ev):
    conn = conectar()
    conn.cursor().execute("DELETE FROM agenda WHERE id = ?", (id_ev,))
    conn.commit()
    conn.close()

def atualizar_evento_agenda(id_ev, tipo, nome, obs, dia, mes, ano):
    conn = conectar()
    conn.cursor().execute("UPDATE agenda SET tipo=?, nome=?, obs=?, dia=?, mes=?, ano=? WHERE id=?", (tipo, nome, obs, dia, mes, ano, id_ev))
    conn.commit()
    conn.close()

def adicionar_associacao(acao1, acao2):
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO processos_associados (acao_principal, acao_associada) VALUES (?, ?)", (acao1, acao2))
        cursor.execute("INSERT OR IGNORE INTO processos_associados (acao_principal, acao_associada) VALUES (?, ?)", (acao2, acao1))
        conn.commit()

def remover_associacao(acao1, acao2):
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM processos_associados WHERE (acao_principal = ? AND acao_associada = ?) OR (acao_principal = ? AND acao_associada = ?)", (acao1, acao2, acao2, acao1))
        conn.commit()

def buscar_processos_associados(acao):
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT acao_associada FROM processos_associados WHERE acao_principal = ?", (acao,))
        return [row[0] for row in cursor.fetchall()]

def sincronizar_associacoes(acao_principal, lista_associadas):
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM processos_associados WHERE acao_principal = ? OR acao_associada = ?", (acao_principal, acao_principal))
        for acao2 in lista_associadas:
            cursor.execute("INSERT OR IGNORE INTO processos_associados (acao_principal, acao_associada) VALUES (?, ?)", (acao_principal, acao2))
            cursor.execute("INSERT OR IGNORE INTO processos_associados (acao_principal, acao_associada) VALUES (?, ?)", (acao2, acao_principal))
        conn.commit()

# ==========================================
# EXECUÇÃO DIRETA (CRIAÇÃO DO BANCO)
# ==========================================
if __name__ == "__main__":
    print("Criando o banco de dados e as tabelas...")
    criar_tabelas()
    criar_tabela_agenda()
    print("Banco de dados 'advocacia.db' criado/atualizado com sucesso!")