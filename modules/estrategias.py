import customtkinter as ctk
import sqlite3
from database.database import conectar, buscar_processos
from datetime import datetime

# ── Paleta ────────────────────────────────────────────────────────────────────
NAVY  = "#1C2E45"
GOLD  = "#C9A84C"
BG    = "#F4F5F7"
CARD  = "#FFFFFF"
BORDA = "#E0E3E8"
TEXT  = "#1A1A2E"
MUTED = "#7A8499"
VERDE = "#1A7A4A"
VERM  = "#B22222"

# ── DB ────────────────────────────────────────────────────────────────────────
def garantir_tabela_estrategias():
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute('''
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
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao criar tabela estrategias: {e}")


def listar_todas_estrategias(termo_busca=""):
    try:
        conn = conectar()
        cursor = conn.cursor()
        if termo_busca:
            like = f"%{termo_busca}%"
            cursor.execute('''
                SELECT e.id, e.titulo, e.descricao, e.prioridade,
                       p.num_acao, p.nome_contratante, e.processo_id, e.data_criacao
                FROM estrategias e
                LEFT JOIN processos p ON e.processo_id = p.id
                WHERE e.titulo LIKE ? OR p.num_acao LIKE ? OR p.nome_contratante LIKE ?
                ORDER BY e.id DESC
            ''', (like, like, like))
        else:
            cursor.execute('''
                SELECT e.id, e.titulo, e.descricao, e.prioridade,
                       p.num_acao, p.nome_contratante, e.processo_id, e.data_criacao
                FROM estrategias e
                LEFT JOIN processos p ON e.processo_id = p.id
                ORDER BY e.id DESC
            ''')
        res = cursor.fetchall()
        conn.close()
        return res
    except Exception as e:
        print(f"Erro ao listar estratégias: {e}")
        return []


def salvar_estrategia_db(id_est, proc_id, titulo, desc, prio):
    conn = conectar()
    cursor = conn.cursor()
    if id_est:
        cursor.execute(
            "UPDATE estrategias SET processo_id=?, titulo=?, descricao=?, prioridade=? WHERE id=?",
            (proc_id, titulo, desc, prio, id_est)
        )
    else:
        data = datetime.now().strftime("%d/%m/%Y")
        cursor.execute(
            "INSERT INTO estrategias (processo_id, titulo, descricao, fase, prioridade, data_criacao) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (proc_id, titulo, desc, "Ativa", prio, data)
        )
    conn.commit()
    conn.close()


def deletar_estrategia_db(id_est):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM estrategias WHERE id=?", (id_est,))
    conn.commit()
    conn.close()


# ── UI ────────────────────────────────────────────────────────────────────────
def criar_aba_estrategias(app, parent_frame):
    garantir_tabela_estrategias()

    parent_frame.configure(fg_color=BG)
    parent_frame.grid_columnconfigure(0, weight=0, minsize=300)
    parent_frame.grid_columnconfigure(1, weight=1)
    parent_frame.grid_rowconfigure(0, weight=1)

    # ── SIDEBAR ───────────────────────────────────────────────────────────────
    sidebar = ctk.CTkFrame(parent_frame, fg_color=CARD, corner_radius=14,
                            border_width=1, border_color=BORDA)
    sidebar.grid(row=0, column=0, sticky="nsew", padx=(20, 8), pady=20)
    sidebar.grid_rowconfigure(2, weight=1)
    sidebar.grid_columnconfigure(0, weight=1)

    # Cabeçalho sidebar
    hdr_side = ctk.CTkFrame(sidebar, fg_color=NAVY, height=52, corner_radius=0)
    hdr_side.grid(row=0, column=0, sticky="ew")
    hdr_side.grid_propagate(False)
    hdr_side.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(hdr_side, text="ESTRATÉGIAS",
                 font=ctk.CTkFont(family="Microsoft YaHei UI", size=13, weight="bold"),
                 text_color=GOLD).grid(row=0, column=0, padx=20, pady=14, sticky="w")

    # Busca
    frame_busca = ctk.CTkFrame(sidebar, fg_color="transparent")
    frame_busca.grid(row=1, column=0, sticky="ew", padx=14, pady=(14, 4))

    app.entry_busca_est = ctk.CTkEntry(frame_busca, placeholder_text="Buscar estratégia...",
                                        fg_color=BG, border_color=BORDA)
    app.entry_busca_est.pack(fill="x")

    def on_busca(event=None):
        carregar_lista_estrategias(app, app.entry_busca_est.get())

    app.entry_busca_est.bind("<KeyRelease>", on_busca)

    # Lista scroll
    app.scroll_estrategias = ctk.CTkScrollableFrame(sidebar, fg_color="transparent")
    app.scroll_estrategias.grid(row=2, column=0, sticky="nsew", padx=8, pady=4)

    # Botão nova estratégia
    rodape = ctk.CTkFrame(sidebar, fg_color="transparent")
    rodape.grid(row=3, column=0, sticky="ew", padx=14, pady=16)
    ctk.CTkButton(rodape, text="+ Nova Estratégia",
                  fg_color=NAVY, hover_color="#253A56", text_color=GOLD,
                  font=ctk.CTkFont(weight="bold", size=13),
                  height=42, corner_radius=10,
                  command=lambda: nova_estrategia(app)).pack(fill="x")

    # ── ÁREA DE TRABALHO ──────────────────────────────────────────────────────
    app.frame_direita_est = ctk.CTkFrame(parent_frame, fg_color="transparent")
    app.frame_direita_est.grid(row=0, column=1, sticky="nsew", padx=(8, 20), pady=20)
    app.frame_direita_est.grid_columnconfigure(0, weight=1)
    app.frame_direita_est.grid_rowconfigure(0, weight=1)

    # Fundo do form — branco com borda, substituindo o "pergaminho" deslocado
    app.form_estrategia = ctk.CTkFrame(app.frame_direita_est, fg_color=CARD,
                                        corner_radius=14,
                                        border_width=1, border_color=BORDA)
    app.form_estrategia.grid(row=0, column=0, sticky="nsew")
    app.form_estrategia.grid_columnconfigure(0, weight=1)
    app.form_estrategia.grid_rowconfigure(2, weight=1)

    # Remover foco ao clicar fora dos inputs
    def remover_foco(event):
        try:
            if event.widget != app.entry_busca_est._entry:
                parent_frame.focus_set()
        except:
            pass

    for bloco in (parent_frame, sidebar, app.frame_direita_est, app.form_estrategia):
        try:
            bloco.bind("<Button-1>", remover_foco, add="+")
        except:
            pass

    app.id_estrategia_atual = None
    try:
        app.lista_processos_tuplas = buscar_processos()
    except:
        app.lista_processos_tuplas = []
    app.lista_processos_nomes = [f"{p[2]}" for p in app.lista_processos_tuplas]

    carregar_lista_estrategias(app)
    nova_estrategia(app)


def carregar_lista_estrategias(app, termo_busca=""):
    if not hasattr(app, 'scroll_estrategias') or not app.scroll_estrategias.winfo_exists():
        return
    app._cards_est_sidebar = {}
    for w in app.scroll_estrategias.winfo_children():
        w.destroy()

    estrategias = listar_todas_estrategias(termo_busca)

    if not estrategias:
        ctk.CTkLabel(app.scroll_estrategias, text="Nenhuma estratégia encontrada.",
                     text_color=MUTED, font=ctk.CTkFont(size=12, slant="italic")
                     ).pack(pady=24)
        return

    for est in estrategias:
        id_est, titulo, desc, prio, acao, cliente, proc_id, data = est

        cor_prio = VERM if prio == "Alta" else GOLD if prio == "Moderada" else VERDE

        if not hasattr(app, '_cards_est_sidebar'):
            app._cards_est_sidebar = {}

        card = ctk.CTkFrame(app.scroll_estrategias, fg_color=CARD, corner_radius=10,
                             border_width=1, border_color=BORDA, cursor="hand2", height=96)
        card.pack(fill="x", pady=4, padx=2)
        card.pack_propagate(False)
        app._cards_est_sidebar[id_est] = card

        # Faixa lateral de urgência
        ctk.CTkFrame(card, width=4, fg_color=cor_prio, corner_radius=0).pack(
            side="left", fill="y")

        conteudo = ctk.CTkFrame(card, fg_color="transparent")
        conteudo.pack(side="left", fill="both", expand=True, padx=12, pady=8)

        def onClick(event, i=id_est):
            abrir_estrategia(app, i)

        for w in (card, conteudo):
            w.bind("<Button-1>", onClick)

        # Topo: badge urgência + data
        topo = ctk.CTkFrame(conteudo, fg_color="transparent")
        topo.pack(fill="x")
        topo.bind("<Button-1>", onClick)

        badge = ctk.CTkLabel(topo, text=f" {prio.upper()} ",
                              font=ctk.CTkFont(size=9, weight="bold"),
                              fg_color=cor_prio, text_color="white", corner_radius=4)
        badge.pack(side="left")
        badge.bind("<Button-1>", onClick)

        lbl_data = ctk.CTkLabel(topo, text=data or "",
                                 font=ctk.CTkFont(size=10), text_color=MUTED)
        lbl_data.pack(side="right")
        lbl_data.bind("<Button-1>", onClick)

        # Título
        lbl_tit = ctk.CTkLabel(conteudo, text=titulo,
                                font=ctk.CTkFont(size=13, weight="bold"),
                                text_color=TEXT, anchor="w")
        lbl_tit.pack(fill="x", pady=(4, 1))
        lbl_tit.bind("<Button-1>", onClick)

        # Processo vinculado
        txt_proc = f"Proc: {acao}" if acao else "Sem processo vinculado"
        lbl_proc = ctk.CTkLabel(conteudo, text=txt_proc,
                                 font=ctk.CTkFont(size=11), text_color=MUTED, anchor="w")
        lbl_proc.pack(fill="x")
        lbl_proc.bind("<Button-1>", onClick)


def desenhar_formulario(app, dados=None):
    for w in app.form_estrategia.winfo_children():
        w.destroy()

    try:
        app.lista_processos_tuplas = buscar_processos()
    except:
        app.lista_processos_tuplas = []
    app.lista_processos_nomes = [f"{p[2]}" for p in app.lista_processos_tuplas]

    # Cabeçalho do form
    hdr = ctk.CTkFrame(app.form_estrategia, fg_color=NAVY, height=52,
                        corner_radius=0)
    hdr.grid(row=0, column=0, sticky="ew")
    hdr.grid_propagate(False)
    hdr.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(hdr, text="PLANO ESTRATÉGICO",
                 font=ctk.CTkFont(family="Microsoft YaHei UI", size=11, weight="bold"),
                 text_color=GOLD).grid(row=0, column=0, padx=28, sticky="w", pady=16)

    # Área de título editável
    area_titulo = ctk.CTkFrame(app.form_estrategia, fg_color="transparent")
    area_titulo.grid(row=1, column=0, sticky="ew", padx=28, pady=(24, 0))
    area_titulo.grid_columnconfigure(0, weight=1)

    app.ent_titulo_est = ctk.CTkEntry(
        area_titulo,
        font=ctk.CTkFont(size=22, weight="bold"),
        text_color=TEXT, fg_color="transparent",
        border_width=0,
        placeholder_text="Título da Estratégia..."
    )
    app.ent_titulo_est.grid(row=0, column=0, sticky="ew")
    ctk.CTkFrame(area_titulo, height=2, fg_color=GOLD).grid(
        row=1, column=0, sticky="ew", pady=(6, 0))

    # Configs: processo + urgência
    configs = ctk.CTkFrame(app.form_estrategia, fg_color="transparent")
    configs.grid(row=2, column=0, sticky="ew", padx=28, pady=(20, 0))
    configs.grid_columnconfigure(1, weight=1)

    def _lbl_cfg(row, texto):
        ctk.CTkLabel(configs, text=texto,
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=TEXT).grid(row=row, column=0, sticky="w",
                                           padx=(0, 16), pady=8)

    _lbl_cfg(0, "Vincular ao Processo:")

    # ── Processo: Label + Botão seta branca (igual financeiro) ────────────────
    frame_proc_wrap = ctk.CTkFrame(configs, fg_color="transparent")
    frame_proc_wrap.grid(row=0, column=1, sticky="w", pady=8)
    frame_proc_wrap.grid_columnconfigure(0, weight=1)

    app.lbl_proc_est = ctk.CTkLabel(
        frame_proc_wrap, text="Nenhum processo",
        font=ctk.CTkFont(size=13), text_color=TEXT,
        fg_color=BG, corner_radius=6, anchor="w", width=330
    )
    app.lbl_proc_est.grid(row=0, column=0, sticky="ew", ipady=6, ipadx=8)

    def _abrir_dropdown_proc():
        # Processos que já têm estratégia vinculada (exceto o da estratégia atual)
        try:
            conn = conectar()
            cur  = conn.cursor()
            cur.execute(
                "SELECT p.num_acao FROM estrategias e "
                "JOIN processos p ON e.processo_id = p.id "
                "WHERE e.id != ? OR e.id IS NULL",
                (app.id_estrategia_atual or -1,)
            )
            ja_vinculados = {r[0] for r in cur.fetchall()}
            conn.close()
        except:
            ja_vinculados = set()
        disponiveis = [n for n in app.lista_processos_nomes if n not in ja_vinculados]
        valores = ["Nenhum processo"] + disponiveis
        _menu = ctk.CTkToplevel(configs)
        _menu.overrideredirect(True)
        _menu.attributes("-topmost", True)
        x = frame_proc_wrap.winfo_rootx()
        y = frame_proc_wrap.winfo_rooty() + frame_proc_wrap.winfo_height()
        _menu.geometry(f"360x{min(len(valores)*36, 200)+4}+{x}+{y}")
        _menu.configure(fg_color=CARD)
        ctk.CTkFrame(_menu, fg_color=BORDA, height=1).pack(fill="x")
        scroll = ctk.CTkScrollableFrame(_menu, fg_color=CARD, corner_radius=0)
        scroll.pack(fill="both", expand=True)
        def _escolher(v):
            app.lbl_proc_est.configure(text=v)
            _menu.destroy()
        for opt in valores:
            ctk.CTkButton(scroll, text=opt, fg_color="transparent",
                          text_color=TEXT, hover_color=BG, anchor="w",
                          height=34, font=ctk.CTkFont(size=12),
                          command=lambda v=opt: _escolher(v)).pack(fill="x", padx=2)
        _menu.bind("<FocusOut>", lambda e: _menu.destroy())
        _menu.after(100, _menu.focus_force)

    ctk.CTkButton(
        frame_proc_wrap, text="▼", width=36, height=36,
        fg_color=NAVY, hover_color="#253A56",
        text_color="#FFFFFF", font=ctk.CTkFont(size=11),
        corner_radius=6, command=_abrir_dropdown_proc
    ).grid(row=0, column=1, padx=(6, 0))

    # Helper get/set para compatibilidade com o restante do código
    class _ComboProc:
        def get(self): return app.lbl_proc_est.cget("text")
        def set(self, v): app.lbl_proc_est.configure(text=v)
    app.combo_proc_est = _ComboProc()

    _lbl_cfg(1, "Nível de Urgência:")

    # ── Urgência: Label + Botão seta branca ───────────────────────────────────
    frame_prio_wrap = ctk.CTkFrame(configs, fg_color="transparent")
    frame_prio_wrap.grid(row=1, column=1, sticky="w", pady=8)

    app.lbl_prio_est = ctk.CTkLabel(
        frame_prio_wrap, text="Moderada",
        font=ctk.CTkFont(size=13), text_color=TEXT,
        fg_color=BG, corner_radius=6, anchor="w", width=160
    )
    app.lbl_prio_est.grid(row=0, column=0, sticky="ew", ipady=6, ipadx=8)

    def _abrir_dropdown_prio():
        _menu2 = ctk.CTkToplevel(configs)
        _menu2.overrideredirect(True)
        _menu2.attributes("-topmost", True)
        x = frame_prio_wrap.winfo_rootx()
        y = frame_prio_wrap.winfo_rooty() + frame_prio_wrap.winfo_height()
        _menu2.geometry(f"180x112+{x}+{y}")
        _menu2.configure(fg_color=CARD)
        ctk.CTkFrame(_menu2, fg_color=BORDA, height=1).pack(fill="x")
        def _esc(v):
            app.lbl_prio_est.configure(text=v)
            _menu2.destroy()
        for opt in ["Baixa", "Moderada", "Alta"]:
            ctk.CTkButton(_menu2, text=opt, fg_color="transparent",
                          text_color=TEXT, hover_color=BG, anchor="w",
                          height=34, font=ctk.CTkFont(size=12),
                          command=lambda v=opt: _esc(v)).pack(fill="x", padx=2)
        _menu2.bind("<FocusOut>", lambda e: _menu2.destroy())
        _menu2.after(100, _menu2.focus_force)

    ctk.CTkButton(
        frame_prio_wrap, text="▼", width=36, height=36,
        fg_color=NAVY, hover_color="#253A56",
        text_color="#FFFFFF", font=ctk.CTkFont(size=11),
        corner_radius=6, command=_abrir_dropdown_prio
    ).grid(row=0, column=1, padx=(6, 0))

    class _ComboPrio:
        def get(self): return app.lbl_prio_est.cget("text")
        def set(self, v): app.lbl_prio_est.configure(text=v)
    app.combo_prio_est = _ComboPrio()

    # Área de texto
    area_txt = ctk.CTkFrame(app.form_estrategia, fg_color="transparent")
    area_txt.grid(row=3, column=0, sticky="nsew", padx=28, pady=(20, 0))
    area_txt.grid_columnconfigure(0, weight=1)
    area_txt.grid_rowconfigure(1, weight=1)
    app.form_estrategia.grid_rowconfigure(3, weight=1)

    ctk.CTkLabel(area_txt, text="Descrição e Plano de Ação",
                 font=ctk.CTkFont(size=13, weight="bold"),
                 text_color=TEXT).grid(row=0, column=0, sticky="w", pady=(0, 8))

    app.txt_desc_est = ctk.CTkTextbox(
        area_txt,
        font=ctk.CTkFont(size=13),
        fg_color=BG, text_color=TEXT,
        border_color=BORDA, border_width=1, corner_radius=10
    )
    app.txt_desc_est.grid(row=1, column=0, sticky="nsew")

    # Rodapé
    rodape = ctk.CTkFrame(app.form_estrategia, fg_color="transparent")
    rodape.grid(row=4, column=0, sticky="ew", padx=28, pady=(16, 24))

    if dados:
        ctk.CTkButton(rodape, text="Excluir Estratégia",
                      fg_color="transparent", text_color=VERM,
                      hover_color="#FFEEEE",
                      font=ctk.CTkFont(weight="bold"),
                      border_width=1, border_color=VERM,
                      corner_radius=8,
                      command=lambda: confirmar_exclusao(app)).pack(side="left")

    texto_btn = "Atualizar Estratégia" if dados else "Salvar Estratégia"
    ctk.CTkButton(rodape, text=texto_btn,
                  fg_color=NAVY, hover_color="#253A56", text_color=GOLD,
                  font=ctk.CTkFont(size=13, weight="bold"),
                  height=40, corner_radius=10,
                  command=lambda: salvar_estrategia(app)).pack(side="right")

    # Preencher dados se editando
    texto_padrao = "Descreva aqui o planejamento.\n\nCHECKLIST:\n- [ ] \n- [ ] \n- [ ] "
    if dados:
        id_est, titulo, desc, prio, acao, cliente, proc_id, data = dados
        app.id_estrategia_atual = id_est
        app.ent_titulo_est.insert(0, titulo)
        app.txt_desc_est.insert("0.0", desc)
        app.combo_prio_est.set(prio)
        app.combo_proc_est.set(acao if acao in app.lista_processos_nomes else "Nenhum processo")
    else:
        app.id_estrategia_atual = None
        app.txt_desc_est.insert("0.0", texto_padrao)
        app.combo_prio_est.set("Moderada")
        app.combo_proc_est.set("Nenhum processo")


def nova_estrategia(app):
    desenhar_formulario(app, dados=None)


def abrir_estrategia(app, id_est):
    carregar_lista_estrategias(app)
    estrategias = listar_todas_estrategias()
    dados = next((m for m in estrategias if m[0] == id_est), None)
    if dados:
        desenhar_formulario(app, dados)
        # Destacar card selecionado na sidebar
        if hasattr(app, '_cards_est_sidebar'):
            for cid, card in app._cards_est_sidebar.items():
                try:
                    if cid == id_est:
                        card.configure(fg_color="#EAF0FA", border_color=NAVY, border_width=1)
                    else:
                        card.configure(fg_color=CARD, border_color=BORDA, border_width=1)
                except:
                    pass


def salvar_estrategia(app):
    titulo = app.ent_titulo_est.get().strip()
    proc_sel = app.combo_proc_est.get()
    prio     = app.combo_prio_est.get()
    desc     = app.txt_desc_est.get("0.0", "end").strip()

    if not titulo:
        app.ent_titulo_est.configure(border_color=VERM, border_width=1)
        return

    proc_id = None
    if proc_sel and proc_sel != "Nenhum processo":
        proc_id = next((p[0] for p in app.lista_processos_tuplas if p[2] == proc_sel), None)

    # Bloquear: se é NOVA estratégia e o processo já tem uma vinculada
    if not app.id_estrategia_atual and proc_id:
        try:
            conn = conectar()
            cur  = conn.cursor()
            cur.execute("SELECT id FROM estrategias WHERE processo_id=? LIMIT 1", (proc_id,))
            existente = cur.fetchone()
            conn.close()
            if existente:
                app.ent_titulo_est.configure(
                    placeholder_text="Este processo já possui uma estratégia vinculada!",
                    border_color=VERM, border_width=1
                )
                return
        except:
            pass

    salvar_estrategia_db(app.id_estrategia_atual, proc_id, titulo, desc, prio)
    carregar_lista_estrategias(app)

    estrategias = listar_todas_estrategias()
    novo_id = app.id_estrategia_atual if app.id_estrategia_atual else estrategias[0][0]
    abrir_estrategia(app, novo_id)


def confirmar_exclusao(app):
    modal = ctk.CTkToplevel(app)
    modal.title("Excluir Estratégia")
    modal.geometry("360x180")
    modal.attributes("-topmost", True)
    modal.grab_set()
    modal.configure(fg_color=BG)

    ctk.CTkFrame(modal, fg_color=NAVY, height=50, corner_radius=0).pack(fill="x")
    ctk.CTkLabel(modal, text="Excluir esta estratégia?",
                 font=ctk.CTkFont(size=14, weight="bold"),
                 text_color=TEXT).pack(pady=(20, 6))
    ctk.CTkLabel(modal, text="Esta ação não pode ser desfeita.",
                 font=ctk.CTkFont(size=11), text_color=MUTED).pack()

    frame_btn = ctk.CTkFrame(modal, fg_color="transparent")
    frame_btn.pack(pady=20)

    def sim():
        if app.id_estrategia_atual:
            deletar_estrategia_db(app.id_estrategia_atual)
            carregar_lista_estrategias(app)
            nova_estrategia(app)
        modal.destroy()

    ctk.CTkButton(frame_btn, text="Excluir", fg_color=VERM, hover_color="#8B1A1A",
                  text_color="white", width=110, corner_radius=8, command=sim).pack(side="left", padx=8)
    ctk.CTkButton(frame_btn, text="Cancelar", fg_color=BG, hover_color=BORDA,
                  text_color=TEXT, border_width=1, border_color=BORDA,
                  width=110, corner_radius=8, command=modal.destroy).pack(side="left", padx=8)
