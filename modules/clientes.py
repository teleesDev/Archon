import customtkinter as ctk
from database.database import (
    adicionar_cliente, atualizar_cliente_completo, buscar_clientes, 
    buscar_processos, deletar_cliente, obter_nome_cliente_por_id, 
    sincronizar_nome_processos
)
from modules.utils import formatar_telefone, formatar_cpf, formatar_rg, formatar_cnpj
from modules import layout, processos
from PIL import Image

def atualizar_cores_abas_clientes(app):
    if not hasattr(app, 'botoes_abas_clientes'):
        return

    aba_atual = app.tabs_pf_pj.get()
    
    for nome, btn in app.botoes_abas_clientes.items():
        if nome == aba_atual:
            btn.configure(fg_color="#1C2E45", text_color="#C9A84C")
        else:
            btn.configure(fg_color="transparent", text_color="#1A1A2E")

def redirecionar_para_processo(app, numero_processo):
    try:
        if hasattr(app, 'frame_form_processo') and hasattr(app, 'frame_lista_processos'):
            app.frame_form_processo.grid_forget()
            app.frame_lista_processos.grid(row=0, column=0, sticky="nsew")

        if hasattr(app, 'selecionar_aba'):
            app.selecionar_aba("Meus Processos")
        
        # Flag de redirecionamento para limpar busca ao trocar de aba lá em processos
        app.redirecionado_proc = True
        
        if hasattr(app, 'entry_busca_proc'):
            app.entry_busca_proc.delete(0, 'end')
            app.entry_busca_proc.insert(0, "Buscar por Nome, CPF ou Nº do Processo...")
            app.entry_busca_proc.configure(text_color="gray")
            
        app.processo_expandir_alvo = numero_processo
        
        if hasattr(processos, 'atualizar_lista_processos'):
            processos.atualizar_lista_processos(app)

        if hasattr(app, 'entry_busca_cliente'):
            app.entry_busca_cliente.delete(0, 'end')
            app.entry_busca_cliente.insert(0, "Buscar por Nome, CPF ou CNPJ...")
            app.entry_busca_cliente.configure(text_color="gray")

    except Exception as e:
        print(f"Erro ao redirecionar: {e}")

def criar_aba_clientes(app, parent_frame):
    parent_frame.grid_rowconfigure(0, weight=1)
    parent_frame.grid_columnconfigure(0, weight=1)

    app.frame_lista_clientes = ctk.CTkFrame(parent_frame, fg_color="#F4F5F7")
    app.frame_lista_clientes.grid(row=0, column=0, sticky="nsew")
    app.frame_lista_clientes.grid_rowconfigure(1, weight=0) 
    app.frame_lista_clientes.grid_rowconfigure(2, weight=1) 
    app.frame_lista_clientes.grid_columnconfigure(0, weight=1)

    topo_frame = ctk.CTkFrame(app.frame_lista_clientes, fg_color="transparent")
    topo_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))

    def on_focus_in(event, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, "end")
            entry.configure(text_color=("black", "white"))

    def on_focus_out(event, entry, placeholder):
        if entry.get() == "":
            entry.insert(0, placeholder)
            entry.configure(text_color="gray")

    app.entry_busca_cliente = ctk.CTkEntry(topo_frame, height=35, border_width=1, border_color=("#E0E3E8", "gray30"))
    app.entry_busca_cliente.insert(0, "Buscar por Nome, CPF ou CNPJ...")
    app.entry_busca_cliente.configure(text_color="gray")
    
    app.entry_busca_cliente.pack(side="left", fill="x", expand=True, padx=(0, 20))
    app.entry_busca_cliente.bind("<FocusIn>", lambda e: on_focus_in(e, app.entry_busca_cliente, "Buscar por Nome, CPF ou CNPJ..."))
    app.entry_busca_cliente.bind("<FocusOut>", lambda e: on_focus_out(e, app.entry_busca_cliente, "Buscar por Nome, CPF ou CNPJ..."))
    app.entry_busca_cliente.bind("<KeyRelease>", lambda e: atualizar_lista_clientes(app, e)) 
    
    def ir_para_novo_cliente_aba():
        mostrar_form_cliente(app)
        if hasattr(app, "tabs_pf_pj") and app.tabs_pf_pj.get() == "Pessoa Jurídica":
            app.var_tipo_pessoa.set("Pessoa Jurídica")
        else:
            app.var_tipo_pessoa.set("Pessoa Física")
        alternar_campos_pj(app)
        
    btn_novo_cliente = ctk.CTkButton(topo_frame, text="+ Cadastrar Novo", width=150, height=35,
                                     font=ctk.CTkFont(weight="bold"),
                                     fg_color="#1C2E45", hover_color="#253A56", text_color="#FFFFFF",
                                     border_width=1, border_color=("#8A8A8A", "#5A5A5A"),
                                     command=ir_para_novo_cliente_aba)
    btn_novo_cliente.pack(side="right")

    header_customizado = ctk.CTkFrame(app.frame_lista_clientes, fg_color="transparent")
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

    app.tabs_pf_pj = ctk.CTkTabview(app.frame_lista_clientes, bg_color=["#FFFFFF", "#1E1E1E"], fg_color="transparent", corner_radius=15)
    app.tabs_pf_pj.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20)) 
    
    app.botoes_abas_clientes = {}

    def alterar_aba_customizada_cli(a):
        app.tabs_pf_pj.set(a)
        
        if hasattr(app, 'redirecionado_cli') and app.redirecionado_cli:
            app.entry_busca_cliente.delete(0, 'end')
            app.entry_busca_cliente.insert(0, "Buscar por Nome, CPF ou CNPJ...")
            app.entry_busca_cliente.configure(text_color="gray")
            app.redirecionado_cli = False
            
        atualizar_cores_abas_clientes(app)
        atualizar_lista_clientes(app)

    abas_clientes = ["Todos", "Pessoa Física", "Pessoa Jurídica"]

    for aba in abas_clientes:
        bloco = ctk.CTkFrame(header_customizado, fg_color=("#E0E3E8", "gray15"), corner_radius=6)
        bloco.pack(side="left", padx=8)

        app.tabs_pf_pj.add(aba)

        btn = ctk.CTkButton(
            bloco, text=aba, height=26, corner_radius=5,
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=12, weight="bold"),
            fg_color="transparent", hover_color="#D8DCE5",
            command=lambda a=aba: alterar_aba_customizada_cli(a)
        )
        btn.pack(side="left", padx=2, pady=2)
        app.botoes_abas_clientes[aba] = btn

    app.scroll_todos = ctk.CTkScrollableFrame(app.tabs_pf_pj.tab("Todos"), corner_radius=15, fg_color="transparent")
    app.scroll_todos.pack(expand=True, fill="both")

    app.scroll_pf = ctk.CTkScrollableFrame(app.tabs_pf_pj.tab("Pessoa Física"), corner_radius=15, fg_color="transparent")
    app.scroll_pf.pack(expand=True, fill="both")
    
    app.scroll_pj = ctk.CTkScrollableFrame(app.tabs_pf_pj.tab("Pessoa Jurídica"), corner_radius=15, fg_color="transparent")
    app.scroll_pj.pack(expand=True, fill="both")

    app.tabs_pf_pj._segmented_button.grid_forget()
    app.tabs_pf_pj._segmented_button.configure(height=0)
    app.tabs_pf_pj._segmented_button.grid = lambda *args, **kwargs: None

    atualizar_cores_abas_clientes(app)

    app.frame_form_cliente = ctk.CTkFrame(parent_frame, fg_color="#F4F5F7")
    app.frame_form_cliente.grid_rowconfigure(0, weight=1)
    app.frame_form_cliente.grid_columnconfigure(0, weight=1)

    scroll_form_box = ctk.CTkScrollableFrame(app.frame_form_cliente, fg_color="#F4F5F7")
    scroll_form_box.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    scroll_form_box.grid_columnconfigure(0, weight=1)

    app.form_box = ctk.CTkFrame(scroll_form_box, corner_radius=15, width=600)
    app.form_box.grid(row=0, column=0, pady=10, sticky="n")
    app.form_box.grid_columnconfigure(1, weight=1)

    # Botão voltar (Topo Esquerdo - Coluna 0)
    try:
        img_voltar = ctk.CTkImage(Image.open("assets/icone_voltar.png"), size=(20, 20))
    except Exception:
        img_voltar = None

    btn_voltar = ctk.CTkButton(app.form_box, text="←" if not img_voltar else "", image=img_voltar, width=30, height=30, 
                               fg_color="transparent", hover_color="#E0E3E8", text_color="#1A1A2E",
                               command=lambda: mostrar_lista_clientes(app))
    btn_voltar.grid(row=0, column=0, sticky="nw", padx=20, pady=(20, 10)) 

    # Título (Coluna 1)
    frame_titulo = ctk.CTkFrame(app.form_box, fg_color="transparent")
    # A MÁGICA AQUI: padx=(0, 50) joga ele um pouquinho para a esquerda! Ajuste esse 50 para mais ou menos se quiser.
    frame_titulo.grid(row=0, column=1, pady=(20, 10), sticky="", padx=(0, 50))

    try:
        img_form = ctk.CTkImage(Image.open("assets/icone_formulario.png"), size=(24, 24))
    except Exception:
        img_form = None
    
    if img_form: ctk.CTkLabel(frame_titulo, text="", image=img_form).pack(side="left", padx=(15, 10))
    ctk.CTkLabel(frame_titulo, text="Registro de Cliente", font=ctk.CTkFont(size=22, weight="bold"), text_color="#1A1A2E").pack(side="left")
    if img_form: ctk.CTkLabel(frame_titulo, text="", image=img_form).pack(side="left", padx=(10, 0))

    # Radios (Física/Jurídica - Coluna 1)
    app.var_tipo_pessoa = ctk.StringVar(value="Pessoa Física")
    frame_radios = ctk.CTkFrame(app.form_box, fg_color="transparent")
    
    # O mesmo padx=(0, 50) para ele seguir o alinhamento do título acima!
    frame_radios.grid(row=1, column=1, pady=(0, 30), sticky="", padx=(0, 50)) 
    
    ctk.CTkRadioButton(frame_radios, text="Pessoa Física", font=ctk.CTkFont(weight="bold"), text_color="#1A1A2E", variable=app.var_tipo_pessoa, value="Pessoa Física", command=lambda: alternar_campos_pj(app)).pack(side="left", padx=(40, 15), pady=(40, 0))
    ctk.CTkRadioButton(frame_radios, text="Pessoa Jurídica", font=ctk.CTkFont(weight="bold"), text_color="#1A1A2E", variable=app.var_tipo_pessoa, value="Pessoa Jurídica", command=lambda: alternar_campos_pj(app)).pack(side="left", padx=15, pady=(40, 0))

    app.entradas_cli = {}
    app.lbls_cli = {}

    campos_pf = [("Nome Completo: *", 2), ("CPF:", 3), ("RG:", 4), ("Telefone: *", 5), ("E-mail:", 6), ("Profissão:", 7), ("Estado Civil:", 8), ("Naturalidade:", 9), ("Endereço:", 10)]
    for texto, linha in campos_pf:
        # AJUSTE: Removido o bloqueio da cor preta para campos obrigatórios (*)
        lbl = ctk.CTkLabel(app.form_box, text=texto, text_color=("black", "white"), font=ctk.CTkFont(weight="bold"))
        lbl.grid(row=linha, column=0, padx=20, pady=7, sticky="w")
        ent = ctk.CTkEntry(app.form_box, width=350)
        ent.grid(row=linha, column=1, padx=(0, 20), pady=7, sticky="ew")
        app.lbls_cli[texto] = lbl
        app.entradas_cli[texto] = ent

    campos_pj = [("Razão Social: *", 2), ("CNPJ: *", 3), ("Estado:", 4), ("Responsável:", 6)]
    for texto, linha in campos_pj:
        # AJUSTE: Removido o bloqueio da cor preta
        lbl = ctk.CTkLabel(app.form_box, text=texto, text_color=("black", "white"), font=ctk.CTkFont(weight="bold"))
        lbl.grid(row=linha, column=0, padx=20, pady=7, sticky="w")
        ent = ctk.CTkEntry(app.form_box, width=350)
        ent.grid(row=linha, column=1, padx=(0, 20), pady=7, sticky="ew")
        app.lbls_cli[texto] = lbl
        app.entradas_cli[texto] = ent

    app.var_unidade_pj = ctk.StringVar(value="Matriz")
    app.frame_unidade_pj = ctk.CTkFrame(app.form_box, fg_color="transparent")
    ctk.CTkRadioButton(app.frame_unidade_pj, text="Matriz", font=ctk.CTkFont(weight="bold"), variable=app.var_unidade_pj, value="Matriz").pack(side="left", padx=(60, 10))
    ctk.CTkRadioButton(app.frame_unidade_pj, text="Filial", font=ctk.CTkFont(weight="bold"), variable=app.var_unidade_pj, value="Filial").pack(side="left", padx=(10, 0))
    # AJUSTE: Text Color adicionado
    app.lbl_unidade_pj = ctk.CTkLabel(app.form_box, text="Tipo de Unidade:", text_color=("black", "white"), font=ctk.CTkFont(weight="bold"))

    ent_tel = app.entradas_cli["Telefone: *"]
    ent_tel.bind("<KeyRelease>", lambda e: formatar_telefone(ent_tel, e))
    ent_cpf = app.entradas_cli["CPF:"]
    ent_cpf.bind("<KeyRelease>", lambda e: formatar_cpf(ent_cpf, e))
    ent_cnpj = app.entradas_cli["CNPJ: *"]
    ent_cnpj.bind("<KeyRelease>", lambda e: formatar_cnpj(ent_cnpj, e))
    ent_rg = app.entradas_cli["RG:"]
    ent_rg.bind("<KeyRelease>", lambda e: formatar_rg(ent_rg, e))

    # AJUSTE: Text Color adicionado
    ctk.CTkLabel(app.form_box, text="Observações:", text_color=("black", "white"), font=ctk.CTkFont(weight="bold")).grid(row=11, column=0, padx=20, pady=7, sticky="nw")
    app.txt_obs_cli = ctk.CTkTextbox(app.form_box, width=350, height=60)
    app.txt_obs_cli.grid(row=11, column=1, padx=(0, 20), pady=7, sticky="ew")

    app.btn_salvar_cliente = ctk.CTkButton(app.form_box, text="Salvar Cliente", font=ctk.CTkFont(weight="bold"), 
                                           fg_color="#C9A84C", hover_color="#A8893C", text_color="#1A1A2E", 
                                           command=lambda: salvar_cliente(app))
    app.btn_salvar_cliente.grid(row=12, column=0, columnspan=2, pady=(20, 20), padx=20, sticky="ew")

    mostrar_lista_clientes(app)

def alternar_campos_pj(app):
    for lbl in app.lbls_cli.values(): lbl.grid_forget()
    for ent in app.entradas_cli.values(): ent.grid_forget()
    app.lbl_unidade_pj.grid_forget()
    app.frame_unidade_pj.grid_forget()

    if app.var_tipo_pessoa.get() == "Pessoa Física":
        campos_pf = ["Nome Completo: *", "CPF:", "RG:", "Telefone: *", "E-mail:", "Profissão:", "Estado Civil:", "Naturalidade:", "Endereço:"]
        linhas = {"Nome Completo: *": 2, "CPF:": 3, "RG:": 4, "Telefone: *": 5, "E-mail:": 6, "Profissão:": 7, "Estado Civil:": 8, "Naturalidade:": 9, "Endereço:": 10}
        for texto in campos_pf:
            app.lbls_cli[texto].grid(row=linhas[texto], column=0, padx=20, pady=7, sticky="w")
            app.entradas_cli[texto].grid(row=linhas[texto], column=1, padx=(0, 20), pady=7, sticky="ew")
    else:
        campos_pj = ["Razão Social: *", "CNPJ: *", "Estado:", "Responsável:"]
        linhas = {"Razão Social: *": 2, "CNPJ: *": 3, "Estado:": 4, "Responsável:": 6}
        for texto in campos_pj:
            app.lbls_cli[texto].grid(row=linhas[texto], column=0, padx=20, pady=7, sticky="w")
            app.entradas_cli[texto].grid(row=linhas[texto], column=1, padx=(0, 20), pady=7, sticky="ew")
        
        app.lbl_unidade_pj.grid(row=5, column=0, padx=20, pady=7, sticky="w")
        app.frame_unidade_pj.grid(row=5, column=1, padx=(0, 20), pady=7, sticky="w")

    app.form_box.update_idletasks()

def mostrar_form_cliente(app):
    app.id_edicao_cli = None
    for ent in app.entradas_cli.values(): ent.delete(0, 'end')
    app.txt_obs_cli.delete("0.0", "end")
    app.frame_lista_clientes.grid_forget()
    app.frame_form_cliente.grid(row=0, column=0, sticky="nsew")

def mostrar_lista_clientes(app):
    app.frame_form_cliente.grid_forget()
    app.frame_lista_clientes.grid(row=0, column=0, sticky="nsew")
    atualizar_lista_clientes(app)

def atualizar_lista_clientes(app, event=None):
    for widget in app.scroll_todos.winfo_children(): widget.destroy()
    for widget in app.scroll_pf.winfo_children(): widget.destroy()
    for widget in app.scroll_pj.winfo_children(): widget.destroy()

    def carregar_icone(caminho, tamanho=(16, 16)):
        try: return ctk.CTkImage(Image.open(f"assets/{caminho}"), size=tamanho)
        except: return None

    img_id, img_rg = carregar_icone("icon_id.png"), carregar_icone("icon_rg.png")
    img_tel, img_mail = carregar_icone("icon_tel.png"), carregar_icone("icon_mail.png")
    img_cnpj, img_resp = carregar_icone("icon_cnpj.png"), carregar_icone("icon_responsavel.png")
    img_proc_item = carregar_icone("icon_processo_item.png", (16, 16))
    img_link = carregar_icone("icon_link.png", (18, 18))
    img_edit, img_del = carregar_icone("icon_edit.png", (14, 14)), carregar_icone("icon_delete.png", (14, 14))
    
    img_seta = carregar_icone("icon_seta.png", (12, 12))
    img_seta_cima = carregar_icone("icon_seta_cima.png", (12, 12)) 

    termo = app.entry_busca_cliente.get() if hasattr(app, 'entry_busca_cliente') else ""
    if termo == "Buscar por Nome, CPF ou CNPJ...": termo = ""

    try: clientes_db = buscar_clientes(termo)
    except: clientes_db = []
    
    aba_atual = app.tabs_pf_pj.get()

    for c in clientes_db:
        try:
            id_c, tipo_pessoa, nome, doc, rg, tel, email, prof, est_civil, nat, endereco, estado, tipo_unidade, resp, obs = c
            is_pj = tipo_pessoa == "Pessoa Jurídica"
            
            if aba_atual == "Todos": parent = app.scroll_todos
            elif aba_atual == "Pessoa Jurídica" and is_pj: parent = app.scroll_pj
            elif aba_atual == "Pessoa Física" and not is_pj: parent = app.scroll_pf
            else: continue
            
            cor_accent = "#C9A84C" if is_pj else "#1C2E45" 

            # AJUSTE DE HARMONIA: Cards com fundo mais claro (#2B2B31) para diferenciar do fundo geral
            card = ctk.CTkFrame(parent, corner_radius=10, height=65, fg_color=("#FFFFFF", "#FFFFFF"), border_width=1, border_color=("#E0E3E8", "#3A3A42"))
            card.pack(fill="x", padx=15, pady=4)
            card.pack_propagate(False)

            ctk.CTkFrame(card, width=4, fg_color=cor_accent, corner_radius=0).pack(side="left", fill="y")
            
            content_frame = ctk.CTkFrame(card, fg_color="transparent")
            content_frame.pack(side="left", fill="both", expand=True, padx=12, pady=5)

            header = ctk.CTkFrame(content_frame, fg_color="transparent")
            header.pack(fill="x")
            ctk.CTkLabel(header, text=nome.upper(), font=ctk.CTkFont(size=13, weight="bold"), text_color=cor_accent).pack(side="left")

            btn_frame = ctk.CTkFrame(header, fg_color="transparent")
            btn_frame.pack(side="right")
            
            btn_exp = ctk.CTkButton(btn_frame, text="", image=img_seta, width=28, height=28, fg_color="transparent", hover_color=("#E0E3E8", "gray30"))
            btn_exp.pack(side="left", padx=1)
            ctk.CTkButton(btn_frame, text="", image=img_edit, width=28, height=28, fg_color="transparent", hover_color=("#E0E3E8", "gray30"), command=lambda d=c: ir_para_editar(app, d)).pack(side="left", padx=1)
            ctk.CTkButton(btn_frame, text="", image=img_del, width=28, height=28, fg_color="transparent", text_color="#d93838", hover_color=("#E0E3E8", "gray30"), command=lambda i=id_c: confirmar_exclusao_cliente(app, i)).pack(side="left", padx=1)

            info_row = ctk.CTkFrame(content_frame, fg_color="transparent")
            info_row.pack(fill="x")

            if is_pj:
                if doc: ctk.CTkLabel(info_row, text=f"  {doc}", image=img_cnpj, compound="left", font=ctk.CTkFont(size=11)).pack(side="left", padx=(0, 15))
                if resp: ctk.CTkLabel(info_row, text=f"  {resp}", image=img_resp, compound="left", font=ctk.CTkFont(size=11)).pack(side="left")
            else:
                if doc: ctk.CTkLabel(info_row, text=f"  {doc}", image=img_id, compound="left", font=ctk.CTkFont(size=11)).pack(side="left", padx=(0, 12))
                if rg: ctk.CTkLabel(info_row, text=f"  {rg}", image=img_rg, compound="left", font=ctk.CTkFont(size=11)).pack(side="left", padx=(0, 12))
                if tel: ctk.CTkLabel(info_row, text=f"  {tel}", image=img_tel, compound="left", font=ctk.CTkFont(size=11)).pack(side="left", padx=(0, 12))
                if email: ctk.CTkLabel(info_row, text=f"  {email}", image=img_mail, compound="left", font=ctk.CTkFont(size=11)).pack(side="left")

            frame_detalhes = ctk.CTkFrame(content_frame, fg_color="transparent")

            l_extra = ctk.CTkFrame(frame_detalhes, fg_color="transparent")
            l_extra.pack(fill="x", pady=(8, 0))
            
            if not is_pj:
                if prof:
                    ctk.CTkLabel(l_extra, text="Profissão: ", font=ctk.CTkFont(size=11, weight="bold")).pack(side="left")
                    ctk.CTkLabel(l_extra, text=f"{prof} ", font=ctk.CTkFont(size=11)).pack(side="left")
                    ctk.CTkFrame(l_extra, width=1, height=10, fg_color="gray70").pack(side="left", padx=8)
                if est_civil:
                    ctk.CTkLabel(l_extra, text=" Estado Civil: ", font=ctk.CTkFont(size=11, weight="bold")).pack(side="left")
                    ctk.CTkLabel(l_extra, text=f"{est_civil} ", font=ctk.CTkFont(size=11)).pack(side="left")
                    ctk.CTkFrame(l_extra, width=1, height=10, fg_color="gray70").pack(side="left", padx=8)
                if nat:
                    ctk.CTkLabel(l_extra, text=" Naturalidade: ", font=ctk.CTkFont(size=11, weight="bold")).pack(side="left")
                    ctk.CTkLabel(l_extra, text=f"{nat}", font=ctk.CTkFont(size=11)).pack(side="left")
                if endereco:
                    l_end = ctk.CTkFrame(frame_detalhes, fg_color="transparent")
                    l_end.pack(fill="x", pady=2)
                    ctk.CTkLabel(l_end, text="Endereço: ", font=ctk.CTkFont(size=11, weight="bold")).pack(side="left")
                    ctk.CTkLabel(l_end, text=f"{endereco}", font=ctk.CTkFont(size=11)).pack(side="left")
            else:
                if estado:
                    ctk.CTkLabel(l_extra, text="Estado: ", font=ctk.CTkFont(size=11, weight="bold")).pack(side="left")
                    ctk.CTkLabel(l_extra, text=f"{estado} ", font=ctk.CTkFont(size=11)).pack(side="left")
                    ctk.CTkFrame(l_extra, width=1, height=10, fg_color="gray70").pack(side="left", padx=8)
                if tipo_unidade:
                    ctk.CTkLabel(l_extra, text=" Unidade: ", font=ctk.CTkFont(size=11, weight="bold")).pack(side="left")
                    ctk.CTkLabel(l_extra, text=f"{tipo_unidade}", font=ctk.CTkFont(size=11)).pack(side="left")

            ctk.CTkFrame(frame_detalhes, height=2, fg_color=("#E0E3E8", "gray30")).pack(fill="x", pady=(20, 20))

            if obs:
                l_obs = ctk.CTkFrame(frame_detalhes, fg_color="transparent")
                l_obs.pack(fill="x", pady=(0, 15))
                ctk.CTkLabel(l_obs, text="Observações:", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
                ctk.CTkLabel(l_obs, text=obs, font=ctk.CTkFont(size=11)).pack(anchor="w", padx=5)

            try: procs_cliente = buscar_processos(nome)
            except: procs_cliente = []

            if procs_cliente:
                ctk.CTkLabel(frame_detalhes, text="PROCESSOS ATIVOS", font=ctk.CTkFont(size=11, weight="bold"), text_color=("#1A1A1A", "#FFFFFF")).pack(anchor="w", pady=(10, 5))
                
                for p in procs_cliente:
                    # AJUSTE DE HARMONIA: Cards internos um tom levemente diferente para não ser pretão
                    p_item = ctk.CTkFrame(frame_detalhes, fg_color=("#E9ECEF", "#323238"), corner_radius=6, height=120)
                    p_item.pack(fill="x", pady=2)
                    p_item.pack_propagate(False) 

                    ctk.CTkFrame(p_item, width=4, fg_color=cor_accent, corner_radius=0).pack(side="left", fill="y")
                    
                    p_grid = ctk.CTkFrame(p_item, fg_color="transparent")
                    p_grid.pack(fill="both", expand=True, padx=10)

                    p_grid.grid_columnconfigure((0, 2, 4), weight=1, uniform="colunas")
                    p_grid.grid_columnconfigure((1, 3), weight=0)
                    p_grid.grid_rowconfigure(0, weight=1)

                    ctk.CTkLabel(p_grid, text=f" {p[2]}", image=img_proc_item, compound="left", text_color=("#1A1A1A", "white"), font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, sticky="")
                    ctk.CTkFrame(p_grid, 1, height=1, fg_color=("#E0E3E8", "gray30")).grid(row=0, column=1, sticky="ns", pady=15)

                    status_col = ctk.CTkFrame(p_grid, fg_color="transparent")
                    status_col.grid(row=0, column=2, sticky="") 
                    ctk.CTkLabel(status_col, text="STATUS", font=ctk.CTkFont(size=10, weight="bold"), text_color=cor_accent).pack(anchor="center", pady=(0, 2))
                    lista_status = str(p[13]).split(',')
                    for st in lista_status:
                        if st.strip() != "Todos":
                            ctk.CTkLabel(status_col, text=st.strip(), font=ctk.CTkFont(size=10)).pack(anchor="center", pady=0)

                    ctk.CTkFrame(p_grid, width=1, height=1, fg_color=("#E0E3E8", "gray30")).grid(row=0, column=3, sticky="ns", pady=15)

                    btn_frame_proc = ctk.CTkFrame(p_grid, fg_color="transparent")
                    btn_frame_proc.grid(row=0, column=4, sticky="")
                    ctk.CTkButton(btn_frame_proc, text="", image=img_link, width=32, height=32, fg_color="transparent", hover=False, command=lambda num_proc=p[2]: redirecionar_para_processo(app, num_proc)).pack(anchor="center")

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
            
            if hasattr(app, "cliente_expandir_alvo") and app.cliente_expandir_alvo == nome:
                app.after(50, toggle)
                app.cliente_expandir_alvo = None

        except Exception as e:
            print(f"Erro ao carregar cliente: {e}")

def ir_para_editar(app, dados):
    id_c, tipo_pessoa, nome, doc, rg, tel, email, prof, est_civil, nat, endereco, estado, tipo_unidade, resp, obs = dados
    app.id_edicao_cli = id_c
    app.var_tipo_pessoa.set(tipo_pessoa)
    alternar_campos_pj(app)
    
    for ent in app.entradas_cli.values(): 
        ent.delete(0, 'end')
    app.txt_obs_cli.delete("0.0", "end")
    
    if tipo_pessoa == "Pessoa Física":
        for k, v in zip(["Nome Completo: *", "CPF:", "RG:", "Telefone: *", "E-mail:", "Profissão:", "Estado Civil:", "Naturalidade:", "Endereço:"], [nome, doc, rg, tel, email, prof, est_civil, nat, endereco]):
            app.entradas_cli[k].insert(0, v if v else "")
    else:
        for k, v in zip(["Razão Social: *", "CNPJ: *", "Estado:", "Responsável:"], [nome, doc, estado, resp]):
            app.entradas_cli[k].insert(0, v if v else "")
        app.var_unidade_pj.set(tipo_unidade)
        
    app.txt_obs_cli.insert("0.0", obs if obs else "")
    app.frame_lista_clientes.grid_forget()
    app.frame_form_cliente.grid(row=0, column=0, sticky="nsew")

def confirmar_exclusao_cliente(app, id_cliente):
    modal = ctk.CTkToplevel(app)
    modal.title("Confirmar")
    modal.geometry("350x150")
    modal.attributes("-topmost", True)
    modal.grab_set()

    ctk.CTkLabel(modal, text="Você quer mesmo excluir esse cliente?", font=ctk.CTkFont(weight="bold", size=14)).pack(pady=(25, 20))

    frame_botoes = ctk.CTkFrame(modal, fg_color="transparent")
    frame_botoes.pack()

    def sim():
        modal.destroy()
        app.update_idletasks()
        remover_cliente(app, id_cliente)

    ctk.CTkButton(frame_botoes, text="Sim", fg_color="#2ecc71", hover_color="#27ae60", text_color="#1A1A2E", width=100, command=sim).pack(side="left", padx=10)
    ctk.CTkButton(frame_botoes, text="Cancelar", fg_color="#F4F5F7", hover_color="#E0E3E8", text_color="#1A1A2E", border_width=1, border_color="#E0E3E8", width=120, height=36, corner_radius=8, font=ctk.CTkFont(weight="bold"), command=modal.destroy).pack(side="left", padx=8)

def remover_cliente(app, id_cliente):
    try:
        cliente_dados = [c for c in buscar_clientes() if c[0] == id_cliente][0]
        nome_cliente = cliente_dados[2]
        
        procs = buscar_processos()
        procs_afetados = [p for p in procs if p[1] == nome_cliente]
        
        if len(procs_afetados) > 0:
            msg = f"⚠️ O cliente '{nome_cliente}' foi excluído e {len(procs_afetados)} processo(s) ficaram sem titular!"
            app.notificacoes.append({"msg": msg, "cor": "alerta"})
            layout.atualizar_sino(app)
    except Exception: pass

    deletar_cliente(id_cliente)
    atualizar_lista_clientes(app)
    if hasattr(processos, 'atualizar_lista_processos'):
        processos.atualizar_lista_processos(app)

def salvar_cliente(app):
    tipo_pessoa = app.var_tipo_pessoa.get()
    obs = app.txt_obs_cli.get("0.0", "end").strip()

    if tipo_pessoa == "Pessoa Física":
        nome = app.entradas_cli["Nome Completo: *"].get().strip()
        tel = app.entradas_cli["Telefone: *"].get().strip()
        
        apenas_numeros = "".join(filter(str.isdigit, tel))
        if len(apenas_numeros) < 10:
            app.notificacoes.append({"msg": "O telefone deve conter pelo menos 10 dígitos (DDD + Número).", "cor": "alerta"})
            from modules import layout; layout.atualizar_sino(app)
            return

        if not nome: return 
            
        doc = app.entradas_cli["CPF:"].get().strip()
        rg = app.entradas_cli["RG:"].get().strip()
        email = app.entradas_cli["E-mail:"].get().strip()
        prof = app.entradas_cli["Profissão:"].get().strip()
        est_civil = app.entradas_cli["Estado Civil:"].get().strip()
        nat = app.entradas_cli["Naturalidade:"].get().strip()
        endereco = app.entradas_cli["Endereço:"].get().strip()
        estado = tipo_unidade = resp = ""
    else:
        nome = app.entradas_cli["Razão Social: *"].get().strip()
        doc = app.entradas_cli["CNPJ: *"].get().strip()
        
        apenas_numeros_cnpj = "".join(filter(str.isdigit, doc))
        if len(apenas_numeros_cnpj) < 14:
            app.notificacoes.append({"msg": "O CNPJ deve conter exatamente 14 dígitos.", "cor": "alerta"})
            return

        if not nome: return 
            
        estado = app.entradas_cli["Estado:"].get().strip()
        tipo_unidade = app.var_unidade_pj.get()
        resp = app.entradas_cli["Responsável:"].get().strip()
        rg = tel = email = prof = est_civil = nat = endereco = ""

    id_edicao = getattr(app, "id_edicao_cli", None)

    if id_edicao:
        from database.database import obter_nome_cliente_por_id, atualizar_cliente_completo, sincronizar_nome_processos
        nome_antigo = obter_nome_cliente_por_id(id_edicao)
        atualizar_cliente_completo(id_edicao, tipo_pessoa, nome, doc, rg, tel, email, prof, est_civil, nat, endereco, estado, tipo_unidade, resp, obs)
        app.notificacoes.append({"msg": f"Informações do cliente '{nome}' editadas.", "cor": "info"})
        if nome_antigo and nome_antigo != nome:
            sincronizar_nome_processos(nome_antigo, nome)
    else:
        from database.database import adicionar_cliente
        adicionar_cliente(tipo_pessoa, nome, doc, rg, tel, email, prof, est_civil, nat, endereco, estado, tipo_unidade, resp, obs)

    mostrar_lista_clientes(app)