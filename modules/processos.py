import customtkinter as ctk
from database.database import (
    adicionar_processo, adicionar_transacao, atualizar_processo_completo, 
    atualizar_status_processo, buscar_clientes, buscar_processos, buscar_processos_associados, 
    buscar_transacao_por_desc, deletar_processo, deletar_transacao, sincronizar_associacoes
)
from modules.utils import formatar_cnj
from modules import clientes, layout, estrategias
from PIL import Image

def atualizar_cores_abas_processos(app):
    if not hasattr(app, 'botoes_abas_processos'):
        return
        
    aba_atual = app.tabs_processos.get()
    
    for nome, btn in app.botoes_abas_processos.items():
        if nome == aba_atual:
            btn.configure(fg_color="#1C2E45", text_color="#C9A84C")
        else:
            btn.configure(fg_color="transparent", text_color="#1A1A2E")

def criar_aba_processos(app, parent_frame):
    parent_frame.grid_rowconfigure(0, weight=1)
    parent_frame.grid_columnconfigure(0, weight=1)

    app.frame_lista_processos = ctk.CTkFrame(parent_frame, fg_color="#F4F5F7")
    app.frame_lista_processos.grid(row=0, column=0, sticky="nsew")
    app.frame_lista_processos.grid_rowconfigure(1, weight=0) 
    app.frame_lista_processos.grid_rowconfigure(2, weight=1) 
    app.frame_lista_processos.grid_columnconfigure(0, weight=1)

    topo_frame = ctk.CTkFrame(app.frame_lista_processos, fg_color="transparent")
    topo_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))

    def on_focus_in(event, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, "end")
            entry.configure(text_color=("black", "white"))

    def on_focus_out(event, entry, placeholder):
        if entry.get() == "":
            entry.insert(0, placeholder)
            entry.configure(text_color="gray")

    app.entry_busca_proc = ctk.CTkEntry(topo_frame, height=35, border_width=1, border_color="#C0C8D5")
    app.entry_busca_proc.insert(0, "Buscar por Nome, CPF ou Nº do Processo...")
    app.entry_busca_proc.configure(text_color="gray")
    
    app.entry_busca_proc.pack(side="left", fill="x", expand=True, padx=(0, 20))
    app.entry_busca_proc.bind("<FocusIn>", lambda e: on_focus_in(e, app.entry_busca_proc, "Buscar por Nome, CPF ou Nº do Processo..."))
    app.entry_busca_proc.bind("<FocusOut>", lambda e: on_focus_out(e, app.entry_busca_proc, "Buscar por Nome, CPF ou Nº do Processo..."))
    app.entry_busca_proc.bind("<KeyRelease>", lambda e: atualizar_lista_processos(app, e))

    btn_novo_proc = ctk.CTkButton(topo_frame, text="+ Cadastrar Novo", width=150, height=35, 
                                  font=ctk.CTkFont(weight="bold"), 
                                  fg_color="#1C2E45", hover_color="#253A56", text_color="#FFFFFF",
                                  border_width=1, border_color=("#8A8A8A", "#5A5A5A"),
                                  command=lambda: mostrar_form_processo(app))
    btn_novo_proc.pack(side="right")

    header_customizado = ctk.CTkFrame(app.frame_lista_processos, fg_color="transparent")
    header_customizado.grid(row=1, column=0, padx=20, pady=(25, 10), sticky="") 

    if not hasattr(app, "foco_global_configurado"):
        def remover_foco_global(event):
            try:
                nome_widget = str(event.widget).lower()
                if "entry" not in nome_widget and "text" not in nome_widget:
                    app.focus_set()
            except: pass
        app.bind_all("<Button-1>", remover_foco_global, add="+")
        app.foco_global_configurado = True

    # AJUSTE: fg_color="transparent" resolve o glitch visual de bordas estranhas nas abas customizadas
    _card_proc = ctk.CTkFrame(app.frame_lista_processos, fg_color="#FFFFFF",
                               corner_radius=15, border_width=1, border_color="#E0E3E8")
    _card_proc.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))
    _card_proc.grid_rowconfigure(0, weight=1)
    _card_proc.grid_columnconfigure(0, weight=1)

    app.tabs_processos = ctk.CTkTabview(_card_proc, fg_color="transparent",
                                         bg_color="#FFFFFF", corner_radius=12)
    app.tabs_processos.grid(row=0, column=0, sticky="nsew")

    grupos_abas = [
        ["Todos"],
        ["Em Andamento", "Concluído"],
        ["Não Pagos", "Pagos"],
        ["Certidão Não-Emitida", "Certidão Emitida"],
        ["Cancelados"]
    ]

    app.botoes_abas_processos = {}
    app.scrolls_processos = {}

    def alterar_aba_customizada(a):
        app.tabs_processos.set(a)
        
        if hasattr(app, 'redirecionado_proc') and app.redirecionado_proc:
            app.entry_busca_proc.delete(0, 'end')
            app.entry_busca_proc.insert(0, "Buscar por Nome, CPF ou Nº do Processo...")
            app.entry_busca_proc.configure(text_color="gray")
            app.redirecionado_proc = False
            atualizar_lista_processos(app)

        atualizar_cores_abas_processos(app)

    for grupo in grupos_abas:
        bloco = ctk.CTkFrame(header_customizado, fg_color="#EDF0F5", corner_radius=8, border_width=1, border_color="#E0E3E8")
        bloco.pack(side="left", padx=8)

        for i, aba in enumerate(grupo):
            app.tabs_processos.add(aba)

            btn = ctk.CTkButton(
                bloco, text=aba, height=26, corner_radius=5,
                font=ctk.CTkFont(family="Microsoft YaHei UI", size=12, weight="bold"),
                fg_color="transparent", hover_color="#D8DCE5",
                command=lambda a=aba: alterar_aba_customizada(a)
            )
            btn.pack(side="left", padx=2, pady=2)
            app.botoes_abas_processos[aba] = btn

            if i < len(grupo) - 1:
                ctk.CTkFrame(bloco, width=1, height=14, fg_color=("gray60", "gray40")).pack(side="left", padx=4)

            tab_frame = app.tabs_processos.tab(aba)
            scroll = ctk.CTkScrollableFrame(tab_frame, corner_radius=15, fg_color="transparent")
            scroll.pack(expand=True, fill="both")
            app.scrolls_processos[aba] = scroll

    app.tabs_processos._segmented_button.grid_forget()
    app.tabs_processos._segmented_button.configure(height=0) 
    app.tabs_processos._segmented_button.grid = lambda *args, **kwargs: None

    atualizar_cores_abas_processos(app)

    app.frame_form_processo = ctk.CTkFrame(parent_frame, fg_color="#F4F5F7")
    app.frame_form_processo.grid_rowconfigure(0, weight=1)
    app.frame_form_processo.grid_columnconfigure(0, weight=1)

    scroll_form_proc = ctk.CTkScrollableFrame(app.frame_form_processo, fg_color="#F4F5F7")
    scroll_form_proc.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    scroll_form_proc.grid_columnconfigure(0, weight=1)

    # form_box: exatamente igual ao de clientes — 2 colunas, largura fixa
    form_box_proc = ctk.CTkFrame(scroll_form_proc, corner_radius=15, width=600)
    form_box_proc.grid(row=0, column=0, pady=10, sticky="n")
    form_box_proc.grid_columnconfigure(0, weight=0)   # col labels
    form_box_proc.grid_columnconfigure(1, weight=1)   # col campos

    # ── Linha 0: Voltar (col 0) + Título (col 1, centralizado) ────────────────
    try:
        img_voltar = ctk.CTkImage(Image.open("assets/icone_voltar.png"), size=(20, 20))
    except:
        img_voltar = None

    btn_voltar = ctk.CTkButton(
        form_box_proc,
        text="←" if not img_voltar else "",
        image=img_voltar, width=30, height=30,
        fg_color="transparent", hover_color="#E0E3E8", text_color="#1A1A2E",
        command=lambda: mostrar_lista_processos(app)
    )
    btn_voltar.grid(row=0, column=0, sticky="nw", padx=20, pady=(20, 10))

    frame_titulo = ctk.CTkFrame(form_box_proc, fg_color="transparent")
    frame_titulo.grid(row=0, column=0, columnspan=2, pady=(24, 20), sticky="")

    try:
        img_form = ctk.CTkImage(Image.open("assets/icone_formulario_proc.png"), size=(24, 24))
    except:
        img_form = None

    if img_form:
        ctk.CTkLabel(frame_titulo, text="", image=img_form).pack(side="left", padx=(15, 10))
    ctk.CTkLabel(frame_titulo, text="Registro de Processo",
                 font=ctk.CTkFont(size=22, weight="bold"),
                 text_color="#1A1A2E").pack(side="left")
    if img_form:
        ctk.CTkLabel(frame_titulo, text="", image=img_form).pack(side="left", padx=(10, 0))

    # ── Helper de label (col 0, sticky="w") ───────────────────────────────────
    def _lbl(row, texto, sticky_v="w"):
        ctk.CTkLabel(form_box_proc, text=texto,
                     text_color="#1A1A2E",
                     font=ctk.CTkFont(weight="bold")
                     ).grid(row=row, column=0, padx=20, pady=7, sticky=sticky_v)

    app.entradas_proc = {}
    linha = 1

    # ── Linha 1: Nome do Contratante ───────────────────────────────────────────
    _lbl(linha, "Nome do Contratante: *")
    frame_nome = ctk.CTkFrame(form_box_proc, fg_color="transparent")
    frame_nome.grid(row=linha, column=1, padx=(0, 20), pady=7, sticky="ew")
    frame_nome.grid_columnconfigure(0, weight=1)

    entrada_nome = ctk.CTkEntry(frame_nome, width=350)
    entrada_nome.grid(row=0, column=0, sticky="ew")
    entrada_nome.insert(0, "[Seleção de Cliente]")
    entrada_nome.configure(state="disabled")
    app.entradas_proc["Nome do Contratante: *"] = entrada_nome

    app.btn_buscar_cli_proc = ctk.CTkButton(
        frame_nome, text="▼", width=34, height=34,
        fg_color="#1C2E45", hover_color="#253A56", text_color="white",
        command=lambda: alternar_busca_cliente_proc(app)
    )
    app.btn_buscar_cli_proc.grid(row=0, column=1, padx=(6, 0))

    ctk.CTkButton(
        frame_nome, text="+", width=34, height=34,
        font=ctk.CTkFont(weight="bold", size=16),
        fg_color="#C9A84C", hover_color="#A8893C", text_color="#1A1A2E",
        command=app.ir_para_novo_cliente
    ).grid(row=0, column=2, padx=(5, 0))
    linha += 1

    # ── Dropdown busca cliente (col 1) ─────────────────────────────────────────
    app.frame_busca_cliente = ctk.CTkFrame(form_box_proc, fg_color="#F0F3F7",
                                            corner_radius=8,
                                            border_width=1, border_color="#E0E3E8")
    app.linha_busca_cliente = linha

    app.var_tipo_busca_cli = ctk.StringVar(value="Pessoa Física")
    frame_radios_cli = ctk.CTkFrame(app.frame_busca_cliente, fg_color="transparent")
    frame_radios_cli.pack(pady=(10, 5))
    ctk.CTkRadioButton(frame_radios_cli, text="Física",
                       variable=app.var_tipo_busca_cli, value="Pessoa Física",
                       command=lambda: atualizar_resultados_busca_cli(app)).pack(side="left", padx=10)
    ctk.CTkRadioButton(frame_radios_cli, text="Jurídica",
                       variable=app.var_tipo_busca_cli, value="Pessoa Jurídica",
                       command=lambda: atualizar_resultados_busca_cli(app)).pack(side="left", padx=10)

    app.entry_busca_nome_cli = ctk.CTkEntry(app.frame_busca_cliente,
                                             placeholder_text="Pesquisar nome...")
    app.entry_busca_nome_cli.pack(fill="x", padx=10, pady=5)
    app.entry_busca_nome_cli.bind("<KeyRelease>",
                                   lambda e: atualizar_resultados_busca_cli(app, e))
    app.scroll_busca_cli = ctk.CTkScrollableFrame(app.frame_busca_cliente, height=100)
    app.scroll_busca_cli.pack(fill="x", padx=10, pady=(0, 10))
    linha += 1

    app.processos_associados_temporarios = []

    # ── Linha N° da Ação (CNJ) ─────────────────────────────────────────────────
    _lbl(linha, "N° da Ação (CNJ): *")
    frame_cnj = ctk.CTkFrame(form_box_proc, fg_color="transparent")
    frame_cnj.grid(row=linha, column=1, padx=(0, 20), pady=7, sticky="ew")
    frame_cnj.grid_columnconfigure(0, weight=1)
    entrada_cnj = ctk.CTkEntry(frame_cnj, width=350)
    entrada_cnj.grid(row=0, column=0, sticky="ew")
    entrada_cnj.bind("<KeyRelease>", lambda e, w=entrada_cnj: formatar_cnj(w, e))
    app.entradas_proc["N° da Ação (CNJ): *"] = entrada_cnj
    linha += 1

    # ── Processos Associados — col 1, centralizado igual título ───────────────
    app.frame_assoc_temporarias = ctk.CTkFrame(form_box_proc, fg_color="transparent")
    app.frame_assoc_temporarias.grid(row=linha, column=1, padx=(0, 20), pady=(0, 6), sticky="w")
    linha += 1

    # ── Campos simples ─────────────────────────────────────────────────────────
    for texto in ["Razão do Contrato: *", "Atuação: *", "Vara: "]:
        _lbl(linha, texto)
        ent = ctk.CTkEntry(form_box_proc, width=350)
        ent.grid(row=linha, column=1, padx=(0, 20), pady=7, sticky="ew")
        app.entradas_proc[texto] = ent
        linha += 1

    # ── Observações ────────────────────────────────────────────────────────────
    _lbl(linha, "Observações:", sticky_v="nw")
    app.txt_obs_proc = ctk.CTkTextbox(form_box_proc, width=350, height=80)
    app.txt_obs_proc.grid(row=linha, column=1, padx=(0, 20), pady=7, sticky="ew")
    linha += 1

    # ── Separador ─────────────────────────────────────────────────────────────
    ctk.CTkFrame(form_box_proc, height=1, fg_color="#E0E3E8").grid(
        row=linha, column=0, columnspan=2, sticky="ew", padx=20, pady=(12, 0))
    linha += 1

    # ── "Configuração de Valores *" — col 1, centralizado ────────────────────
    ctk.CTkLabel(form_box_proc, text="Configuração de Valores *",
                 font=ctk.CTkFont(size=15, weight="bold"),
                 text_color="#1A1A2E"
                 ).grid(row=linha, column=0, columnspan=2, pady=(28, 8), sticky="")
    linha += 1

    # ── Radio buttons — col 1, centralizado ───────────────────────────────────
    app.var_tipo_valor = ctk.StringVar(value="")
    frame_radios_val = ctk.CTkFrame(form_box_proc, fg_color="transparent")
    frame_radios_val.grid(row=linha, column=0, columnspan=2, pady=(0, 16), sticky="")
    ctk.CTkRadioButton(frame_radios_val, text="Porcentagem (%)",
                       font=ctk.CTkFont(weight="bold"),
                       variable=app.var_tipo_valor, value="Porcentagem",
                       command=lambda: alternar_campos_valor_proc(app)).pack(side="left", padx=(20, 15))
    ctk.CTkRadioButton(frame_radios_val, text="Fixo ou Parcelado",
                       font=ctk.CTkFont(weight="bold"),
                       variable=app.var_tipo_valor, value="Fixo",
                       command=lambda: alternar_campos_valor_proc(app)).pack(side="left", padx=15)
    ctk.CTkRadioButton(frame_radios_val, text="Pro Bono",
                       font=ctk.CTkFont(weight="bold"),
                       variable=app.var_tipo_valor, value="Pro Bono",
                       command=lambda: alternar_campos_valor_proc(app)).pack(side="left", padx=15)
    linha += 1

    # ── Frame Porcentagem ─────────────────────────────────────────────────────
    app.frame_pct = ctk.CTkFrame(form_box_proc, fg_color="transparent")
    app.frame_pct.grid_columnconfigure(0, weight=0)
    app.frame_pct.grid_columnconfigure(1, weight=1)

    def _lbl_pct(r, t):
        ctk.CTkLabel(app.frame_pct, text=t, text_color="#1A1A2E",
                     font=ctk.CTkFont(weight="bold")).grid(
                     row=r, column=0, padx=20, pady=7, sticky="w")

    _lbl_pct(0, "% *")
    app.entry_pct = ctk.CTkEntry(app.frame_pct, width=350, placeholder_text="Ex: 10")
    app.entry_pct.grid(row=0, column=1, padx=(0, 20), pady=7, sticky="ew")
    app.entry_pct.bind("<KeyRelease>", lambda e: calcular_conversao(app, e))

    _lbl_pct(1, "Proveito (R$) *")
    app.entry_proveito = ctk.CTkEntry(app.frame_pct, width=350, placeholder_text="Ex: 5000")
    app.entry_proveito.grid(row=1, column=1, padx=(0, 20), pady=7, sticky="ew")
    app.entry_proveito.bind("<KeyRelease>", lambda e: calcular_conversao(app, e))

    _lbl_pct(2, "Conversão *")
    app.entry_conversao = ctk.CTkEntry(app.frame_pct, width=350, state="disabled",
                                        text_color="#1f9c46", font=ctk.CTkFont(weight="bold"))
    app.entry_conversao.grid(row=2, column=1, padx=(0, 20), pady=7, sticky="ew")

    # ── Frame Fixo ────────────────────────────────────────────────────────────
    app.frame_fixo = ctk.CTkFrame(form_box_proc, fg_color="transparent")
    app.frame_fixo.grid_columnconfigure(0, weight=0)
    app.frame_fixo.grid_columnconfigure(1, weight=1)

    def _lbl_fixo(r, t):
        ctk.CTkLabel(app.frame_fixo, text=t, text_color="#1A1A2E",
                     font=ctk.CTkFont(weight="bold")).grid(
                     row=r, column=0, padx=20, pady=7, sticky="w")

    _lbl_fixo(0, "Valor Fixo (R$) *")
    app.entry_valor_fixo = ctk.CTkEntry(app.frame_fixo, width=350)
    app.entry_valor_fixo.grid(row=0, column=1, padx=(0, 20), pady=7, sticky="ew")

    _lbl_fixo(1, "Qtd. Parcelas *")
    app.entry_parcelas = ctk.CTkEntry(app.frame_fixo, width=350)
    app.entry_parcelas.grid(row=1, column=1, padx=(0, 20), pady=7, sticky="ew")

    _lbl_fixo(2, "Parcelas Pagas *")
    app.entry_parcelas_adim = ctk.CTkEntry(app.frame_fixo, width=350)
    app.entry_parcelas_adim.grid(row=2, column=1, padx=(0, 20), pady=7, sticky="ew")

    app.linha_dinamica_proc = linha   # linha onde frame_pct/fixo aparecem

    # ── Separador ─────────────────────────────────────────────────────────────
    ctk.CTkFrame(form_box_proc, height=1, fg_color="#E0E3E8").grid(
        row=97, column=0, columnspan=2, sticky="ew", padx=20, pady=(12, 0))

    # ── "Exibição nas Abas (Checklist) *" — col 1, centralizado ──────────────
    ctk.CTkLabel(form_box_proc, text="Exibição nas Abas (Checklist) *",
                 font=ctk.CTkFont(size=15, weight="bold"),
                 text_color="#1A1A2E"
                 ).grid(row=98, column=0, columnspan=2, pady=(28, 10), sticky="")

    # ── Checkboxes — col 1, centralizado ──────────────────────────────────────
    frame_status = ctk.CTkFrame(form_box_proc, fg_color="transparent")
    frame_status.grid(row=99, column=0, columnspan=2, pady=(0, 20), sticky="")

    app.var_st_andamento = ctk.StringVar(value="Em Andamento")
    app.var_st_concluido = ctk.StringVar(value="")
    app.var_st_pago      = ctk.StringVar(value="")
    app.var_st_naopago   = ctk.StringVar(value="")
    app.var_st_certsim   = ctk.StringVar(value="")
    app.var_st_certnao   = ctk.StringVar(value="")
    app.var_st_cancelado = ctk.StringVar(value="")

    def regra_cancelado():
        if app.var_st_cancelado.get():
            app.var_st_andamento.set(""); app.var_st_concluido.set("")
            app.var_st_pago.set(""); app.var_st_naopago.set("")
            app.var_st_certsim.set(""); app.var_st_certnao.set("")
    def regra_andamento():
        if app.var_st_andamento.get():
            app.var_st_concluido.set(""); app.var_st_cancelado.set("")
    def regra_concluido():
        if app.var_st_concluido.get():
            app.var_st_andamento.set(""); app.var_st_cancelado.set("")
    def regra_pago():
        if app.var_st_pago.get():
            app.var_st_naopago.set(""); app.var_st_cancelado.set("")
    def regra_naopago():
        if app.var_st_naopago.get():
            app.var_st_pago.set(""); app.var_st_cancelado.set("")
    def regra_certsim():
        if app.var_st_certsim.get():
            app.var_st_certnao.set(""); app.var_st_cancelado.set("")
    def regra_certnao():
        if app.var_st_certnao.get():
            app.var_st_certsim.set(""); app.var_st_cancelado.set("")

    ctk.CTkCheckBox(frame_status, text="Em Andamento", font=ctk.CTkFont(weight="bold"),
                    variable=app.var_st_andamento, onvalue="Em Andamento", offvalue="",
                    command=regra_andamento).grid(row=0, column=0, padx=12, pady=8, sticky="w")
    ctk.CTkCheckBox(frame_status, text="Concluído", font=ctk.CTkFont(weight="bold"),
                    variable=app.var_st_concluido, onvalue="Concluído", offvalue="",
                    command=regra_concluido).grid(row=1, column=0, padx=12, pady=8, sticky="w")
    ctk.CTkCheckBox(frame_status, text="Não Pagos", font=ctk.CTkFont(weight="bold"),
                    variable=app.var_st_naopago, onvalue="Não Pagos", offvalue="",
                    command=regra_naopago).grid(row=0, column=1, padx=12, pady=8, sticky="w")
    ctk.CTkCheckBox(frame_status, text="Pagos", font=ctk.CTkFont(weight="bold"),
                    variable=app.var_st_pago, onvalue="Pagos", offvalue="",
                    command=regra_pago).grid(row=1, column=1, padx=12, pady=8, sticky="w")
    ctk.CTkCheckBox(frame_status, text="Certidão Não-Emitida", font=ctk.CTkFont(weight="bold"),
                    variable=app.var_st_certnao, onvalue="Certidão Não-Emitida", offvalue="",
                    command=regra_certnao).grid(row=0, column=2, padx=12, pady=8, sticky="w")
    ctk.CTkCheckBox(frame_status, text="Certidão Emitida", font=ctk.CTkFont(weight="bold"),
                    variable=app.var_st_certsim, onvalue="Certidão Emitida", offvalue="",
                    command=regra_certsim).grid(row=1, column=2, padx=12, pady=8, sticky="w")

    app.chk_cancelado = ctk.CTkCheckBox(
        frame_status, text="Cancelado", font=ctk.CTkFont(weight="bold"),
        variable=app.var_st_cancelado, onvalue="Cancelado", offvalue="",
        command=regra_cancelado, text_color="#d93838"
    )
    app.chk_cancelado.grid(row=2, column=0, padx=12, pady=8, sticky="w")
    app.chk_cancelado.grid_remove()

    # ── Botão Salvar ───────────────────────────────────────────────────────────
    app.btn_salvar_proc = ctk.CTkButton(
        form_box_proc, text="Salvar Processo",
        font=ctk.CTkFont(weight="bold"),
        fg_color="#C9A84C", hover_color="#A8893C", text_color="#1A1A2E",
        command=lambda: salvar_processo(app)
    )
    app.btn_salvar_proc.grid(row=100, column=0, columnspan=2,
                              pady=(20, 20), padx=20, sticky="ew")

    mostrar_lista_processos(app)

def redirecionar_para_cliente(app, nome_cliente, tipo_pessoa):
    try:
        if hasattr(app, 'frame_form_cliente') and hasattr(app, 'frame_lista_clientes'):
            app.frame_form_cliente.grid_forget()
            app.frame_lista_clientes.grid(row=0, column=0, sticky="nsew")

        if hasattr(app, 'selecionar_aba'):
            app.selecionar_aba("Meus Clientes")
        
        if hasattr(app, 'tabs_pf_pj'):
            app.tabs_pf_pj.set(tipo_pessoa)
            if app.tabs_pf_pj._command:
                app.tabs_pf_pj._command()

        app.redirecionado_cli = True

        if hasattr(app, 'entry_busca_cliente'):
            app.entry_busca_cliente.delete(0, 'end')
            app.entry_busca_cliente.insert(0, "Buscar por Nome, CPF ou CNPJ...")
            app.entry_busca_cliente.configure(text_color="gray")
            
        app.cliente_expandir_alvo = nome_cliente
        
        if hasattr(clientes, 'atualizar_lista_clientes'):
            clientes.atualizar_lista_clientes(app)
            
        if hasattr(app, 'entry_busca_proc'):
            app.entry_busca_proc.delete(0, 'end')
            app.entry_busca_proc.insert(0, "Buscar por Nome, CPF ou Nº do Processo...")
            app.entry_busca_proc.configure(text_color="gray")
            
    except Exception as e:
        print(f"Erro ao redirecionar para cliente: {e}")

def mostrar_lista_processos(app):
    app.frame_form_processo.grid_forget()
    app.frame_lista_processos.grid(row=0, column=0, sticky="nsew")
    atualizar_lista_processos(app)

def alternar_campos_valor_proc(app):
    app.frame_fixo.grid_forget()
    app.frame_pct.grid_forget()
    
    if app.var_tipo_valor.get() == "Porcentagem":
        app.frame_pct.grid(row=app.linha_dinamica_proc, column=0, columnspan=2, sticky="ew", pady=4)
    elif app.var_tipo_valor.get() == "Fixo":
        app.frame_fixo.grid(row=app.linha_dinamica_proc, column=0, columnspan=2, sticky="ew", pady=4)

def calcular_conversao(app, event=None):
    pct_str = app.entry_pct.get().replace(",", ".")
    proveito_str = app.entry_proveito.get().replace(",", ".")
    try:
        if pct_str and proveito_str:
            pct = float(pct_str)
            proveito = float(proveito_str)
            conversao = proveito * (pct / 100)
            app.entry_conversao.configure(state="normal")
            app.entry_conversao.delete(0, "end")
            texto_formatado = f"R$ {conversao:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            app.entry_conversao.insert(0, texto_formatado)
            app.entry_conversao.configure(state="disabled")
        else:
            app.entry_conversao.configure(state="normal")
            app.entry_conversao.delete(0, "end")
            app.entry_conversao.configure(state="disabled")
    except ValueError:
        app.entry_conversao.configure(state="normal")
        app.entry_conversao.delete(0, "end")
        app.entry_conversao.insert(0, "Aguardando...")
        app.entry_conversao.configure(state="disabled")

def alternar_busca_cliente_proc(app):
    if app.frame_busca_cliente.winfo_ismapped():
        app.frame_busca_cliente.grid_forget()
        app.btn_buscar_cli_proc.configure(text="▼")
    else:
        app.frame_busca_cliente.grid(row=app.linha_busca_cliente, column=1, padx=(0, 20), pady=(0, 10), sticky="ew")
        app.btn_buscar_cli_proc.configure(text="▲")
        atualizar_resultados_busca_cli(app)

def atualizar_resultados_busca_cli(app, event=None):
    for w in app.scroll_busca_cli.winfo_children():
        w.destroy()
    termo = app.entry_busca_nome_cli.get()
    tipo_req = app.var_tipo_busca_cli.get()
    try: clientes_list = buscar_clientes(termo)
    except: clientes_list = []
    
    clientes_filtrados = [c for c in clientes_list if c[1] == tipo_req]

    if not clientes_filtrados:
        ctk.CTkLabel(app.scroll_busca_cli, text="Nenhum cliente encontrado.", text_color="gray").pack(pady=10)
        return

    for c in clientes_filtrados:
        nome = c[2]
        btn = ctk.CTkButton(app.scroll_busca_cli, text=nome, fg_color="transparent", text_color=("black", "white"), anchor="w", hover_color=("gray80", "gray25"), 
                            command=lambda n=nome: selecionar_cliente_proc(app, n))
        btn.pack(fill="x", pady=2)

def selecionar_cliente_proc(app, nome):
    entrada = app.entradas_proc["Nome do Contratante: *"]
    entrada.configure(state="normal")
    entrada.delete(0, 'end')
    entrada.insert(0, nome)
    entrada.configure(state="disabled")
    app.frame_busca_cliente.grid_forget()
    app.btn_buscar_cli_proc.configure(text="▼")

def atualizar_lista_assoc_form(app):
    for w in app.frame_assoc_temporarias.winfo_children(): w.destroy()
    
    qtd = len(app.processos_associados_temporarios)
    texto = f"{qtd} processo selecionado" if qtd == 1 else f"{qtd} processos selecionados"
    
    ctk.CTkLabel(app.frame_assoc_temporarias, text=f"Processos Associados: {texto}", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=(0, 10))
    ctk.CTkButton(app.frame_assoc_temporarias, text="+ Gerenciar", height=24, fg_color="#C9A84C", text_color="#1A1A2E", hover_color="#A8893C", font=ctk.CTkFont(weight="bold", size=11), command=lambda: abrir_seletor_processos(app)).pack(side="left", padx=10)

def mostrar_form_processo(app):
    app.id_edicao_proc = None 
    app.processos_associados_temporarios = [] 
    app.chk_cancelado.grid_remove() 
    atualizar_lista_assoc_form(app)
    
    if hasattr(app, "lbl_erro_proc"):
        app.lbl_erro_proc.configure(text="")
    
    app.entradas_proc["Nome do Contratante: *"].configure(state="normal")
    for entrada in app.entradas_proc.values(): 
        entrada.delete(0, 'end')
    app.entradas_proc["Nome do Contratante: *"].insert(0, "[Seleção de Cliente]")
    app.entradas_proc["Nome do Contratante: *"].configure(state="disabled")
    
    app.txt_obs_proc.delete("0.0", "end")

    app.entry_pct.delete(0, 'end')
    app.entry_proveito.delete(0, 'end')
    app.entry_conversao.configure(state="normal")
    app.entry_conversao.delete(0, 'end')
    app.entry_conversao.configure(state="disabled")
    app.entry_valor_fixo.delete(0, 'end')
    app.entry_parcelas.delete(0, 'end')
    app.entry_parcelas_adim.delete(0, 'end')
    
    app.var_tipo_valor.set("Porcentagem")
    alternar_campos_valor_proc(app)
    
    app.var_st_andamento.set("Em Andamento")
    app.var_st_concluido.set("")
    app.var_st_pago.set("")
    app.var_st_naopago.set("")
    app.var_st_certsim.set("")
    app.var_st_certnao.set("")
    app.var_st_cancelado.set("")

    app.frame_lista_processos.grid_forget()
    app.frame_form_processo.grid(row=0, column=0, sticky="nsew")

def salvar_processo(app):
    if getattr(app, "linha_erro_criada", False) is False:
        app.lbl_erro_proc = ctk.CTkLabel(app.btn_salvar_proc.master, text="",
                                          text_color="#d93838",
                                          font=ctk.CTkFont(weight="bold"),
                                          wraplength=500)
        app.lbl_erro_proc.grid(row=101, column=0, columnspan=2, pady=(4, 8))
        app.linha_erro_criada = True
        
    app.lbl_erro_proc.configure(text="") 

    nome = app.entradas_proc["Nome do Contratante: *"].get().strip()
    acao = app.entradas_proc["N° da Ação (CNJ): *"].get().strip()
    razao = app.entradas_proc["Razão do Contrato: *"].get().strip()
    atuacao = app.entradas_proc["Atuação: *"].get().strip()
    vara = app.entradas_proc["Vara: "].get().strip()
    obs = app.txt_obs_proc.get("0.0", "end").strip()
    tipo_v = app.var_tipo_valor.get()

    status_selecionados = [
        app.var_st_andamento.get(), app.var_st_concluido.get(), 
        app.var_st_pago.get(), app.var_st_naopago.get(), 
        app.var_st_certsim.get(), app.var_st_certnao.get(), 
        app.var_st_cancelado.get()
    ]
    status_final = ",".join([s for s in status_selecionados if s]) 

    if "Seleção" in nome or not nome:
        app.lbl_erro_proc.configure(text="ERRO: Selecione um Contratante.")
        return
    if len(acao) != 25:
        app.lbl_erro_proc.configure(text="ERRO: O N° da Ação (CNJ) deve ter 25 caracteres.")
        return
    if not razao or not atuacao:
        app.lbl_erro_proc.configure(text="ERRO: Preencha a Razão do Contrato e a Atuação.")
        return
    if not status_final:
        app.lbl_erro_proc.configure(text="ERRO: Selecione ao menos um status nas Abas de Exibição.")
        return

    def limpa_valor(val_str):
        clean = str(val_str).replace(".", "").replace(",", ".")
        try: return float(clean)
        except: return 0.0

    pct = prov = conv = v_fixo = parc = parc_pagas = 0.0
    
    ignorar_validacao_valores = (app.var_st_naopago.get() == "Não Pagos") or (app.var_st_cancelado.get() == "Cancelado")
    
    if tipo_v == "Porcentagem":
        pct = limpa_valor(app.entry_pct.get())
        prov = limpa_valor(app.entry_proveito.get())
        conv = prov * (pct / 100)
        
        if not ignorar_validacao_valores:
            if pct <= 0 or prov <= 0:
                app.lbl_erro_proc.configure(text="ERRO: Preencha a Porcentagem e o Proveito corretamente.")
                return

    elif tipo_v == "Fixo":
        v_fixo = limpa_valor(app.entry_valor_fixo.get())
        try:
            parc = int(app.entry_parcelas.get() or 0)
            parc_pagas = int(app.entry_parcelas_adim.get() or 0)
        except:
            parc = 0
            parc_pagas = 0
            
        if not ignorar_validacao_valores:
            if v_fixo <= 0:
                app.lbl_erro_proc.configure(text="ERRO: Preencha o Valor Fixo corretamente.")
                return
            if parc <= 0:
                app.lbl_erro_proc.configure(text="ERRO: Informe a quantidade de parcelas (mínimo 1).")
                return

    elif tipo_v == "Pro Bono":
        pass 
    else:
        app.lbl_erro_proc.configure(text="ERRO: Selecione a Configuração de Valores (%, Fixo ou Pro Bono).")
        return

    id_edicao = getattr(app, "id_edicao_proc", None)
    if id_edicao:
        from database.database import atualizar_processo_completo
        atualizar_processo_completo(id_edicao, nome, acao, razao, atuacao, vara, tipo_v, pct, prov, conv, v_fixo, parc, parc_pagas, status_final, obs)
    else:
        from database.database import adicionar_processo
        adicionar_processo(nome, acao, razao, atuacao, vara, tipo_v, pct, prov, conv, v_fixo, parc, parc_pagas, status_final, obs)
    
    try:
        from database.database import sincronizar_associacoes
        sincronizar_associacoes(acao, app.processos_associados_temporarios)
    except Exception as e:
        print(f"Erro ao sincronizar associações: {e}")
    
    from database.database import buscar_transacao_por_desc, adicionar_transacao, deletar_transacao
    desc_fin = f"| {acao}"
    transacao_existente = buscar_transacao_por_desc(desc_fin)
    
    is_pago = bool(app.var_st_pago.get())
    
    if is_pago and tipo_v != "Pro Bono" and not app.var_st_cancelado.get():
        if not transacao_existente:
            valor_receita = conv if tipo_v == "Porcentagem" else v_fixo
            adicionar_transacao(desc_fin, valor_receita, "Receita (+)", "") 
    else:
        if transacao_existente:
            deletar_transacao(transacao_existente[0])
            app.notificacoes.append({"msg": f"Processo {acao} foi removido do financeiro.", "cor": "info"})
            try:
                from modules import layout
                layout.atualizar_sino(app)
            except: pass

    mostrar_lista_processos(app)


def desassociar_processos_rapido(app, acao_pai, acao_remover):
    try:
        from database.database import buscar_processos_associados, sincronizar_associacoes
        
        assoc_pai = list(buscar_processos_associados(acao_pai))
        if acao_remover in assoc_pai: assoc_pai.remove(acao_remover)
        sincronizar_associacoes(acao_pai, assoc_pai)
        
        assoc_filho = list(buscar_processos_associados(acao_remover))
        if acao_pai in assoc_filho: assoc_filho.remove(acao_pai)
        sincronizar_associacoes(acao_remover, assoc_filho)
        
        app.notificacoes.append({"msg": f"Vínculo com {acao_remover} foi removido.", "cor": "alerta"})
        from modules import layout
        try: layout.atualizar_sino(app)
        except: pass
        
        atualizar_lista_processos(app)
    except Exception as e:
        print(f"Erro ao desassociar: {e}")

def abrir_modal_add_assoc_rapida(app, acao_pai):
    modal = ctk.CTkToplevel(app)
    modal.title("Vincular Processo")
    modal.geometry("400x200")
    modal.attributes("-topmost", True)
    modal.grab_set()

    modal.configure(fg_color="#F4F5F7")
    hdr_a = ctk.CTkFrame(modal, fg_color="#1C2E45", height=50, corner_radius=0)
    hdr_a.pack(fill="x"); hdr_a.pack_propagate(False)
    ctk.CTkLabel(hdr_a, text="Vincular Processo", font=ctk.CTkFont(size=13, weight="bold"),
                 text_color="#FFFFFF").pack(pady=13)
    ctk.CTkLabel(modal, text="Adicionar Processo Associado",
                 font=ctk.CTkFont(weight="bold", size=13),
                 text_color="#1A1A2E").pack(pady=(16, 6))
    entry_assoc = ctk.CTkEntry(modal, width=320, placeholder_text="Digite o Nº do Processo (25 dígitos)...",
                                fg_color="#FFFFFF", border_color="#E0E3E8")
    entry_assoc.pack(pady=6)
    lbl_erro = ctk.CTkLabel(modal, text="", text_color="#B22222", font=ctk.CTkFont(size=11))
    lbl_erro.pack()

    def salvar_vinculo():
        acao_nova = entry_assoc.get().strip()
        if len(acao_nova) != 25:
            lbl_erro.configure(text="Formato inválido. O processo deve ter 25 caracteres.")
            return
        if acao_nova == acao_pai:
            lbl_erro.configure(text="Você não pode vincular o processo a ele mesmo.")
            return
        
        try:
            from database.database import buscar_processos_associados, sincronizar_associacoes
            assoc_pai = list(buscar_processos_associados(acao_pai))
            if acao_nova not in assoc_pai:
                assoc_pai.append(acao_nova)
                sincronizar_associacoes(acao_pai, assoc_pai)
                
            assoc_novo = list(buscar_processos_associados(acao_nova))
            if acao_pai not in assoc_novo:
                assoc_novo.append(acao_pai)
                sincronizar_associacoes(acao_nova, assoc_novo)
                
            app.notificacoes.append({"msg": "Processo vinculado com sucesso.", "cor": "info"})
            from modules import layout
            try: layout.atualizar_sino(app)
            except: pass
            
            atualizar_lista_processos(app)
            modal.destroy()
        except: pass

    ctk.CTkButton(modal, text="Vincular", fg_color="#1C2E45", hover_color="#253A56", text_color="#C9A84C", font=ctk.CTkFont(weight="bold"), width=160, height=36, corner_radius=8, command=salvar_vinculo).pack(pady=14)

def abrir_modal_gerenciar_associacoes_card(app, acao_pai):
    from database.database import buscar_processos, buscar_processos_associados, sincronizar_associacoes
    
    modal = ctk.CTkToplevel(app)
    modal.title("Gerenciar Associações")
    modal.geometry("500x400")
    modal.attributes("-topmost", True)
    modal.grab_set()

    ctk.CTkLabel(modal, text=f"Associar Processos a\n{acao_pai}", font=ctk.CTkFont(weight="bold", size=14)).pack(pady=(15, 10))

    scroll_assoc = ctk.CTkScrollableFrame(modal, fg_color="transparent")
    scroll_assoc.pack(fill="both", expand=True, padx=20, pady=5)

    try: processos_db = buscar_processos()
    except: processos_db = []
    
    try: assoc_atuais = list(buscar_processos_associados(acao_pai))
    except: assoc_atuais = []
    
    vars_check = {}
    for p in processos_db:
        p_acao = p[2]
        if p_acao == acao_pai: continue 
        
        var = ctk.StringVar(value=p_acao if p_acao in assoc_atuais else "")
        vars_check[p_acao] = var
        
        texto_chk = f"{p_acao} - {p[1]}"
        chk = ctk.CTkCheckBox(scroll_assoc, text=texto_chk, variable=var, onvalue=p_acao, offvalue="")
        chk.pack(anchor="w", pady=5)

    def salvar_assoc():
        novas_assoc = [v.get() for v in vars_check.values() if v.get()]
        try:
            sincronizar_associacoes(acao_pai, novas_assoc)
            app.notificacoes.append({"msg": "Associações atualizadas com sucesso.", "cor": "info"})
            from modules import layout
            try: layout.atualizar_sino(app)
            except: pass
            atualizar_lista_processos(app)
        except Exception as e:
            print(f"Erro ao salvar associações: {e}")
        modal.destroy()

    ctk.CTkButton(modal, text="Confirmar Associações", height=38, fg_color="#1C2E45", hover_color="#253A56", text_color="#C9A84C", font=ctk.CTkFont(weight="bold"), width=200, corner_radius=8, command=salvar_assoc).pack(pady=14)

def _ir_nova_strat_com_proc(app, num_acao):
    """Abre nova estratégia com processo já preenchido."""
    from modules import estrategias as _est_mod
    # Abre form vazio
    _est_mod.nova_estrategia(app)
    # Preenche o label do processo — usa lbl_proc_est diretamente
    def _set_proc():
        try:
            if hasattr(app, 'lbl_proc_est') and app.lbl_proc_est.winfo_exists():
                app.lbl_proc_est.configure(text=num_acao)
        except:
            pass
    app.after(200, _set_proc)


def atualizar_lista_processos(app, event=None):
    for aba in app.scrolls_processos.values():
        for widget in list(aba.winfo_children()):
            widget.destroy()

    def carregar_icone(caminho, tamanho=(16, 16)):
        try: return ctk.CTkImage(Image.open(f"assets/{caminho}"), size=tamanho)
        except: return None

    img_id, img_rg = carregar_icone("icon_id.png"), carregar_icone("icon_rg.png")
    img_tel, img_mail = carregar_icone("icon_tel.png"), carregar_icone("icon_mail.png")
    img_cnpj, img_resp = carregar_icone("icon_cnpj.png"), carregar_icone("icon_responsavel.png")
    img_razao, img_atuacao = carregar_icone("icon_razao.png", (14, 14)), carregar_icone("icon_atuacao.png", (14, 14))
    img_cliente_item = carregar_icone("icon_cliente_item.png", (16, 16))
    img_link = carregar_icone("icon_link.png", (18, 18))
    img_edit, img_del = carregar_icone("icon_edit.png", (14, 14)), carregar_icone("icon_delete.png", (14, 14))
    img_seta = carregar_icone("icon_seta.png", (12, 12))
    img_seta_cima = carregar_icone("icon_seta_cima.png", (12, 12)) 
    img_alerta_proc = carregar_icone("icon_notificacoes_alerta.png", (16, 16)) 
    img_clipe = carregar_icone("icon_clipe.png", (14, 14))

    termo = app.entry_busca_proc.get() if hasattr(app, 'entry_busca_proc') else ""
    if termo == "Buscar por Nome, CPF ou Nº do Processo...": termo = ""

    try: 
        processos = buscar_processos(termo)
    except: processos = []
    
    cache_clientes = {}

    def criar_card_proc(app, scroll_parent, p_dados):
        id_p, nome, acao, razao, atuacao, vara, tipo_v, pct, prov, conv, v_fixo, parc, parc_p, status_db, data, obs = p_dados
        
        cor_accent = "#1C2E45" 
        cli_obj = None
        
        from database.database import buscar_clientes
        
        if nome != "[Sem Cliente]":
            if nome not in cache_clientes:
                try: 
                    busca = buscar_clientes(nome)
                    exato = next((c for c in busca if str(c[2]).strip().lower() == str(nome).strip().lower()), busca[0] if busca else None)
                    cache_clientes[nome] = exato
                except: cache_clientes[nome] = None
            
            cli_obj = cache_clientes[nome]
            if cli_obj and cli_obj[1] == "Pessoa Jurídica": cor_accent = "#C9A84C" 
        else: cor_accent = "#d93838" 

        # AJUSTE DE HARMONIA: Cards com fundo mais claro (#2B2B31) para diferenciar do fundo geral
        card = ctk.CTkFrame(scroll_parent, corner_radius=10, height=65, fg_color="#FFFFFF", border_width=1, border_color="#E0E3E8")
        card.pack(fill="x", padx=15, pady=4)
        card.pack_propagate(False)

        ctk.CTkFrame(card, width=4, fg_color=cor_accent, corner_radius=0).pack(side="left", fill="y")
        
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(side="left", fill="both", expand=True, padx=12, pady=5)

        header = ctk.CTkFrame(content_frame, fg_color="transparent")
        header.pack(fill="x")

        try: 
            from database.database import buscar_processos_associados
            associados_db = buscar_processos_associados(acao)
        except: associados_db = []
        has_assoc = len(associados_db) > 0

        if nome != "[Sem Cliente]":
            ctk.CTkLabel(header, text=f"{acao}", font=ctk.CTkFont(size=13, weight="bold"), text_color=cor_accent).pack(side="left")
        else:
            ctk.CTkLabel(header, text=f" {acao}", image=img_alerta_proc, compound="left", font=ctk.CTkFont(size=13, weight="bold"), text_color=cor_accent).pack(side="left")

        if has_assoc:
            if img_clipe:
                ctk.CTkLabel(header, text="", image=img_clipe).pack(side="left", padx=(5, 0))
            else:
                ctk.CTkLabel(header, text="📎", font=ctk.CTkFont(size=14)).pack(side="left", padx=(5, 0))

        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side="right")

        # ── Verificar se existe estratégia vinculada a este processo ──────────
        id_estrat_vinc = None
        try:
            from database.database import conectar
            conn_st = conectar()
            cur_st  = conn_st.cursor()
            # Busca pelo num_acao diretamente no campo texto, não por subquery
            cur_st.execute(
                "SELECT e.id FROM estrategias e "
                "INNER JOIN processos p ON e.processo_id = p.id "
                "WHERE p.num_acao = ? LIMIT 1",
                (acao,)
            )
            row_st = cur_st.fetchone()
            conn_st.close()
            id_estrat_vinc = row_st[0] if row_st else None
        except Exception as _eq:
            id_estrat_vinc = None

        # Ícone estratégia dinâmico
        try:
            _img_est = ctk.CTkImage(Image.open(
                "assets/edit_strat.png" if id_estrat_vinc else "assets/criar_strat.png"
            ), size=(18, 18))
        except:
            _img_est = None

        def _acao_estrategia(id_e=id_estrat_vinc, num_a=acao):
            from modules import estrategias as _est_mod
            if id_e:
                # Navega para estratégias e abre a estratégia vinculada
                app.selecionar_aba("Estratégias")
                # Delay maior para garantir que a aba renderizou completamente
                app.after(200, lambda i=id_e: _est_mod.abrir_estrategia(app, i))
            else:
                # Navega para estratégias e abre form novo com processo preenchido
                app.selecionar_aba("Estratégias")
                app.after(200, lambda n=num_a: _ir_nova_strat_com_proc(app, n))

        # Seta de expandir — agora à ESQUERDA
        btn_exp = ctk.CTkButton(btn_frame, text="", image=img_seta, width=28, height=28,
                                 fg_color="transparent", hover_color=("gray80", "gray30"))
        btn_exp.pack(side="left", padx=5)

        # Ícone estratégia — segunda posição
        ctk.CTkButton(btn_frame, text="", image=_img_est, width=28, height=28,
                      fg_color="transparent", hover_color=("gray80", "gray30"),
                      command=_acao_estrategia).pack(side="left", padx=5)

        # Lápis (editar)
        ctk.CTkButton(btn_frame, text="", image=img_edit, width=28, height=28,
                      fg_color="transparent", hover_color=("gray80", "gray30"),
                      command=lambda pr=p_dados: abrir_opcoes_processo(app, pr)).pack(side="left", padx=5)

        # Excluir
        ctk.CTkButton(btn_frame, text="", image=img_del, width=28, height=28,
                      fg_color="transparent", text_color="#d93838",
                      hover_color=("gray80", "gray30"),
                      command=lambda i=id_p: confirmar_exclusao_processo(app, i)).pack(side="left", padx=5)

        info_row = ctk.CTkFrame(content_frame, fg_color="transparent")
        info_row.pack(fill="x")
        ctk.CTkLabel(info_row, text=f"  {razao}", image=img_razao, compound="left", font=ctk.CTkFont(size=11, weight="bold"), text_color="#1A1A2E").pack(side="left", padx=(0, 15))
        ctk.CTkLabel(info_row, text=f"  {atuacao}", image=img_atuacao, compound="left", font=ctk.CTkFont(size=11, weight="bold"), text_color="#1A1A2E").pack(side="left")

        frame_detalhes = ctk.CTkFrame(content_frame, fg_color="transparent")
        grid_detalhes = ctk.CTkFrame(frame_detalhes, fg_color="transparent")
        grid_detalhes.pack(fill="x", padx=(14, 10), pady=(10, 0))
        grid_detalhes.grid_columnconfigure((0, 2, 4), weight=1, uniform="colunas")
        grid_detalhes.grid_columnconfigure((1, 3), weight=0)

        col0 = ctk.CTkFrame(grid_detalhes, fg_color="transparent")
        col0.grid(row=0, column=0, sticky="n")
        ctk.CTkLabel(col0, text="VARA", font=ctk.CTkFont(size=10, weight="bold"), text_color=cor_accent).pack(anchor="center", pady=(0, 1))
        ctk.CTkLabel(col0, text=vara if vara else "Não informada", font=ctk.CTkFont(size=10)).pack(anchor="center")

        ctk.CTkFrame(grid_detalhes, width=2, height=1, fg_color=("gray80", "gray30")).grid(row=0, column=1, sticky="ns", pady=5)

        col2 = ctk.CTkFrame(grid_detalhes, fg_color="transparent")
        col2.grid(row=0, column=2, sticky="n")
        ctk.CTkLabel(col2, text="STATUS", font=ctk.CTkFont(size=10, weight="bold"), text_color=cor_accent).pack(anchor="center", pady=(0, 1))
        abas_do_processo = [s.strip() for s in status_db.split(",") if s.strip()]
        for st in abas_do_processo: 
            if st != "Todos": ctk.CTkLabel(col2, text=st, font=ctk.CTkFont(size=10)).pack(anchor="center")

        ctk.CTkFrame(grid_detalhes, width=2, height=1, fg_color=("gray80", "gray30")).grid(row=0, column=3, sticky="ns", pady=5)

        col4 = ctk.CTkFrame(grid_detalhes, fg_color="transparent")
        col4.grid(row=0, column=4, sticky="n")
        ctk.CTkLabel(col4, text="DADOS / VALORES", font=ctk.CTkFont(size=10, weight="bold"), text_color=cor_accent).pack(anchor="center", pady=(0, 1))
        
        if tipo_v == "Porcentagem":
            txts = [f"Honorários: {pct}%", f"Prov: R$ {prov:,.2f}", f"Conv: R$ {conv:,.2f}"] 
        elif tipo_v == "Fixo":
            txts = [f"Fixo: R$ {v_fixo:,.2f}", f"Parc: {parc_p}/{parc}"]
        else:
            txts = ["Pro Bono", "Sem Custos", ""]
        
        for t in txts: ctk.CTkLabel(col4, text=t, font=ctk.CTkFont(size=10)).pack(anchor="center")

        ctk.CTkFrame(frame_detalhes, height=2, fg_color=("gray80", "gray30")).pack(fill="x", pady=(20, 20))
        
        if obs:
            l_obs = ctk.CTkFrame(frame_detalhes, fg_color="transparent")
            l_obs.pack(fill="x", pady=(0, 15))
            ctk.CTkLabel(l_obs, text="Observações:", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
            ctk.CTkLabel(l_obs, text=obs, font=ctk.CTkFont(size=11)).pack(anchor="w", padx=5)

        if cli_obj:
            ctk.CTkLabel(frame_detalhes, text="CLIENTE ASSOCIADO", font=ctk.CTkFont(size=11, weight="bold"), text_color=("#1A1A1A", "#FFFFFF")).pack(anchor="w", pady=(0, 5))
            tipo_c, nome_c = cli_obj[1], cli_obj[2]
            
            c_item = ctk.CTkFrame(frame_detalhes, fg_color=("#E9ECEF", "#202024"), corner_radius=6, height=120)
            c_item.pack(fill="x", pady=(0, 15))
            c_item.pack_propagate(False) 
            ctk.CTkFrame(c_item, width=4, fg_color=cor_accent, corner_radius=0).pack(side="left", fill="y")
            
            c_grid = ctk.CTkFrame(c_item, fg_color="transparent")
            c_grid.pack(fill="both", expand=True, padx=10)
            c_grid.grid_columnconfigure((0, 2, 4), weight=1, uniform="colunas")
            c_grid.grid_columnconfigure((1, 3), weight=0)
            c_grid.grid_rowconfigure(0, weight=1)

            ctk.CTkLabel(c_grid, text=f" {nome_c}", image=img_cliente_item, compound="left", text_color=("#1A1A1A", "white"), font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, sticky="")
            
            ctk.CTkFrame(c_grid, width=1, height=1, fg_color=("gray80", "gray30")).grid(row=0, column=1, sticky="ns", pady=15)

            info_col = ctk.CTkFrame(c_grid, fg_color="transparent")
            info_col.grid(row=0, column=2, sticky="")
            if tipo_c == "Pessoa Jurídica":
                ctk.CTkLabel(info_col, text=f" {cli_obj[3]}", image=img_cnpj, compound="left", font=ctk.CTkFont(size=10)).pack(pady=2)
                ctk.CTkLabel(info_col, text=f" {cli_obj[13]}", image=img_resp, compound="left", font=ctk.CTkFont(size=10)).pack(pady=2)
            else:
                ctk.CTkLabel(info_col, text=f" {cli_obj[3]}", image=img_id, compound="left", font=ctk.CTkFont(size=10)).pack(pady=2)
                if cli_obj[4]: ctk.CTkLabel(info_col, text=f" {cli_obj[4]}", image=img_rg, compound="left", font=ctk.CTkFont(size=10)).pack(pady=2)
                ctk.CTkLabel(info_col, text=f" {cli_obj[5]}", image=img_tel, compound="left", font=ctk.CTkFont(size=10)).pack(pady=2)
                if cli_obj[6]: ctk.CTkLabel(info_col, text=f" {cli_obj[6]}", image=img_mail, compound="left", font=ctk.CTkFont(size=10)).pack(pady=2)

            ctk.CTkFrame(c_grid, width=1, height=1, fg_color=("gray80", "gray30")).grid(row=0, column=3, sticky="ns", pady=15)

            btn_f = ctk.CTkFrame(c_grid, fg_color="transparent")
            btn_f.grid(row=0, column=4, sticky="")
            ctk.CTkButton(btn_f, text="", image=img_link, width=32, height=32, fg_color="transparent", hover=False, command=lambda n=nome_c, t=tipo_c: redirecionar_para_cliente(app, n, t)).pack(anchor="center")

        assoc_header = ctk.CTkFrame(frame_detalhes, fg_color="transparent")
        assoc_header.pack(fill="x", pady=(5, 5))
        ctk.CTkLabel(assoc_header, text="PROCESSOS ASSOCIADOS", font=ctk.CTkFont(size=11, weight="bold"), text_color=("#1A1A1A", "#FFFFFF")).pack(side="left")
        
        ctk.CTkButton(assoc_header, text="", image=img_edit, width=28, height=28, fg_color="transparent", hover_color=("gray80", "gray30"), command=lambda p=acao: abrir_modal_gerenciar_associacoes_card(app, p)).pack(side="left", padx=10)
        
        try:
            from database.database import buscar_processos
            todos_processos_db = buscar_processos()
        except: todos_processos_db = []
        
        if not associados_db:
            ctk.CTkLabel(frame_detalhes, text="Nenhum processo associado.", font=ctk.CTkFont(size=10), text_color="gray").pack(anchor="w", padx=5)
        else:
            for a_acao in associados_db:
                razao_assoc = ""
                cor_associado = "#8A8A8A" # Cinza padrão caso falte algum dado

                try:
                    proc_assoc_dados = next((px for px in todos_processos_db if px[2] == a_acao), None)
                    if proc_assoc_dados:
                        razao_assoc = proc_assoc_dados[3]
                        nome_cliente_assoc = proc_assoc_dados[1] # Pega o nome do cliente dono deste processo
                        todos_clientes_db = buscar_clientes()
                        # Busca o cliente para saber se é Física ou Jurídica
                        cliente_assoc = next((cx for cx in todos_clientes_db if cx[2] == nome_cliente_assoc), None)
                        if cliente_assoc:
                            tipo_pessoa = cliente_assoc[1]
                            cor_associado = "#C9A84C" if tipo_pessoa == "Pessoa Jurídica" else "#1C2E45"
                except Exception:
                    pass

                a_row = ctk.CTkFrame(frame_detalhes, fg_color="#E9ECEF", corner_radius=6, height=32)
                a_row.pack(fill="x", pady=3)
                a_row.pack_propagate(False)

                # APLICANDO A COR DINÂMICA AQUI
                ctk.CTkFrame(a_row, width=4, fg_color=cor_associado, corner_radius=0).pack(side="left", fill="y") 
                
                a_grid = ctk.CTkFrame(a_row, fg_color="transparent")
                a_grid.pack(fill="both", expand=True, padx=10)
                
                a_grid.grid_columnconfigure((0, 2, 4), weight=1, uniform="colunas")
                a_grid.grid_columnconfigure((1, 3), weight=0)
                a_grid.grid_rowconfigure(0, weight=1)

                ctk.CTkLabel(a_grid, text=f" {a_acao}", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=0, sticky="")
                
                ctk.CTkFrame(a_grid, width=1, height=1, fg_color="transparent").grid(row=0, column=1, sticky="ns", pady=15)

                info_col_assoc = ctk.CTkFrame(a_grid, fg_color="transparent")
                info_col_assoc.grid(row=0, column=2, sticky="")
                if razao_assoc:
                    ctk.CTkLabel(info_col_assoc, text=f" {razao_assoc}", image=img_razao, compound="left", font=ctk.CTkFont(size=10)).pack(pady=2)

                ctk.CTkFrame(a_grid, width=1, height=1, fg_color="transparent").grid(row=0, column=3, sticky="ns", pady=15)

                btn_f_assoc = ctk.CTkFrame(a_grid, fg_color="transparent")
                btn_f_assoc.grid(row=0, column=4, sticky="") 
                ctk.CTkButton(btn_f_assoc, text="", image=img_link, width=32, height=32, fg_color="transparent", hover=False, command=lambda n=a_acao: redirecionar_para_processo_associado(app, n)).pack(anchor="center")

        def toggle(fd=frame_detalhes, c=card, b=btn_exp):
            if fd.winfo_ismapped(): 
                fd.pack_forget()
                c.configure(height=65)
                c.pack_propagate(False)
                b.configure(image=img_seta)
            else: 
                c.pack_propagate(True)
                fd.pack(fill="x", pady=(0, 10))
                if img_seta_cima: b.configure(image=img_seta_cima)

        btn_exp.configure(command=toggle)
        if hasattr(app, "processo_expandir_alvo") and app.processo_expandir_alvo == acao:
            app.after(50, toggle)
            app.processo_expandir_alvo = None

    renderizados = set()
    for p in processos:
        id_p = p[0]
        acao = p[2]
        abas_do_processo = [s.strip() for s in p[13].split(",") if s.strip()]
        
        if "Cancelado" in abas_do_processo:
            abas_do_processo = ["Cancelados"]
        else:
            if "Todos" not in abas_do_processo: abas_do_processo.insert(0, "Todos")
        
        for aba_nome in abas_do_processo:
            scroll_parent = app.scrolls_processos.get(aba_nome)
            if not scroll_parent: continue
            
            chave_render = f"{aba_nome}_{id_p}"
            if chave_render in renderizados: continue
            
            try:
                criar_card_proc(app, scroll_parent, p)
                renderizados.add(chave_render)
            except Exception as e:
                print(f"Erro ao renderizar card {id_p}: {e}")

def abrir_modal_configurar_valores(app, modal_pai, dados_proc, var_pago, var_naopago, var_cancelado, callback_salvar):
    id_p, nome, acao, razao, atuacao, vara, tipo_v, pct, prov, conv, v_fixo, parc, parc_p, status_atual, data, obs = dados_proc
    
    modal = ctk.CTkToplevel(modal_pai)
    modal.title("Configurar Valor")
    modal.geometry("460x440")
    modal.resizable(False, False)
    modal.attributes("-topmost", True)
    modal.grab_set()
    modal.configure(fg_color="#F4F5F7")

    # Cabeçalho navy
    hdr = ctk.CTkFrame(modal, fg_color="#1C2E45", height=50, corner_radius=0)
    hdr.pack(fill="x")
    hdr.pack_propagate(False)
    ctk.CTkLabel(hdr, text="Configurar Valor do Processo",
                 font=ctk.CTkFont(size=13, weight="bold"),
                 text_color="#FFFFFF").pack(pady=13)

    # Processo
    ctk.CTkLabel(modal, text=acao,
                 font=ctk.CTkFont(size=11), text_color="#7A8499").pack(pady=(10, 0))

    ctk.CTkLabel(modal,
                 text="Para marcar como Pago, informe os valores do processo.",
                 font=ctk.CTkFont(size=11), text_color="#7A8499").pack(pady=(2, 10))

    # Card de conteúdo
    card = ctk.CTkFrame(modal, fg_color="#FFFFFF", corner_radius=12,
                        border_width=1, border_color="#E0E3E8")
    card.pack(fill="x", padx=20, pady=(0, 10))

    var_tipo = ctk.StringVar(value="")
    frame_radios = ctk.CTkFrame(card, fg_color="transparent")
    frame_radios.pack(pady=(14, 8))
    
    frame_dinamico = ctk.CTkFrame(card, fg_color="transparent", height=140)
    frame_dinamico.pack(fill="x", padx=16, pady=(0, 10))
    frame_dinamico.pack_propagate(False)

    frame_pct = ctk.CTkFrame(frame_dinamico, fg_color="transparent")
    ctk.CTkLabel(frame_pct, text="% *", width=120, anchor="w", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=5)
    entry_pct = ctk.CTkEntry(frame_pct, width=180, placeholder_text="Ex: 10")
    entry_pct.grid(row=0, column=1, padx=10, pady=5)
    
    ctk.CTkLabel(frame_pct, text="Proveito (R$) *", width=120, anchor="w", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, padx=10, pady=5)
    entry_proveito = ctk.CTkEntry(frame_pct, width=180, placeholder_text="Ex: 5000")
    entry_proveito.grid(row=1, column=1, padx=10, pady=5)

    ctk.CTkLabel(frame_pct, text="Conversão *", width=120, anchor="w", font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, padx=10, pady=5)
    entry_conversao = ctk.CTkEntry(frame_pct, width=180, state="disabled", text_color="#1f9c46", font=ctk.CTkFont(weight="bold"))
    entry_conversao.grid(row=2, column=1, padx=10, pady=5)

    def calc_conv(e=None):
        try:
            p = float(entry_pct.get().replace(",", ".") or 0)
            pr = float(entry_proveito.get().replace(",", ".") or 0)
            c = pr * (p / 100)
            entry_conversao.configure(state="normal")
            entry_conversao.delete(0, "end")
            entry_conversao.insert(0, f"R$ {c:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            entry_conversao.configure(state="disabled")
        except:
            entry_conversao.configure(state="normal")
            entry_conversao.delete(0, "end")
            entry_conversao.configure(state="disabled")

    entry_pct.bind("<KeyRelease>", calc_conv)
    entry_proveito.bind("<KeyRelease>", calc_conv)

    frame_fixo = ctk.CTkFrame(frame_dinamico, fg_color="transparent")
    ctk.CTkLabel(frame_fixo, text="Valor Fixo (R$) *", width=140, anchor="w", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=5)
    entry_valor_fixo = ctk.CTkEntry(frame_fixo, width=160)
    entry_valor_fixo.grid(row=0, column=1, padx=10, pady=5)

    ctk.CTkLabel(frame_fixo, text="Qtd. Parcelas *", width=140, anchor="w", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, padx=10, pady=5)
    entry_parcelas = ctk.CTkEntry(frame_fixo, width=160)
    entry_parcelas.grid(row=1, column=1, padx=10, pady=5)

    ctk.CTkLabel(frame_fixo, text="Parcelas Pagas *", width=140, anchor="w", font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, padx=10, pady=5)
    entry_parcelas_adim = ctk.CTkEntry(frame_fixo, width=160)
    entry_parcelas_adim.grid(row=2, column=1, padx=10, pady=5)

    def alternar():
        frame_pct.pack_forget()
        frame_fixo.pack_forget()
        if var_tipo.get() == "Porcentagem":
            frame_pct.pack(fill="x", pady=10)
        elif var_tipo.get() == "Fixo":
            frame_fixo.pack(fill="x", pady=10)

    ctk.CTkRadioButton(frame_radios, text="%", variable=var_tipo, value="Porcentagem", font=ctk.CTkFont(weight="bold"), command=alternar).pack(side="left", padx=15)
    ctk.CTkRadioButton(frame_radios, text="Fixo", variable=var_tipo, value="Fixo", font=ctk.CTkFont(weight="bold"), command=alternar).pack(side="left", padx=15)
    ctk.CTkRadioButton(frame_radios, text="Pro Bono", variable=var_tipo, value="Pro Bono", font=ctk.CTkFont(weight="bold"), command=alternar).pack(side="left", padx=15)

    def salvar_valores_e_confirmar():
        tv = var_tipo.get()
        if not tv: return

        npct = nprov = nconv = nfixo = nparc = nparc_p = 0.0
        try:
            if tv == "Porcentagem":
                npct = float(entry_pct.get().replace(",", ".") or 0)
                nprov = float(entry_proveito.get().replace(",", ".") or 0)
                nconv = nprov * (npct / 100)
                if nconv <= 0: return
            elif tv == "Fixo":
                nfixo = float(entry_valor_fixo.get().replace(",", ".") or 0)
                nparc = int(entry_parcelas.get() or 0)
                nparc_p = int(entry_parcelas_adim.get() or 0)
                if nfixo <= 0: return
        except: return

        from database.database import atualizar_processo_completo
        atualizar_processo_completo(id_p, nome, acao, razao, atuacao, vara, tv, npct, nprov, nconv, nfixo, nparc, nparc_p, status_atual, obs)

        var_pago.set("Pagos")
        var_naopago.set("")
        var_cancelado.set("")
        
        modal.destroy()
        callback_salvar()

    ctk.CTkButton(modal, text="Salvar Valor e Marcar como Pago",
                   height=42, fg_color="#C9A84C", hover_color="#A8893C",
                   text_color="#1A1A2E", font=ctk.CTkFont(weight="bold", size=13),
                   corner_radius=8,
                   command=salvar_valores_e_confirmar).pack(pady=16, padx=20, fill="x")

def abrir_opcoes_processo(app, dados_proc):
    id_p, nome, acao, razao, atuacao, vara, tipo_v, pct, prov, conv, v_fixo, parc, parc_p, status_atual, data, obs = dados_proc

    modal = ctk.CTkToplevel(app)
    modal.title("Gerenciar Processo")
    modal.geometry("480x380")
    modal.resizable(False, False)
    modal.attributes("-topmost", True)
    modal.grab_set()
    modal.configure(fg_color="#F4F5F7")

    # Cabeçalho navy
    hdr = ctk.CTkFrame(modal, fg_color="#1C2E45", height=50, corner_radius=0)
    hdr.pack(fill="x")
    hdr.pack_propagate(False)
    ctk.CTkLabel(hdr, text="Gerenciar Abas de Exibição",
                 font=ctk.CTkFont(size=13, weight="bold"),
                 text_color="#FFFFFF").pack(pady=14)

    # Número do processo
    ctk.CTkLabel(modal, text=acao,
                 font=ctk.CTkFont(size=11),
                 text_color="#7A8499").pack(pady=(10, 0))

    # Card dos checkboxes
    card_chk = ctk.CTkFrame(modal, fg_color="#FFFFFF", corner_radius=12,
                             border_width=1, border_color="#E0E3E8")
    card_chk.pack(fill="x", padx=20, pady=(8, 0))

    frame_chk = ctk.CTkFrame(card_chk, fg_color="transparent")
    frame_chk.pack(pady=12, padx=12)
    
    status_list = [s.strip() for s in status_atual.split(",") if s.strip()]
    
    var_m_andamento = ctk.StringVar(value="Em Andamento" if "Em Andamento" in status_list else "")
    var_m_concluido = ctk.StringVar(value="Concluído" if "Concluído" in status_list else "")
    var_m_naopago = ctk.StringVar(value="Não Pagos" if "Não Pagos" in status_list else "")
    var_m_pago = ctk.StringVar(value="Pagos" if "Pagos" in status_list else "")
    var_m_certnao = ctk.StringVar(value="Certidão Não-Emitida" if "Certidão Não-Emitida" in status_list else "")
    var_m_certsim = ctk.StringVar(value="Certidão Emitida" if "Certidão Emitida" in status_list else "")
    var_m_cancelado = ctk.StringVar(value="Cancelado" if "Cancelado" in status_list else "")

    def salvar_modal():
        sts = [var_m_andamento.get(), var_m_concluido.get(), var_m_pago.get(), var_m_naopago.get(), var_m_certsim.get(), var_m_certnao.get(), var_m_cancelado.get()]
        st_final = ",".join([s for s in sts if s])
        
        if st_final:
            from database.database import buscar_processos, atualizar_status_processo, buscar_transacao_por_desc, adicionar_transacao, deletar_transacao
            proc_final = next((p for p in buscar_processos() if p[0] == id_p), dados_proc)
            tipo_v_final, conv_final, v_fixo_final = proc_final[6], proc_final[9], proc_final[10]

            if bool(var_m_pago.get()) and tipo_v_final != "Pro Bono":
                valido = False
                if tipo_v_final == "Porcentagem" and conv_final > 0: valido = True
                elif tipo_v_final == "Fixo" and v_fixo_final > 0: valido = True
                
                if not valido:
                    var_m_pago.set("")
                    app.notificacoes.append({"msg": "Não é possível salvar como 'Pago' com valores zerados.", "cor": "alerta"})
                    from modules import layout
                    try: layout.atualizar_sino(app)
                    except: pass
                    return

            atualizar_status_processo(id_p, st_final)
            desc_fin = f"| {acao}"
            transacao_existente = buscar_transacao_por_desc(desc_fin)

            if "Pagos" in sts and tipo_v_final != "Pro Bono" and not var_m_cancelado.get():
                if not transacao_existente:
                    valor_receita = conv_final if tipo_v_final == "Porcentagem" else v_fixo_final
                    adicionar_transacao(desc_fin, valor_receita, "Receita (+)", "")
            else:
                if transacao_existente:
                    deletar_transacao(transacao_existente[0])
                    app.notificacoes.append({"msg": f"Processo {acao} voltou para Não Pago (ou Cancelado) e foi removido do financeiro.", "cor": "info"})
                    from modules import layout
                    try: layout.atualizar_sino(app)
                    except: pass

            atualizar_lista_processos(app)
            try: modal.destroy() 
            except: pass

    def r_can():
        if var_m_cancelado.get():
            var_m_andamento.set("")
            var_m_concluido.set("")
            var_m_pago.set("")
            var_m_naopago.set("")
            var_m_certsim.set("")
            var_m_certnao.set("")
            
    def r_and(): 
        if var_m_andamento.get(): 
            var_m_concluido.set("")
            var_m_cancelado.set("")
    def r_con(): 
        if var_m_concluido.get(): 
            var_m_andamento.set("")
            var_m_cancelado.set("")

    def r_pag(): 
        if var_m_pago.get(): 
            from database.database import buscar_processos, buscar_transacao_por_desc
            proc_fresco = next((p for p in buscar_processos() if p[0] == id_p), dados_proc)
            t_v, c_v, v_f = proc_fresco[6], proc_fresco[9], proc_fresco[10]
            
            # Verificar se tem valor E se a transação financeira existe
            transacao_existe = buscar_transacao_por_desc(f"| {acao}") is not None

            tem_valor = False
            if t_v == "Porcentagem" and c_v > 0: tem_valor = True
            elif t_v == "Fixo" and v_f > 0: tem_valor = True
            elif t_v == "Pro Bono": tem_valor = True

            # Se deletou a transação financeira, pedir valores novamente
            if not tem_valor or not transacao_existe:
                var_m_pago.set("") 
                abrir_modal_configurar_valores(app, modal, proc_fresco, var_m_pago, var_m_naopago, var_m_cancelado, salvar_modal)
                return
                
            var_m_naopago.set("")
            var_m_cancelado.set("")

    def r_npa(): 
        if var_m_naopago.get(): 
            var_m_pago.set("")
            var_m_cancelado.set("")
    def r_csm(): 
        if var_m_certsim.get(): 
            var_m_certnao.set("")
            var_m_cancelado.set("")
    def r_cna(): 
        if var_m_certnao.get(): 
            var_m_certsim.set("")
            var_m_cancelado.set("")

    ctk.CTkCheckBox(frame_chk, text="Em Andamento", font=ctk.CTkFont(weight="bold"), variable=var_m_andamento, onvalue="Em Andamento", offvalue="", command=r_and).grid(row=0, column=0, padx=10, pady=5, sticky="w")
    ctk.CTkCheckBox(frame_chk, text="Concluído", font=ctk.CTkFont(weight="bold"), variable=var_m_concluido, onvalue="Concluído", offvalue="", command=r_con).grid(row=1, column=0, padx=10, pady=5, sticky="w")
    
    ctk.CTkCheckBox(frame_chk, text="Não Pagos", font=ctk.CTkFont(weight="bold"), variable=var_m_naopago, onvalue="Não Pagos", offvalue="", command=r_npa).grid(row=0, column=1, padx=10, pady=5, sticky="w")
    ctk.CTkCheckBox(frame_chk, text="Pagos", font=ctk.CTkFont(weight="bold"), variable=var_m_pago, onvalue="Pagos", offvalue="", command=r_pag).grid(row=1, column=1, padx=10, pady=5, sticky="w")
    
    ctk.CTkCheckBox(frame_chk, text="Cert. Não-Emitida", font=ctk.CTkFont(weight="bold"), variable=var_m_certnao, onvalue="Certidão Não-Emitida", offvalue="", command=r_cna).grid(row=0, column=2, padx=10, pady=5, sticky="w")
    ctk.CTkCheckBox(frame_chk, text="Cert. Emitida", font=ctk.CTkFont(weight="bold"), variable=var_m_certsim, onvalue="Certidão Emitida", offvalue="", command=r_csm).grid(row=1, column=2, padx=10, pady=5, sticky="w")
    
    ctk.CTkCheckBox(frame_chk, text="Cancelado", font=ctk.CTkFont(weight="bold"), variable=var_m_cancelado, onvalue="Cancelado", offvalue="", command=r_can, text_color="#d93838").grid(row=2, column=0, padx=10, pady=5, sticky="w")
    
    ctk.CTkButton(frame_chk, text="Salvar Checklists",
                   font=ctk.CTkFont(weight="bold"),
                   fg_color="#1C2E45", hover_color="#253A56",
                   text_color="#C9A84C", height=36, corner_radius=8,
                   width=160, command=salvar_modal
                   ).grid(row=3, column=0, columnspan=3, pady=(16, 4))

    ctk.CTkFrame(modal, height=1, fg_color="#E0E3E8", corner_radius=0).pack(fill="x", padx=20, pady=(10, 6))

    def ir_para_editar():
        modal.destroy()
        app.id_edicao_proc = id_p
        app.chk_cancelado.grid() 
        
        try:
            from database.database import buscar_processos_associados
            app.processos_associados_temporarios = buscar_processos_associados(acao)
        except: app.processos_associados_temporarios = []
        atualizar_lista_assoc_form(app)
        
        app.var_st_andamento.set("Em Andamento" if "Em Andamento" in status_list else "")
        app.var_st_concluido.set("Concluído" if "Concluído" in status_list else "")
        app.var_st_pago.set("Pagos" if "Pagos" in status_list else "")
        app.var_st_naopago.set("Não Pagos" if "Não Pagos" in status_list else "")
        app.var_st_certsim.set("Certidão Emitida" if "Certidão Emitida" in status_list else "")
        app.var_st_certnao.set("Certidão Não-Emitida" if "Certidão Não-Emitida" in status_list else "")
        app.var_st_cancelado.set("Cancelado" if "Cancelado" in status_list else "")

        app.entradas_proc["Nome do Contratante: *"].configure(state="normal")
        app.entradas_proc["Nome do Contratante: *"].delete(0, 'end')
        app.entradas_proc["Nome do Contratante: *"].insert(0, nome)
        app.entradas_proc["Nome do Contratante: *"].configure(state="disabled")
        
        app.entradas_proc["N° da Ação (CNJ): *"].delete(0, 'end')
        app.entradas_proc["N° da Ação (CNJ): *"].insert(0, acao)
        app.entradas_proc["Razão do Contrato: *"].delete(0, 'end')
        app.entradas_proc["Razão do Contrato: *"].insert(0, razao)
        app.entradas_proc["Atuação: *"].delete(0, 'end')
        app.entradas_proc["Atuação: *"].insert(0, atuacao)
        
        app.entradas_proc["Vara: "].delete(0, 'end')
        if vara: app.entradas_proc["Vara: "].insert(0, vara)

        app.txt_obs_proc.delete("0.0", "end")
        app.txt_obs_proc.insert("0.0", obs if obs else "")

        app.var_tipo_valor.set(tipo_v)
        alternar_campos_valor_proc(app)

        if tipo_v == "Porcentagem":
            app.entry_pct.delete(0, 'end')
            app.entry_pct.insert(0, str(pct))
            app.entry_proveito.delete(0, 'end')
            app.entry_proveito.insert(0, str(prov))
            calcular_conversao(app)
        elif tipo_v == "Fixo":
            app.entry_valor_fixo.delete(0, 'end')
            app.entry_valor_fixo.insert(0, str(v_fixo))
            app.entry_parcelas.delete(0, 'end')
            app.entry_parcelas.insert(0, str(parc))
            app.entry_parcelas_adim.delete(0, 'end')
            app.entry_parcelas_adim.insert(0, str(parc_p))
        else: 
            app.entry_pct.delete(0, 'end')
            app.entry_proveito.delete(0, 'end')
            app.entry_valor_fixo.delete(0, 'end')
            app.entry_parcelas.delete(0, 'end')
            app.entry_parcelas_adim.delete(0, 'end')

        app.frame_lista_processos.grid_forget()
        app.frame_form_processo.grid(row=0, column=0, sticky="nsew")

    ctk.CTkButton(modal,
                   text="Editar Todas as Informações",
                   text_color="#C9A84C", fg_color="#1C2E45",
                   hover_color="#253A56",
                   font=ctk.CTkFont(weight="bold"),
                   height=40, corner_radius=8,
                   command=ir_para_editar).pack(pady=(4, 16), padx=20, fill="x")

def confirmar_exclusao_processo(app, id_processo):
    modal = ctk.CTkToplevel(app)
    modal.title("Excluir Processo")
    modal.geometry("400x210")
    modal.attributes("-topmost", True)
    modal.grab_set()
    modal.configure(fg_color="#F4F5F7")

    hdr = ctk.CTkFrame(modal, fg_color="#1C2E45", height=50, corner_radius=0)
    hdr.pack(fill="x")
    hdr.pack_propagate(False)
    ctk.CTkLabel(hdr, text="Excluir Processo",
                 font=ctk.CTkFont(size=13, weight="bold"),
                 text_color="#FFFFFF").pack(pady=13)

    ctk.CTkLabel(modal, text="Tem certeza que deseja excluir este processo?",
                 font=ctk.CTkFont(size=13, weight="bold"),
                 text_color="#1A1A2E").pack(pady=(20, 4))
    ctk.CTkLabel(modal, text="Esta ação removerá também os vínculos e lançamentos financeiros.",
                 font=ctk.CTkFont(size=11), text_color="#7A8499",
                 wraplength=340).pack()

    frame_btn = ctk.CTkFrame(modal, fg_color="transparent")
    frame_btn.pack(pady=20)

    def sim():
        modal.destroy()
        app.after(50, lambda: remover_processo(app, id_processo))

    ctk.CTkButton(frame_btn, text="Excluir", fg_color="#B22222", hover_color="#8B1A1A",
                  text_color="white", width=120, height=36, corner_radius=8,
                  font=ctk.CTkFont(weight="bold"), command=sim).pack(side="left", padx=8)
    ctk.CTkButton(frame_btn, text="Cancelar", fg_color="#F4F5F7", hover_color="#E0E3E8",
                  text_color="#1A1A2E", border_width=1, border_color="#E0E3E8",
                  width=120, height=36, corner_radius=8,
                  font=ctk.CTkFont(weight="bold"), command=modal.destroy).pack(side="left", padx=8)

def remover_processo(app, id_processo):
    try:
        from database.database import (
            buscar_processos, deletar_processo, buscar_transacao_por_desc,
            deletar_transacao, buscar_processos_associados, sincronizar_associacoes
        )

        processos_bd = buscar_processos()
        proc_info = next((p for p in processos_bd if p[0] == id_processo), None)
        
        if proc_info:
            num_acao = proc_info[2]
            
            try:
                desc_fin = f"| {num_acao}"
                transacao_existente = buscar_transacao_por_desc(desc_fin)
                if transacao_existente:
                    deletar_transacao(transacao_existente[0])
            except Exception: pass

            try:
                for p in processos_bd:
                    outra_acao = p[2]
                    if outra_acao != num_acao:
                        assocs_deste = list(buscar_processos_associados(outra_acao))
                        if num_acao in assocs_deste:
                            assocs_deste.remove(num_acao)
                            sincronizar_associacoes(outra_acao, assocs_deste)

                sincronizar_associacoes(num_acao, [])
            except Exception as e:
                print(f"Erro ao limpar associações cruzadas: {e}")

            from modules import layout
            app.notificacoes.append({"msg": f"Processo '{num_acao}' foi excluído definitivamente.", "cor": "alerta"})
            layout.atualizar_sino(app)

        deletar_processo(id_processo)
        app.after(100, lambda: atualizar_lista_processos(app))
        
    except Exception as e:
        print(f"Erro em remover_processo: {e}")

def abrir_seletor_processos(app, acao_mestre=None):
    modal = ctk.CTkToplevel(app)
    modal.title("Vincular Processos")
    modal.geometry("500x550")
    modal.attributes("-topmost", True)
    modal.grab_set()

    modal.configure(fg_color="#F4F5F7")
    hdr_s = ctk.CTkFrame(modal, fg_color="#1C2E45", height=50, corner_radius=0)
    hdr_s.pack(fill="x"); hdr_s.pack_propagate(False)
    ctk.CTkLabel(hdr_s, text="Gerenciar Associacoes", font=ctk.CTkFont(size=13, weight="bold"),
                 text_color="#FFFFFF").pack(pady=13)
    entry_busca = ctk.CTkEntry(modal, placeholder_text="Pesquisar por numero...",
                                width=460, height=36, fg_color="#FFFFFF", border_color="#E0E3E8")
    entry_busca.pack(pady=(14, 6))
    scroll_procs = ctk.CTkScrollableFrame(modal, fg_color="transparent")
    scroll_procs.pack(expand=True, fill="both", padx=16, pady=4)

    if acao_mestre:
        try:
            from database.database import buscar_processos_associados
            temp_assocs = buscar_processos_associados(acao_mestre)
        except: temp_assocs = []
    else:
        temp_assocs = list(app.processos_associados_temporarios)

    def carregar_lista(event=None):
        for w in scroll_procs.winfo_children(): w.destroy()
        termo = entry_busca.get().strip()
        
        try:
            todos_procs = buscar_processos(termo)
        except: todos_procs = []

        for p in todos_procs:
            acao_p = p[2]
            
            if acao_mestre and acao_p == acao_mestre: continue
            if not acao_mestre and hasattr(app, "entradas_proc"):
                acao_atual = app.entradas_proc["N° da Ação (CNJ): *"].get()
                if acao_p == acao_atual: continue

            row = ctk.CTkFrame(scroll_procs, fg_color="#FFFFFF", corner_radius=8, border_width=1, border_color="#E0E3E8")
            row.pack(fill="x", pady=2)
            
            ctk.CTkLabel(row, text=acao_p, font=ctk.CTkFont(weight="bold"), text_color="#1A1A2E").pack(side="left", padx=15, pady=10)
            
            is_vinculado = acao_p in temp_assocs

            def toggle_vinculo(num=acao_p):
                if num in temp_assocs:
                    temp_assocs.remove(num)
                else:
                    temp_assocs.append(num)
                carregar_lista() 

            if is_vinculado:
                ctk.CTkButton(row, text="Remover", width=90, height=30, fg_color="#B22222", hover_color="#8B1A1A", text_color="white", corner_radius=6, font=ctk.CTkFont(weight="bold", size=11), command=toggle_vinculo).pack(side="right", padx=10, pady=6)
            else:
                ctk.CTkButton(row, text="Adicionar", width=90, height=30, fg_color="#1C2E45", hover_color="#253A56", text_color="#C9A84C", corner_radius=6, font=ctk.CTkFont(weight="bold", size=11), command=toggle_vinculo).pack(side="right", padx=10, pady=6)

    def confirmar_vinculacoes():
        if acao_mestre:
            try:
                from database.database import sincronizar_associacoes
                sincronizar_associacoes(acao_mestre, temp_assocs)
                atualizar_lista_processos(app) 
            except: pass
        else:
            app.processos_associados_temporarios = temp_assocs
            atualizar_lista_assoc_form(app)
        modal.destroy()

    entry_busca.bind("<KeyRelease>", carregar_lista)
    carregar_lista()
    
    ctk.CTkButton(modal, text="Confirmar Vinculacoes", font=ctk.CTkFont(weight="bold"), height=40, fg_color="#1C2E45", hover_color="#253A56", text_color="#C9A84C", corner_radius=8, command=confirmar_vinculacoes).pack(fill="x", padx=20, pady=14)

def redirecionar_para_processo_associado(app, acao_alvo):
    for widget in app.winfo_children():
        if isinstance(widget, ctk.CTkToplevel):
            widget.destroy()

    app.tabs_processos.set("Todos")
    
    app.redirecionado_proc = True
    atualizar_cores_abas_processos(app)

    if hasattr(app, 'entry_busca_proc'):
        app.entry_busca_proc.delete(0, 'end')
        app.entry_busca_proc.insert(0, acao_alvo)
        app.entry_busca_proc.configure(text_color=("black", "white"))

    app.processo_expandir_alvo = acao_alvo
    atualizar_lista_processos(app)