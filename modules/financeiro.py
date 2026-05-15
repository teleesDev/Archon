import customtkinter as ctk
from datetime import datetime
from PIL import Image
from database.database import (
    adicionar_transacao, deletar_transacao, filtrar_financeiro,
    reverter_pagamento_processo, atualizar_data_transacao, buscar_processos, buscar_clientes
)
from modules import layout, processos
from modules.utils import formatar_data

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


def criar_aba_financeiro(app, parent_frame):
    parent_frame.configure(fg_color=BG)
    parent_frame.grid_rowconfigure(0, weight=1)
    parent_frame.grid_columnconfigure(0, weight=0, minsize=320)
    parent_frame.grid_columnconfigure(1, weight=1)

    # ── COLUNA ESQUERDA ───────────────────────────────────────────────────────
    col_esq = ctk.CTkFrame(parent_frame, fg_color="transparent")
    col_esq.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)
    col_esq.grid_columnconfigure(0, weight=1)
    col_esq.grid_rowconfigure(1, weight=0)

    # Card Saldo
    card_saldo = ctk.CTkFrame(col_esq, fg_color=NAVY, corner_radius=14)
    card_saldo.grid(row=0, column=0, sticky="ew", pady=(0, 16))

    ctk.CTkLabel(card_saldo, text="Saldo do Período",
                 font=ctk.CTkFont(size=12, weight="bold"),
                 text_color="#8AAABB").pack(anchor="w", padx=24, pady=(20, 0))

    app.lbl_saldo = ctk.CTkLabel(card_saldo, text="R$ 0,00",
                                  font=ctk.CTkFont(size=34, weight="bold"),
                                  text_color="#FFFFFF")
    app.lbl_saldo.pack(anchor="w", padx=24, pady=(4, 20))

    # Card Novo Lançamento
    form_fin = ctk.CTkFrame(col_esq, fg_color=CARD, corner_radius=14,
                             border_width=1, border_color=BORDA)
    form_fin.grid(row=1, column=0, sticky="ew")
    form_fin.grid_columnconfigure(0, weight=1)

    # Cabeçalho do form
    hdr = ctk.CTkFrame(form_fin, fg_color="transparent")
    hdr.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 0))
    ctk.CTkLabel(hdr, text="Novo Lançamento",
                 font=ctk.CTkFont(size=15, weight="bold"),
                 text_color=TEXT).pack(side="left")
    ctk.CTkFrame(form_fin, height=1, fg_color=BORDA).grid(
        row=1, column=0, sticky="ew", padx=20, pady=(10, 0))

    app.fin_desc = ctk.CTkEntry(form_fin, placeholder_text="Descrição (Ex: Honorários)",
                                 fg_color=BG, border_color=BORDA)
    app.fin_desc.grid(row=2, column=0, padx=20, pady=(14, 6), sticky="ew")

    app.fin_valor = ctk.CTkEntry(form_fin, placeholder_text="Valor numérico (Ex: 1500.50)",
                                  fg_color=BG, border_color=BORDA)
    app.fin_valor.grid(row=3, column=0, padx=20, pady=6, sticky="ew")

    # Frame que contém label colorido + OptionMenu com seta sempre branca
    frame_tipo_wrap = ctk.CTkFrame(form_fin, fg_color="transparent")
    frame_tipo_wrap.grid(row=4, column=0, padx=20, pady=6, sticky="ew")
    frame_tipo_wrap.grid_columnconfigure(0, weight=1)

    # Label colorido separado — muda cor independente da seta
    app.lbl_tipo_fin = ctk.CTkLabel(
        frame_tipo_wrap, text="Receita (+)",
        font=ctk.CTkFont(weight="bold", size=13),
        text_color=VERDE, fg_color=BG,
        corner_radius=6, anchor="w"
    )
    app.lbl_tipo_fin.grid(row=0, column=0, sticky="ew", ipady=6, ipadx=8)

    def _abrir_dropdown_tipo():
        # Simula um dropdown com toplevel simples
        _menu = ctk.CTkToplevel(form_fin)
        _menu.overrideredirect(True)
        _menu.attributes("-topmost", True)
        x = frame_tipo_wrap.winfo_rootx()
        y = frame_tipo_wrap.winfo_rooty() + frame_tipo_wrap.winfo_height()
        _menu.geometry(f"180x80+{x}+{y}")
        _menu.configure(fg_color=CARD)
        ctk.CTkFrame(_menu, fg_color=BORDA, height=1).pack(fill="x")

        def _escolher(valor):
            app.lbl_tipo_fin.configure(
                text=valor,
                text_color=VERDE if "Receita" in valor else VERM
            )
            _menu.destroy()

        for opt in ["Receita (+)", "Despesa (-)"]:
            ctk.CTkButton(
                _menu, text=opt, fg_color="transparent",
                text_color=VERDE if "Receita" in opt else VERM,
                hover_color=BG, anchor="w", height=38,
                font=ctk.CTkFont(weight="bold"),
                command=lambda v=opt: _escolher(v)
            ).pack(fill="x", padx=4, pady=2)

        _menu.bind("<FocusOut>", lambda e: _menu.destroy())
        _menu.after(100, _menu.focus_force)

    # Botão da seta — sempre branco sobre navy
    btn_seta_tipo = ctk.CTkButton(
        frame_tipo_wrap, text="▼", width=36, height=36,
        fg_color=NAVY, hover_color="#253A56",
        text_color="#FFFFFF",  # seta SEMPRE branca
        font=ctk.CTkFont(size=11),
        corner_radius=6,
        command=_abrir_dropdown_tipo
    )
    btn_seta_tipo.grid(row=0, column=1, padx=(6, 0))

    # Helper para obter o tipo selecionado atual
    def _get_tipo_fin():
        return app.lbl_tipo_fin.cget("text")
    app._get_tipo_fin = _get_tipo_fin

    frame_data = ctk.CTkFrame(form_fin, fg_color="transparent")
    frame_data.grid(row=5, column=0, padx=20, pady=6, sticky="ew")
    frame_data.grid_columnconfigure(0, weight=1)

    app.fin_data = ctk.CTkEntry(frame_data, placeholder_text="DD/MM/AAAA",
                                 fg_color=BG, border_color=BORDA)
    app.fin_data.grid(row=0, column=0, padx=(0, 10), sticky="ew")
    app.fin_data.configure(state="disabled")
    app.fin_data.bind("<KeyRelease>", lambda e: formatar_data(app.fin_data, e))

    app.var_data_atual = ctk.BooleanVar(value=True)
    app.chk_data = ctk.CTkCheckBox(frame_data, text="Hoje", text_color=TEXT,
                                    variable=app.var_data_atual,
                                    fg_color=NAVY, hover_color="#253A56",
                                    command=lambda: alternar_campo_data(app))
    app.chk_data.grid(row=0, column=1, sticky="e")

    ctk.CTkButton(form_fin, text="Adicionar Lançamento",
                  font=ctk.CTkFont(weight="bold", size=13),
                  fg_color=GOLD, hover_color="#A8893C", text_color="#1A1A2E",
                  height=40, corner_radius=8,
                  command=lambda: salvar_lancamento(app)
                  ).grid(row=6, column=0, padx=20, pady=(14, 6), sticky="ew")

    app.lbl_mensagem = ctk.CTkLabel(form_fin, text="",
                                     font=ctk.CTkFont(size=12, weight="bold"))
    app.lbl_mensagem.grid(row=7, column=0, padx=20, pady=(0, 16), sticky="ew")

    # ── COLUNA DIREITA: Histórico ──────────────────────────────────────────────
    col_dir = ctk.CTkFrame(parent_frame, fg_color="transparent")
    col_dir.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)
    col_dir.grid_rowconfigure(1, weight=1)
    col_dir.grid_columnconfigure(0, weight=1)

    # Barra de filtros
    filt = ctk.CTkFrame(col_dir, fg_color=CARD, corner_radius=12,
                         border_width=1, border_color=BORDA)
    filt.grid(row=0, column=0, sticky="ew", pady=(0, 12))
    filt.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(filt, text="Histórico",
                 font=ctk.CTkFont(size=16, weight="bold"),
                 text_color=TEXT).grid(row=0, column=0, padx=20, pady=14, sticky="w")

    frame_filtros = ctk.CTkFrame(filt, fg_color="transparent")
    frame_filtros.grid(row=0, column=1, padx=20, pady=10, sticky="e")

    app.combo_mes = ctk.CTkOptionMenu(
        frame_filtros, width=100,
        values=["Mes", "01", "02", "03", "04", "05", "06",
                "07", "08", "09", "10", "11", "12"],
        fg_color=NAVY, button_color="#253A56", button_hover_color="#1C2E45",
        text_color="#FFFFFF", dropdown_fg_color=CARD, dropdown_text_color=TEXT
    )
    app.combo_mes.set("Mes")
    app.combo_mes.pack(side="left", padx=(0, 6))

    app.combo_ano = ctk.CTkOptionMenu(
        frame_filtros, width=100,
        values=["Ano", "2024", "2025", "2026", "2027", "2028"],
        fg_color=NAVY, button_color="#253A56", button_hover_color="#1C2E45",
        text_color="#FFFFFF", dropdown_fg_color=CARD, dropdown_text_color=TEXT
    )
    app.combo_ano.set("Ano")
    app.combo_ano.pack(side="left", padx=(0, 6))

    ctk.CTkButton(frame_filtros, text="Filtrar", width=70,
                  fg_color=GOLD, hover_color="#A8893C", text_color="#1A1A2E",
                  font=ctk.CTkFont(weight="bold"), corner_radius=8,
                  command=lambda: atualizar_tela_financeira(app)
                  ).pack(side="left")

    # Scroll de transações
    app.scroll_fin = ctk.CTkScrollableFrame(col_dir, fg_color="transparent",
                                             corner_radius=0)
    app.scroll_fin.grid(row=1, column=0, sticky="nsew")


def alternar_campo_data(app):
    if app.var_data_atual.get():
        app.fin_data.delete(0, 'end')
        app.fin_data.configure(state="disabled")
    else:
        app.fin_data.configure(state="normal")


def salvar_lancamento(app):
    app.lbl_mensagem.configure(text="")
    desc = app.fin_desc.get()
    valor_str = app.fin_valor.get().replace(",", ".")
    tipo = app._get_tipo_fin()

    if app.var_data_atual.get():
        data_lancamento = datetime.now().strftime("%d/%m/%Y")
    else:
        data_lancamento = app.fin_data.get().strip()
        if len(data_lancamento) != 10:
            app.lbl_mensagem.configure(text="Erro: Digite a data completa.", text_color=VERM)
            return

    if not desc or not valor_str:
        app.lbl_mensagem.configure(text="Erro: Preencha descrição e valor.", text_color=VERM)
        return

    try:
        valor = float(valor_str)
        adicionar_transacao(desc, valor, tipo, data_lancamento)
        app.fin_desc.delete(0, 'end')
        app.fin_valor.delete(0, 'end')
        if not app.var_data_atual.get():
            app.fin_data.delete(0, 'end')
        app.combo_mes.set("Todos")
        app.combo_ano.set("Todos")
        atualizar_tela_financeira(app)
        app.lbl_mensagem.configure(text="Lançamento salvo!", text_color=VERDE)
    except ValueError:
        app.lbl_mensagem.configure(text="Erro: Valor inválido.", text_color=VERM)


def atualizar_tela_financeira(app):
    for w in list(app.scroll_fin.winfo_children()):
        w.destroy()

    def _ic(nome, tam=(14, 14)):
        try: return ctk.CTkImage(Image.open(f"assets/{nome}"), size=tam)
        except: return None

    img_edit   = _ic("icon_edit.png")
    img_del    = _ic("icon_delete.png")
    img_proc   = _ic("icon_balanca.png",  (16, 16))
    img_manual = _ic("icon_manual.png",   (16, 16))

    mes_raw = app.combo_mes.get() if hasattr(app, 'combo_mes') else "Todos"
    ano_raw = app.combo_ano.get() if hasattr(app, 'combo_ano') else "Todos"
    mes = "Todos" if mes_raw in ("Mes", "Todos") else mes_raw
    ano = "Todos" if ano_raw in ("Ano", "Todos") else ano_raw

    try:
        transacoes, saldo = filtrar_financeiro(mes, ano)
    except:
        transacoes, saldo = [], 0.0

    moeda = lambda v: f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    app.lbl_saldo.configure(text=moeda(saldo))

    try:
        mapa_clientes  = {c[2]: c[1] for c in buscar_clientes()}
        mapa_processos = {p[2]: p[1] for p in buscar_processos()}
    except:
        mapa_clientes = mapa_processos = {}

    if not transacoes:
        ctk.CTkLabel(app.scroll_fin, text="Nenhum lançamento encontrado.",
                     text_color=MUTED, font=ctk.CTkFont(size=13, slant="italic")
                     ).pack(pady=40)
        return

    for t in transacoes:
        id_t, desc, data_lanc, valor, tipo = t

        is_proc = desc.startswith("|")
        if is_proc:
            cnj = desc.replace("|", "").strip()
            nome_cli = mapa_processos.get(cnj)
            tipo_cli = mapa_clientes.get(nome_cli) if nome_cli else None
            if tipo_cli == "Pessoa Jurídica":
                cor_accent = GOLD
            else:
                cor_accent = "#253A56"   # azul PF
            desc_limpa = cnj
        else:
            cor_accent = TEXT            # preto para manual
            desc_limpa = desc.strip()

        cor_valor = VERDE if "Receita" in tipo else VERM

        # Card
        card = ctk.CTkFrame(app.scroll_fin, fg_color=CARD, corner_radius=10,
                             border_width=1, border_color=BORDA, height=70)
        card.pack(fill="x", pady=5, padx=2)
        card.pack_propagate(False)

        # Faixa lateral colorida
        ctk.CTkFrame(card, width=4, fg_color=cor_accent, corner_radius=0).pack(
            side="left", fill="y")

        # Ícone tipo
        icone = img_proc if is_proc else img_manual
        if icone:
            ctk.CTkLabel(card, text="", image=icone, fg_color="transparent").pack(
                side="left", padx=(10, 0), pady=10)

        # Conteúdo
        conteudo = ctk.CTkFrame(card, fg_color="transparent")
        conteudo.pack(side="left", fill="both", expand=True, padx=12, pady=8)
        conteudo.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(conteudo, text=desc_limpa,
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=TEXT, anchor="w"
                     ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(conteudo, text=data_lanc or "Sem data",
                     font=ctk.CTkFont(size=11),
                     text_color=MUTED, anchor="w"
                     ).grid(row=1, column=0, sticky="w")
        ctk.CTkLabel(conteudo,
                     text=moeda(valor),
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=cor_valor
                     ).grid(row=0, column=1, rowspan=2, padx=16, sticky="e")

        # Botões
        frame_btn = ctk.CTkFrame(card, fg_color="transparent")
        frame_btn.pack(side="right", padx=(0, 12))
        ctk.CTkButton(frame_btn, text="", image=img_edit, width=28, height=28,
                      fg_color="transparent", hover_color="#EDF0F5",
                      command=lambda i=id_t, d=desc, dt=data_lanc:
                          abrir_opcoes_financeiro(app, i, d, dt)).pack(side="left", padx=2)
        ctk.CTkButton(frame_btn, text="", image=img_del, width=28, height=28,
                      fg_color="transparent", hover_color="#FFEEEE",
                      command=lambda i=id_t, d=desc:
                          confirmar_exclusao_financeiro(app, i, d)).pack(side="left", padx=2)

    app.update_idletasks()


def confirmar_exclusao_financeiro(app, id_t, desc):
    modal = ctk.CTkToplevel(app)
    modal.title("Confirmar exclusão")
    modal.geometry("400x220")
    modal.resizable(False, False)
    modal.attributes("-topmost", True)
    modal.grab_set()
    modal.configure(fg_color=BG)

    # Cabeçalho navy com título
    hdr = ctk.CTkFrame(modal, fg_color=NAVY, height=50, corner_radius=0)
    hdr.pack(fill="x")
    hdr.pack_propagate(False)
    ctk.CTkLabel(hdr, text="Confirmar Exclusão",
                 font=ctk.CTkFont(size=13, weight="bold"),
                 text_color="#FFFFFF").pack(pady=14)

    # Conteúdo
    ctk.CTkLabel(modal, text="Excluir este lançamento?",
                 font=ctk.CTkFont(size=14, weight="bold"),
                 text_color=TEXT).pack(pady=(20, 4))
    ctk.CTkLabel(modal, text=desc[:60],
                 font=ctk.CTkFont(size=11), text_color=MUTED,
                 wraplength=340).pack()

    # Botões — pack normal top-to-bottom, sem side="bottom"
    frame_btn = ctk.CTkFrame(modal, fg_color="transparent")
    frame_btn.pack(pady=24)

    def sim():
        modal.destroy()
        app.update_idletasks()
        apagar_transacao_com_reversao(app, id_t, desc)

    ctk.CTkButton(frame_btn, text="Excluir", fg_color=VERM, hover_color="#8B1A1A",
                  text_color="white", width=120, height=36, corner_radius=8,
                  font=ctk.CTkFont(weight="bold"), command=sim).pack(side="left", padx=8)
    ctk.CTkButton(frame_btn, text="Cancelar", fg_color=BG, hover_color=BORDA,
                  text_color=TEXT, border_width=1, border_color=BORDA,
                  width=120, height=36, corner_radius=8,
                  font=ctk.CTkFont(weight="bold"), command=modal.destroy).pack(side="left", padx=8)


def abrir_opcoes_financeiro(app, id_t, desc, data_atual):
    modal = ctk.CTkToplevel(app)
    modal.title("Editar Lançamento")
    modal.geometry("340x260")
    modal.attributes("-topmost", True)
    modal.grab_set()
    modal.configure(fg_color=BG)

    hdr = ctk.CTkFrame(modal, fg_color=NAVY, height=50, corner_radius=0)
    hdr.pack(fill="x")
    hdr.pack_propagate(False)
    ctk.CTkLabel(hdr, text="Alterar Data do Lançamento",
                 font=ctk.CTkFont(size=13, weight="bold"),
                 text_color="#FFFFFF").pack(pady=14)

    ctk.CTkLabel(modal, text=desc[:50], font=ctk.CTkFont(size=11),
                 text_color=MUTED).pack(pady=(14, 6))

    entry_data = ctk.CTkEntry(modal, placeholder_text="DD/MM/AAAA",
                               width=160, justify="center",
                               fg_color=CARD, border_color=BORDA)
    entry_data.pack(pady=4)
    entry_data.bind("<KeyRelease>", lambda e: formatar_data(entry_data, e))

    if data_atual and "Sem data" not in data_atual:
        entry_data.insert(0, data_atual)

    var_hoje = ctk.StringVar(value="")

    def toggle_hoje():
        if var_hoje.get() == "Hoje":
            hoje = datetime.now().strftime("%d/%m/%Y")
            entry_data.configure(state="normal")
            entry_data.delete(0, 'end')
            entry_data.insert(0, hoje)
            entry_data.configure(state="disabled")
        else:
            entry_data.configure(state="normal")

    ctk.CTkCheckBox(modal, text="Hoje", text_color=TEXT, font=ctk.CTkFont(weight="bold"),
                    variable=var_hoje, onvalue="Hoje", offvalue="",
                    fg_color=NAVY, hover_color="#253A56",
                    command=toggle_hoje).pack(pady=8)

    def salvar_data():
        nova_data = entry_data.get().strip()
        if len(nova_data) == 10:
            atualizar_data_transacao(id_t, nova_data)
            atualizar_tela_financeira(app)
            modal.destroy()

    ctk.CTkButton(modal, text="Salvar Data",
                  fg_color=NAVY, hover_color="#253A56", text_color="white",
                  font=ctk.CTkFont(weight="bold"),
                  width=160, corner_radius=8, command=salvar_data).pack(pady=(8, 16))


def apagar_transacao_com_reversao(app, id_t, desc):
    deletar_transacao(id_t)
    if desc.startswith("| "):
        num_acao = desc.replace("| ", "").strip()
        reverter_pagamento_processo(num_acao)
        app.notificacoes.append({
            "msg": f"Lançamento '{desc}' excluído. Processo voltou para 'Não Pagos'."
        })
        layout.atualizar_sino(app)
        if hasattr(processos, 'atualizar_lista_processos'):
            processos.atualizar_lista_processos(app)
    atualizar_tela_financeira(app)
