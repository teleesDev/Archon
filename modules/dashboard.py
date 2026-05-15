import customtkinter as ctk
from datetime import datetime
from PIL import Image
from modules import calendario

COR_NAVY   = "#1C2E45"
COR_GOLD   = "#C9A84C"
COR_GOLD_H = "#A8893C"
COR_BG     = "#F4F5F7"
COR_CARD   = "#FFFFFF"
COR_BORDA  = "#E0E3E8"
COR_TEXT   = "#1A1A2E"
COR_MUTED  = "#7A8499"
COR_VERDE  = "#1A7A4A"
COR_VERM   = "#B22222"
COR_AZUL   = "#1A5FAD"


def _icone(nome, tam):
    try:
        return ctk.CTkImage(Image.open(f"assets/{nome}"), size=tam)
    except:
        return None


def criar_dashboard(app, parent_frame):
    for widget in parent_frame.winfo_children():
        widget.destroy()

    parent_frame.configure(fg_color=COR_BG)
    parent_frame.grid_columnconfigure(0, weight=1)
    parent_frame.grid_rowconfigure(0, weight=0)
    parent_frame.grid_rowconfigure(1, weight=1)

    # ── Barra de atalhos ──────────────────────────────────────────────────────
    barra = ctk.CTkFrame(parent_frame, fg_color=COR_CARD, height=62, corner_radius=0)
    barra.grid(row=0, column=0, sticky="ew")
    barra.grid_propagate(False)
    barra.grid_columnconfigure(1, weight=1)

    # linha decorativa inferior fina
    ctk.CTkFrame(barra, height=1, fg_color=COR_BORDA, corner_radius=0).place(
        relx=0, rely=1.0, anchor="sw", relwidth=1.0
    )

    frame_btns = ctk.CTkFrame(barra, fg_color="transparent")
    frame_btns.grid(row=0, column=0, padx=20, pady=10, sticky="ns")

    _btn(frame_btns, "+ Novo Cliente",     COR_NAVY, "#FFFFFF",
         lambda: app.ir_para_novo_cliente()).pack(side="left", padx=(0, 8))
    _btn(frame_btns, "+ Novo Processo",    COR_NAVY, "#FFFFFF",
         lambda: app.ir_para_novo_processo()).pack(side="left", padx=(0, 8))
    _btn(frame_btns, "+ Novo Compromisso", COR_GOLD, "#1A1A2E",
         lambda: calendario.abrir_modal_evento(app)).pack(side="left")

    # Alerta de agenda
    try:
        from database.database import buscar_eventos_do_mes
        hoje = datetime.now()
        evs  = buscar_eventos_do_mes(hoje.month, hoje.year)
        eventos_hoje = [e for e in evs if e[4] == hoje.day]
    except:
        eventos_hoje = []

    frame_alerta = ctk.CTkFrame(barra, fg_color="transparent")
    frame_alerta.grid(row=0, column=1, padx=20, pady=10, sticky="e")

    if eventos_hoje:
        _btn(frame_alerta,
             f"  {len(eventos_hoje)} Evento(s) Hoje!",
             "#B22222", "#FFFFFF",
             lambda: app.selecionar_aba("Calendário")).pack()
    else:
        pill = ctk.CTkFrame(frame_alerta, fg_color="#E8F5EE", corner_radius=20,
                            border_width=1, border_color="#A8D5B5")
        pill.pack()
        ctk.CTkLabel(pill, text="  Agenda Livre Hoje",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color="#1A7A4A").pack(padx=16, pady=6)

    # ── Corpo ─────────────────────────────────────────────────────────────────
    frame_corpo = ctk.CTkFrame(parent_frame, fg_color="transparent")
    frame_corpo.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
    frame_corpo.grid_columnconfigure(0, weight=3, uniform="cols")
    frame_corpo.grid_columnconfigure(1, weight=0)
    frame_corpo.grid_columnconfigure(2, weight=2, uniform="cols")
    frame_corpo.grid_rowconfigure(0, weight=1)

    # ── COLUNA ESQUERDA ───────────────────────────────────────────────────────
    col_esq = ctk.CTkFrame(frame_corpo, fg_color=COR_CARD, corner_radius=14,
                           border_width=1, border_color=COR_BORDA)
    col_esq.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
    col_esq.grid_columnconfigure(0, weight=1)
    col_esq.grid_rowconfigure(4, weight=1)  # gráfico expande

    # Dados
    try:
        from database.database import buscar_processos
        lista_proc = buscar_processos()
    except:
        lista_proc = []

    total_p = len(lista_proc)

    def cnt(lista, alvo):
        return sum(1 for p in lista if alvo in [s.strip() for s in str(p[13]).split(",")])

    andamento = cnt(lista_proc, "Em Andamento")
    concluido = cnt(lista_proc, "Concluído")
    naopagos  = cnt(lista_proc, "Não Pagos")
    pagos     = cnt(lista_proc, "Pagos")
    cert_nao  = cnt(lista_proc, "Certidão Não-Emitida")
    cert_sim  = cnt(lista_proc, "Certidão Emitida")
    max_ref   = total_p if total_p > 0 else 1

    # Cabeçalho esq – sem emoji
    img_pag = _icone("icone_pagamentos.png", (20, 20))
    _secao_header(col_esq, "Controle de Pagamentos", img_pag, row=0)

    # Barras de progresso
    frame_barras = ctk.CTkFrame(col_esq, fg_color="transparent")
    frame_barras.grid(row=1, column=0, sticky="ew", padx=24, pady=(4, 0))
    frame_barras.grid_columnconfigure(0, weight=1)
    _barra(frame_barras, "Pagos",     pagos,    max_ref, COR_GOLD, 0)
    _barra(frame_barras, "Nao Pagos", naopagos, max_ref, COR_NAVY, 1)

    # Separador
    ctk.CTkFrame(col_esq, height=1, fg_color=COR_BORDA).grid(
        row=2, column=0, sticky="ew", padx=24, pady=16)

    # Cabeçalho gráfico
    img_dist = _icone("icone_distribuicao.png", (20, 20))
    _secao_header(col_esq, "Distribuicao de Processos", img_dist, row=3)

    # Gráfico de barras verticais
    frame_graph = ctk.CTkFrame(col_esq, fg_color="transparent")
    frame_graph.grid(row=4, column=0, sticky="nsew", padx=24, pady=(8, 24))

    # Separador entre CADA barra + largura generosa para não cortar texto
    # Grupos: Total | Andamento/Concluído | NãoPago/Pago | Cert.X/Cert.V
    dados = [
        ("Total",         total_p,  COR_NAVY),
        None,
        ("Andamento",     andamento, COR_GOLD),
        None,
        ("Concluído",     concluido, COR_GOLD),
        None,
        ("Não Pago",      naopagos,  COR_GOLD),
        None,
        ("Pago",          pagos,     COR_GOLD),
        None,
        ("Cert. Não",     cert_nao,  COR_GOLD),
        None,
        ("Cert. Sim",     cert_sim,  COR_GOLD),
    ]

    for item in dados:
        if item is None:
            sep = ctk.CTkFrame(frame_graph, width=1, fg_color=COR_BORDA, corner_radius=0)
            sep.pack(side="left", fill="y", padx=6, pady=8)
        else:
            label, valor, cor = item
            col_f = ctk.CTkFrame(frame_graph, fg_color="transparent")
            col_f.pack(side="left", fill="y", expand=True)
            col_f.pack_propagate(False)
            col_f.configure(width=62)   # largo o suficiente para "Andamento", "Cert. Não" etc.

            bar = ctk.CTkProgressBar(
                col_f, orientation="vertical",
                progress_color=cor,
                fg_color="#E8EBF0",
                width=16, corner_radius=4
            )
            bar.pack(expand=True, pady=(10, 4))
            bar.set(valor / max_ref)

            ctk.CTkLabel(col_f, text=str(valor),
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=COR_TEXT).pack()
            ctk.CTkLabel(col_f, text=label,
                         font=ctk.CTkFont(size=9),
                         text_color=COR_MUTED,
                         wraplength=60,        # nunca mais corta o texto
                         justify="center").pack(pady=(0, 6))

    # ── DIVISÓRIA ─────────────────────────────────────────────────────────────
    ctk.CTkFrame(frame_corpo, width=1, fg_color=COR_BORDA).grid(
        row=0, column=1, sticky="ns", padx=6, pady=10)

    # ── COLUNA DIREITA ────────────────────────────────────────────────────────
    col_dir = ctk.CTkFrame(frame_corpo, fg_color="transparent")
    col_dir.grid(row=0, column=2, sticky="nsew", padx=(10, 0))
    col_dir.grid_columnconfigure(0, weight=1)
    col_dir.grid_rowconfigure((1, 2, 3), weight=1, uniform="fcards")

    img_saude = _icone("icone_saude.png", (20, 20))
    _secao_header_stand(col_dir, "Controle Financeiro", img_saude, row=0)

    try:
        from database.database import resumo_financeiro
        r, d, s = resumo_financeiro()
    except:
        r, d, s = 0.0, 0.0, 0.0

    cor_saldo = COR_VERDE if s > 0 else (COR_GOLD if s == 0 else COR_VERM)

    _card_fin(col_dir, "Faturamento Bruto", r, COR_AZUL, row=1)
    _card_fin(col_dir, "Saidas / Despesas", d, COR_VERM,  row=2)
    _card_fin(col_dir, "Saldo em Caixa",    s, cor_saldo, row=3)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _btn(parent, texto, bg, fg, cmd):
    def _escurecer(h):
        try:
            r, g, b = int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)
            return f"#{int(r*.85):02X}{int(g*.85):02X}{int(b*.85):02X}"
        except:
            return h
    return ctk.CTkButton(
        parent, text=texto,
        font=ctk.CTkFont(family="Microsoft YaHei UI", size=12, weight="bold"),
        fg_color=bg, hover_color=_escurecer(bg), text_color=fg,
        height=38, corner_radius=8, command=cmd
    )


def _secao_header(parent, titulo, img, row):
    """Cabeçalho de seção com ícone opcional — sem emoji no texto."""
    f = ctk.CTkFrame(parent, fg_color="transparent")
    f.grid(row=row, column=0, sticky="ew", padx=24, pady=(20, 4))

    if img:
        ctk.CTkLabel(f, text="", image=img).pack(side="left", padx=(0, 8))

    ctk.CTkLabel(f, text=titulo,
                 font=ctk.CTkFont(size=14, weight="bold"),
                 text_color=COR_TEXT).pack(side="left")

    # Traço dourado pequeno decorativo
    ctk.CTkFrame(f, height=2, fg_color=COR_GOLD, corner_radius=1, width=36).pack(
        side="left", padx=10, pady=7)


def _secao_header_stand(parent, titulo, img, row):
    f = ctk.CTkFrame(parent, fg_color="transparent")
    f.grid(row=row, column=0, sticky="ew", pady=(0, 12))

    if img:
        ctk.CTkLabel(f, text="", image=img).pack(side="left", padx=(0, 8))

    ctk.CTkLabel(f, text=titulo,
                 font=ctk.CTkFont(size=15, weight="bold"),
                 text_color=COR_TEXT).pack(side="left")


def _barra(parent, titulo, valor, max_ref, cor, row_idx):
    pct = valor / max_ref if max_ref > 0 else 0
    f = ctk.CTkFrame(parent, fg_color="transparent")
    f.grid(row=row_idx, column=0, sticky="ew", pady=8)
    f.grid_columnconfigure(0, weight=1)

    info = ctk.CTkFrame(f, fg_color="transparent")
    info.grid(row=0, column=0, sticky="ew")
    ctk.CTkLabel(info, text=titulo,
                 font=ctk.CTkFont(size=12, weight="bold"),
                 text_color=COR_TEXT).pack(side="left")
    ctk.CTkLabel(info, text=str(valor),
                 font=ctk.CTkFont(size=12, weight="bold"),
                 text_color=cor).pack(side="right")

    pb = ctk.CTkProgressBar(f, progress_color=cor, fg_color="#E8EBF0",
                             height=10, corner_radius=5)
    pb.grid(row=1, column=0, sticky="ew", pady=(4, 0))
    pb.set(pct)


def _card_fin(parent, titulo, valor, cor_valor, row):
    card = ctk.CTkFrame(parent, fg_color=COR_CARD, corner_radius=12,
                        border_width=1, border_color=COR_BORDA)
    card.grid(row=row, column=0, sticky="nsew", pady=6)
    card.grid_columnconfigure(1, weight=1)

    # faixa lateral colorida
    ctk.CTkFrame(card, width=4, fg_color=cor_valor, corner_radius=0).grid(
        row=0, column=0, sticky="ns", rowspan=2, padx=(0, 0))

    ctk.CTkLabel(card, text=titulo,
                 font=ctk.CTkFont(size=13, weight="bold"),
                 text_color=COR_MUTED).grid(row=0, column=1, padx=(18, 20),
                                            pady=(20, 2), sticky="w")

    moeda = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    ctk.CTkLabel(card, text=moeda,
                 font=ctk.CTkFont(size=28, weight="bold"),
                 text_color=cor_valor).grid(row=1, column=1, padx=(18, 20),
                                            pady=(0, 20), sticky="w")
