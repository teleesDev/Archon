import customtkinter as ctk
import calendar
from datetime import datetime
from database.database import (
    adicionar_evento_agenda, atualizar_evento_agenda, 
    buscar_eventos_do_mes, deletar_evento_agenda
)
from modules.utils import formatar_data
from modules import layout
from PIL import Image

FERIADOS_DB = {
    (2026, 1, 1): {"nome": "Confraternização", "tipo": "nacional"},
    (2026, 2, 16): {"nome": "Carnaval", "tipo": "nacional"},
    (2026, 2, 17): {"nome": "Carnaval", "tipo": "nacional"},
    (2026, 2, 18): {"nome": "Quarta de Cinzas", "tipo": "nacional"},
    (2026, 4, 3): {"nome": "Paixão de Cristo", "tipo": "nacional"},
    (2026, 4, 5): {"nome": "Páscoa", "tipo": "comemorativa"},
    (2026, 4, 21): {"nome": "Tiradentes", "tipo": "nacional"},
    (2026, 5, 1): {"nome": "Dia do Trabalho", "tipo": "nacional"},
    (2026, 6, 4): {"nome": "Corpus Christi", "tipo": "nacional"},
    (2026, 9, 7): {"nome": "Independência", "tipo": "nacional"},
    (2026, 10, 12): {"nome": "N. Sra. Aparecida", "tipo": "nacional"},
    (2026, 11, 2): {"nome": "Finados", "tipo": "nacional"},
    (2026, 11, 15): {"nome": "Proc. da República", "tipo": "nacional"},
    (2026, 11, 20): {"nome": "Consciência Negra", "tipo": "nacional"},
    (2026, 12, 25): {"nome": "Natal", "tipo": "nacional"}
}

def criar_aba_calendario(app, parent_frame):
    for widget in parent_frame.winfo_children():
        widget.destroy()

    parent_frame.grid_rowconfigure(0, weight=1)
    parent_frame.grid_columnconfigure(0, weight=1)

    # ── Container principal ───────────────────────────────────────────────────
    app.blocao_calendario = ctk.CTkFrame(parent_frame, fg_color="#FFFFFF",
                                          corner_radius=14,
                                          border_width=1, border_color="#E0E3E8")
    app.blocao_calendario.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
    app.blocao_calendario.grid_rowconfigure(1, weight=1)
    app.blocao_calendario.grid_columnconfigure(0, weight=1)

    # ── Barra topo navy ────────────────────────────────────────────────────────
    barra_topo = ctk.CTkFrame(app.blocao_calendario, fg_color="#1C2E45",
                               height=62, corner_radius=0)
    barra_topo.grid(row=0, column=0, sticky="ew")
    barra_topo.grid_propagate(False)
    barra_topo.grid_columnconfigure(4, weight=1)

    app.meses_nomes = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho",
                       "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]

    hoje = datetime.now()
    app.var_cal_mes = ctk.StringVar(value=app.meses_nomes[hoje.month - 1])
    app.var_cal_ano = ctk.StringVar(value=str(hoje.year))

    ctk.CTkButton(barra_topo, text="+ Evento", width=100, height=34,
                  fg_color="#C9A84C", hover_color="#A8893C",
                  text_color="#1A1A2E", font=ctk.CTkFont(weight="bold"),
                  corner_radius=8,
                  command=lambda: abrir_modal_evento(app)
                  ).grid(row=0, column=0, padx=(20, 16), pady=14)

    ctk.CTkLabel(barra_topo, text="Mes:", font=ctk.CTkFont(weight="bold"),
                 text_color="#D0D8E8").grid(row=0, column=1, padx=(0, 6))
    ctk.CTkOptionMenu(barra_topo, values=app.meses_nomes,
                      variable=app.var_cal_mes,
                      fg_color="#253A56", button_color="#1C2E45",
                      button_hover_color="#2A4065",
                      text_color="#FFFFFF", dropdown_fg_color="#1C2E45",
                      dropdown_text_color="#FFFFFF", width=130,
                      command=lambda e: atualizar_calendario(app)
                      ).grid(row=0, column=2, padx=(0, 20))

    ctk.CTkLabel(barra_topo, text="Ano:", font=ctk.CTkFont(weight="bold"),
                 text_color="#D0D8E8").grid(row=0, column=3, padx=(0, 6))
    app.combo_anos_cal = ctk.CTkOptionMenu(
        barra_topo,
        values=["2024","2025","2026","2027","2028","2029","2030"],
        variable=app.var_cal_ano,
        fg_color="#253A56", button_color="#1C2E45",
        button_hover_color="#2A4065",
        text_color="#FFFFFF", dropdown_fg_color="#1C2E45",
        dropdown_text_color="#FFFFFF", width=100,
        command=lambda e: atualizar_calendario(app)
    )
    app.combo_anos_cal.grid(row=0, column=4, sticky="w")

    # Legenda compacta
    leg = ctk.CTkFrame(barra_topo, fg_color="transparent")
    leg.grid(row=0, column=5, padx=20, sticky="e")
    def _pip(p, cor, t):
        f = ctk.CTkFrame(p, fg_color="transparent")
        f.pack(side="left", padx=5)
        ctk.CTkFrame(f, fg_color=cor, width=10, height=10, corner_radius=2).pack(side="left", padx=(0, 3))
        ctk.CTkLabel(f, text=t, font=ctk.CTkFont(size=10), text_color="#D0D8E8").pack(side="left")
    _pip(leg, "#FCE68E", "Nacionais")
    _pip(leg, "#A8E6A3", "Estaduais")
    _pip(leg, "#E0E4E8", "Comemorativas")
    _pip(leg, "#e74c3c", "Datas Imp.")
    _pip(leg, "#74b9ff", "Compromissos")

    # ── Grid do calendário ─────────────────────────────────────────────────────
    app.frame_grid_cal = ctk.CTkFrame(app.blocao_calendario, fg_color="transparent")
    app.frame_grid_cal.grid(row=1, column=0, sticky="nsew", padx=16, pady=(8, 8))

    # ── Navegação inferior ─────────────────────────────────────────────────────
    nav = ctk.CTkFrame(app.blocao_calendario, fg_color="transparent", height=56)
    nav.grid(row=2, column=0, pady=(0, 14))
    nav.grid_propagate(False)

    try:
        img_esq = ctk.CTkImage(Image.open("assets/icone_seta_esq.png"), size=(20, 20))
        img_dir = ctk.CTkImage(Image.open("assets/icone_seta_dir.png"), size=(20, 20))
    except:
        img_esq = img_dir = None

    ctk.CTkButton(nav, text="  Anterior", image=img_esq, compound="left",
                  width=130, height=38, corner_radius=8,
                  fg_color="#1C2E45", hover_color="#253A56",
                  text_color="#FFFFFF", font=ctk.CTkFont(weight="bold"),
                  command=lambda: mover_mes(app, -1)).pack(side="left", padx=(0, 12))

    ctk.CTkButton(nav, text="Proximo  ", image=img_dir, compound="right",
                  width=130, height=38, corner_radius=8,
                  fg_color="#1C2E45", hover_color="#253A56",
                  text_color="#FFFFFF", font=ctk.CTkFont(weight="bold"),
                  command=lambda: mover_mes(app, 1)).pack(side="left")


def mover_mes(app, direcao):
    mes_atual = app.var_cal_mes.get()
    ano_atual = int(app.var_cal_ano.get())
    idx = app.meses_nomes.index(mes_atual)
    
    novo_idx = idx + direcao

    if novo_idx > 11:
        novo_idx = 0
        ano_atual += 1
    elif novo_idx < 0:
        novo_idx = 11
        ano_atual -= 1

    app.var_cal_mes.set(app.meses_nomes[novo_idx])
    app.var_cal_ano.set(str(ano_atual))
    
    anos_atuais = app.combo_anos_cal.cget("values")
    if str(ano_atual) not in anos_atuais:
        anos_atuais.append(str(ano_atual))
        anos_atuais.sort()
        app.combo_anos_cal.configure(values=anos_atuais)

    atualizar_calendario(app)

def atualizar_calendario(app, event=None):
    for widget in app.frame_grid_cal.winfo_children():
        widget.destroy()

    app.celula_hover_atual = None

    for i in range(7): app.frame_grid_cal.grid_columnconfigure(i, weight=1, uniform="col")
    
    # AJUSTE: Diminuído o minsize de 80 para 65 para não forçar as linhas a cortarem a tela
    for i in range(1, 7): app.frame_grid_cal.grid_rowconfigure(i, weight=1, minsize=65, uniform="row")

    dias_semana = ["DOM", "SEG", "TER", "QUA", "QUI", "SEX", "SÁB"]
    for i, dia in enumerate(dias_semana):
        ctk.CTkLabel(app.frame_grid_cal, text=dia, font=ctk.CTkFont(weight="bold", size=14), text_color=("gray20", "gray80")).grid(row=0, column=i, pady=(0, 5))

    mes_idx = app.meses_nomes.index(app.var_cal_mes.get()) + 1
    ano_num = int(app.var_cal_ano.get())

    calendar.setfirstweekday(calendar.SUNDAY)
    matriz_mes = calendar.monthcalendar(ano_num, mes_idx)
    while len(matriz_mes) < 6: matriz_mes.append([0, 0, 0, 0, 0, 0, 0])

    eventos_mes = buscar_eventos_do_mes(mes_idx, ano_num)
    eventos_dict = {}
    for ev in eventos_mes:
        d = ev[4]
        if d not in eventos_dict: eventos_dict[d] = []
        eventos_dict[d].append(ev)

    def carregar_icone_cal(caminho, tamanho):
        try: return ctk.CTkImage(Image.open(f"assets/{caminho}"), size=tamanho)
        except: return None
        
    img_alerta_cal = carregar_icone_cal("alerta_calendar.png", (14, 14))
    img_obs_cal = carregar_icone_cal("observacoes_calendar.png", (12, 12))

    hoje_real = datetime.now()

    for row_idx in range(6):
        for col_idx, dia in enumerate(matriz_mes[row_idx]):
            if dia != 0: 
                info_feriado = FERIADOS_DB.get((ano_num, mes_idx, dia))
                is_hoje = (dia == hoje_real.day and mes_idx == hoje_real.month and ano_num == hoje_real.year)
                    
                cor_fundo = ("gray95", "gray15")
                cor_texto_dia = ("black", "white")
                    
                if info_feriado:
                    cor_texto_dia = "black"
                    if info_feriado["tipo"] == "nacional": cor_fundo = "#FCE68E"
                    elif info_feriado["tipo"] == "estadual": cor_fundo = "#A8E6A3"
                    else: cor_fundo = "#E0E4E8"

                # Define borda destaque se for hoje
                b_color = "#C9A84C" if is_hoje else ("gray70", "gray30")
                b_width = 2 if is_hoje else 1

                celula_frame = ctk.CTkFrame(app.frame_grid_cal, border_width=b_width, border_color=b_color, fg_color=cor_fundo, corner_radius=10, cursor="hand2")
                celula_frame.grid(row=row_idx + 1, column=col_idx, sticky="nsew", padx=3, pady=3)
                celula_frame.eh_hoje = is_hoje # injetando a flag no componente para uso nas interações do mouse
                    
                top_frame = ctk.CTkFrame(celula_frame, fg_color="transparent", height=25)
                top_frame.pack(fill="x", padx=8, pady=(4, 0))
                    
                if info_feriado:
                    ctk.CTkLabel(top_frame, text=info_feriado["nome"].upper(), font=ctk.CTkFont(size=9, weight="bold"), text_color=cor_texto_dia).pack(side="left", anchor="nw")
                    
                ctk.CTkLabel(top_frame, text=str(dia), font=ctk.CTkFont(weight="bold", size=14), text_color=cor_texto_dia).pack(side="right", anchor="ne")

                evs_do_dia = eventos_dict.get(dia, [])
                    
                # Contador: quantos eventos além dos tipos únicos exibidos
                total_extra = max(0, len(evs_do_dia) - len(set(ev[1] for ev in evs_do_dia)))
                total_extra += max(0, len(set(ev[1] for ev in evs_do_dia)) - 2)  # max 2 barras
                if len(evs_do_dia) > 0:
                    tipos_unicos = len(set(ev[1] for ev in evs_do_dia))
                    qtd_extra = len(evs_do_dia) - min(tipos_unicos, 2)
                    if qtd_extra > 0:
                        lbl_extra = ctk.CTkLabel(top_frame, text=f" +{qtd_extra}",
                                                  image=img_alerta_cal if img_alerta_cal else None,
                                                  compound="left",
                                                  font=ctk.CTkFont(size=11, weight="bold"),
                                                  text_color="#000000")
                        lbl_extra._is_extra_label = True
                        lbl_extra.pack(side="right", anchor="ne", padx=(0, 6))

                frame_linhas = ctk.CTkFrame(celula_frame, fg_color="transparent")
                frame_linhas.pack(fill="both", expand=True, padx=4, pady=2)

                # Mostrar máximo 1 barra por tipo (1 azul + 1 vermelha no máximo)
                tipos_exibidos = set()
                qtd_extras = 0
                for ev in evs_do_dia:
                    tipo_ev = ev[1]
                    if tipo_ev in tipos_exibidos:
                        qtd_extras += 1
                        continue
                    tipos_exibidos.add(tipo_ev)

                    tem_obs = bool(ev[3].strip())
                    bg_cor = "#e74c3c" if tipo_ev == "Importante" else "#74b9ff"
                    txt_cor = "white" if tipo_ev == "Importante" else "#1A1A2E"

                    lbl_ev = ctk.CTkLabel(frame_linhas, text=f" {ev[2]}",
                                           fg_color=bg_cor, text_color=txt_cor,
                                           corner_radius=4, height=20, anchor="w",
                                           font=ctk.CTkFont(size=9, weight="bold"))
                    if tem_obs and img_obs_cal:
                        lbl_ev.configure(image=img_obs_cal, compound="left", padx=5)
                    elif tem_obs:
                        lbl_ev.configure(text=f"! {ev[2]}")
                    lbl_ev.pack(fill="x", pady=2)

                # Atualizar contador de extras incluindo duplicatas de tipo
                if qtd_extras > 0 and top_frame.winfo_exists():
                    # Atualizar o label de +N se já existir, senão adicionar
                    extra_label = f" +{qtd_extras}"
                    try:
                        for child in top_frame.winfo_children():
                            if hasattr(child, '_is_extra_label'):
                                child.configure(text=extra_label)
                                break
                    except:
                        pass

                def ao_entrar(e, f_atual=celula_frame):
                    if app.celula_hover_atual == f_atual: return
                    
                    # Restaura a borda do anterior que perdeu foco (preservando o Dourado se for "Hoje")
                    if app.celula_hover_atual and app.celula_hover_atual.winfo_exists():
                        if getattr(app.celula_hover_atual, 'eh_hoje', False):
                            app.celula_hover_atual.configure(border_color="#C9A84C", border_width=2)
                        else:
                            app.celula_hover_atual.configure(border_color=("gray70", "gray30"), border_width=1)
                            
                    # Aplica o hover azul novo
                    f_atual.configure(border_color="#00a8ff", border_width=2)
                    app.celula_hover_atual = f_atual

                def ao_sair(e, f_atual=celula_frame):
                    x = f_atual.winfo_pointerx() - f_atual.winfo_rootx()
                    y = f_atual.winfo_pointery() - f_atual.winfo_rooty()
                    if 0 <= x <= f_atual.winfo_width() and 0 <= y <= f_atual.winfo_height(): return 
                    
                    # Regra de restauração customizada ao tirar o mouse
                    if getattr(f_atual, 'eh_hoje', False):
                        f_atual.configure(border_color="#C9A84C", border_width=2)
                    else:
                        f_atual.configure(border_color=("gray70", "gray30"), border_width=1)
                        
                    if app.celula_hover_atual == f_atual:
                        app.celula_hover_atual = None

                def ao_clicar(e, d=dia, evs=evs_do_dia, fer=info_feriado):
                    abrir_detalhes_dia(app, d, mes_idx, ano_num, fer, evs)

                def aplicar_binds(widget):
                    widget.bind("<Enter>", ao_entrar)
                    widget.bind("<Leave>", ao_sair)
                    widget.bind("<Button-1>", ao_clicar)
                    for child in widget.winfo_children(): 
                        aplicar_binds(child)
                        
                aplicar_binds(celula_frame)

def abrir_modal_evento(app, id_editar=None, dados_editar=None):
    modal = ctk.CTkToplevel(app)
    modal.title("Novo Evento" if not id_editar else "Editar Evento")
    modal.geometry("360x460")
    modal.attributes("-topmost", True)
    modal.grab_set()
    modal.configure(fg_color="#F4F5F7")

    # Cabeçalho
    hdr = ctk.CTkFrame(modal, fg_color="#1C2E45", height=50, corner_radius=0)
    hdr.pack(fill="x"); hdr.pack_propagate(False)
    ctk.CTkLabel(hdr,
                 text="Adicionar à Agenda" if not id_editar else "Editar Evento",
                 font=ctk.CTkFont(weight="bold", size=14),
                 text_color="#FFFFFF").pack(pady=14)

    var_tipo = ctk.StringVar(value="Compromisso")

    # ── Nome ──────────────────────────────────────────────────────────────────
    ctk.CTkLabel(modal, text="Nome do Evento: *",
                 font=ctk.CTkFont(weight="bold"), text_color="#1A1A2E"
                 ).pack(anchor="w", padx=30, pady=(14, 0))
    entry_nome = ctk.CTkEntry(modal, width=300, fg_color="#FFFFFF", border_color="#E0E3E8")
    entry_nome.pack(pady=5)

    # ── Data ──────────────────────────────────────────────────────────────────
    ctk.CTkLabel(modal, text="Data: *",
                 font=ctk.CTkFont(weight="bold"), text_color="#1A1A2E"
                 ).pack(anchor="w", padx=30, pady=(8, 0))
    frame_data = ctk.CTkFrame(modal, fg_color="transparent")
    frame_data.pack(fill="x", padx=30, pady=4)

    entry_data = ctk.CTkEntry(frame_data, width=210,
                               placeholder_text="DD/MM/AAAA",
                               fg_color="#FFFFFF", border_color="#E0E3E8")
    entry_data.pack(side="left")

    # Callbacks definidos DEPOIS de entry_data existir
    def atualizar_placeholder():
        if var_tipo.get() == "Importante":
            entry_data.configure(placeholder_text="DD/MM")
            if len(entry_data.get()) > 5:
                entry_data.delete(5, "end")
        else:
            entry_data.configure(placeholder_text="DD/MM/AAAA")

    def _fmt(e=None):
        if var_tipo.get() == "Importante":
            if len(entry_data.get()) > 5:
                entry_data.delete(5, "end")
            formatar_data(entry_data, e)
        else:
            formatar_data(entry_data, e)

    entry_data.bind("<KeyRelease>", _fmt)

    var_hoje = ctk.BooleanVar(value=False)
    def alternar_hoje():
        if var_hoje.get():
            fmt = "%d/%m/%Y" if var_tipo.get() == "Compromisso" else "%d/%m"
            entry_data.delete(0, "end")
            entry_data.insert(0, datetime.now().strftime(fmt))
            entry_data.configure(state="disabled")
        else:
            entry_data.configure(state="normal")

    ctk.CTkCheckBox(frame_data, text="Hoje", variable=var_hoje,
                    command=alternar_hoje, fg_color="#1C2E45",
                    hover_color="#253A56", text_color="#1A1A2E"
                    ).pack(side="right", padx=(15, 0))

    # ── Tipo (depois dos callbacks) ───────────────────────────────────────────
    frame_radios = ctk.CTkFrame(modal, fg_color="transparent")
    frame_radios.pack(pady=(8, 0))
    ctk.CTkRadioButton(frame_radios, text="Compromisso",
                       variable=var_tipo, value="Compromisso",
                       fg_color="#74b9ff", font=ctk.CTkFont(weight="bold"),
                       command=atualizar_placeholder).pack(side="left", padx=10)
    ctk.CTkRadioButton(frame_radios, text="Data Importante",
                       variable=var_tipo, value="Importante",
                       fg_color="#e74c3c", font=ctk.CTkFont(weight="bold"),
                       command=atualizar_placeholder).pack(side="left", padx=10)

    # ── Observações ───────────────────────────────────────────────────────────
    ctk.CTkLabel(modal, text="Observações (Opcional):",
                 font=ctk.CTkFont(weight="bold"), text_color="#1A1A2E"
                 ).pack(anchor="w", padx=30, pady=(10, 0))
    txt_obs = ctk.CTkTextbox(modal, width=300, height=80,
                              fg_color="#FFFFFF", border_color="#E0E3E8",
                              border_width=1, corner_radius=8)
    txt_obs.pack(pady=5)

    # ── Preencher se editando ─────────────────────────────────────────────────
    if dados_editar:
        var_tipo.set(dados_editar[1])
        atualizar_placeholder()
        entry_nome.insert(0, dados_editar[2])
        txt_obs.insert("0.0", dados_editar[3])
        if dados_editar[1] == "Importante":
            entry_data.insert(0, f"{dados_editar[4]:02d}/{dados_editar[5]:02d}")
        else:
            ano_fmt = dados_editar[6] if dados_editar[6] != 0 else int(app.var_cal_ano.get())
            entry_data.insert(0, f"{dados_editar[4]:02d}/{dados_editar[5]:02d}/{ano_fmt}")

    # ── Salvar ────────────────────────────────────────────────────────────────
    def salvar():
        tipo = var_tipo.get()
        nome = entry_nome.get().strip()
        data_str = entry_data.get().strip()
        obs  = txt_obs.get("0.0", "end").strip()

        if not nome: return

        if tipo == "Compromisso":
            if len(data_str) != 10: return
            dia, mes, ano = int(data_str[:2]), int(data_str[3:5]), int(data_str[6:])
        else:
            if len(data_str) != 5: return
            dia, mes, ano = int(data_str[:2]), int(data_str[3:5]), 0

        if id_editar:
            atualizar_evento_agenda(id_editar, tipo, nome, obs, dia, mes, ano)
            app.notificacoes.append({"msg": "Evento editado com sucesso.", "cor": "info"})
        else:
            adicionar_evento_agenda(tipo, nome, obs, dia, mes, ano)
            if var_hoje.get():
                app.notificacoes.append({"msg": f"Evento agendado para HOJE: {nome}", "cor": "info"})

        layout.atualizar_sino(app)
        atualizar_calendario(app)
        modal.destroy()

    ctk.CTkButton(modal, text="Salvar Evento",
                  font=ctk.CTkFont(weight="bold", size=13),
                  fg_color="#C9A84C", hover_color="#A8893C",
                  text_color="#1A1A2E", height=40, corner_radius=8,
                  command=salvar).pack(pady=16, padx=30, fill="x")


def abrir_detalhes_dia(app, dia, mes, ano, feriado_info, lista_eventos):
    modal = ctk.CTkToplevel(app)
    modal.title(f"Eventos do dia {dia:02d}/{mes:02d}/{ano}")
    modal.geometry("400x400")
    modal.attributes("-topmost", True)
    modal.grab_set()

    ctk.CTkLabel(modal, text=f"Agenda: {dia:02d}/{mes:02d}/{ano}", font=ctk.CTkFont(weight="bold", size=18)).pack(pady=(15, 10))

    scroll = ctk.CTkScrollableFrame(modal, fg_color="transparent")
    scroll.pack(fill="both", expand=True, padx=10, pady=5)

    if feriado_info:
        card_fer = ctk.CTkFrame(scroll, corner_radius=8, border_width=1, fg_color="#FCE68E" if feriado_info["tipo"] == "nacional" else "#A8E6A3" if feriado_info["tipo"] == "estadual" else "#E0E4E8")
        card_fer.pack(fill="x", pady=5)
        ctk.CTkLabel(card_fer, text=f"⭐ {feriado_info['nome']}", font=ctk.CTkFont(weight="bold"), text_color="#1A1A2E").pack(side="left", padx=10, pady=10)
        ctk.CTkLabel(card_fer, text="(Feriado/Comemorativa)", text_color="gray30", font=ctk.CTkFont(size=10)).pack(side="right", padx=10)

    if not lista_eventos and not feriado_info:
        ctk.CTkLabel(scroll, text="Nenhum evento neste dia.", text_color="gray").pack(pady=20)

    for ev in lista_eventos:
        id_ev, tipo, nome, obs = ev[0], ev[1], ev[2], ev[3]
            
        card_ev = ctk.CTkFrame(scroll, corner_radius=8, fg_color="#e74c3c" if tipo == "Importante" else "#74b9ff")
        card_ev.pack(fill="x", pady=5)
            
        txt_cor = "white" if tipo == "Importante" else "black"
        tem_obs = bool(obs.strip())
        nome_exibicao = f"! {nome}" if tem_obs else nome
            
        ctk.CTkLabel(card_ev, text=nome_exibicao, font=ctk.CTkFont(weight="bold"), text_color=txt_cor).pack(side="left", padx=10, pady=10)
            
        frame_btn = ctk.CTkFrame(card_ev, fg_color="transparent")
        frame_btn.pack(side="right", padx=5)

        def criar_cmd_apagar(i, c):
            def cmd():
                deletar_evento_agenda(i)
                c.destroy()
                atualizar_calendario(app)
            return cmd
            
        def criar_cmd_editar(d):
            def cmd():
                modal.destroy()
                abrir_modal_evento(app, id_editar=d[0], dados_editar=d)
            return cmd

        ctk.CTkButton(frame_btn, text="⋮", width=25, fg_color="gray20", hover_color="black", command=criar_cmd_editar(ev)).pack(side="left", padx=2)
        ctk.CTkButton(frame_btn, text="X", width=25, fg_color="#d63031", hover_color="#c0392b", command=criar_cmd_apagar(id_ev, card_ev)).pack(side="left", padx=2)