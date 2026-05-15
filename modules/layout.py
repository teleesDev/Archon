import customtkinter as ctk
from PIL import Image
import os

DIRETORIO_BASE = os.path.dirname(os.path.dirname(__file__))
PASTA_ASSETS   = os.path.join(DIRETORIO_BASE, "assets")

COR_NAVY  = "#1C2E45"
COR_GOLD  = "#C9A84C"
COR_CARD  = "#FFFFFF"
COR_BG    = "#F4F5F7"
COR_BORDA = "#E0E3E8"
COR_TEXT  = "#1A1A2E"


def carregar_imagem(nome_arquivo, tamanho):
    caminho = os.path.join(PASTA_ASSETS, nome_arquivo)
    try:
        img = Image.open(caminho)
        return ctk.CTkImage(light_image=img, dark_image=img, size=tamanho)
    except Exception:
        return None


def criar_cabecalho(app):
    """Mantida por compatibilidade — no-op na nova arquitetura."""
    pass


def criar_sino_notificacoes_tb(app, parent_frame):
    """
    Cria o botão de sino dentro do parent_frame (frame_direita na titlebar).
    O sino fica à direita do nome do advogado com espaçamento fixo para não
    colidir mesmo quando o badge "+N" aparece.
    """
    app.img_sino = carregar_imagem("sino.png", (20, 20))
    texto_padrao = "" if app.img_sino else "🔔"

    app.btn_sino = ctk.CTkButton(
        parent_frame,
        text=texto_padrao,
        image=app.img_sino,
        width=48, height=44,
        fg_color="transparent",
        hover_color="#2A4065",
        text_color="#FFFFFF",
        font=ctk.CTkFont(weight="bold", size=11),
        corner_radius=0,
        anchor="center",
        command=lambda: abrir_notificacoes(app)
    )

    app.btn_sino.pack(side="left", padx=(0, 6))


def criar_sino_notificacoes(app):
    """Compatibilidade: no-op se o sino já foi criado via criar_sino_notificacoes_tb."""
    if hasattr(app, 'btn_sino') and app.btn_sino.winfo_exists():
        return


def atualizar_sino(app):
    if not hasattr(app, 'btn_sino') or not app.btn_sino.winfo_exists():
        return

    qtd = len(app.notificacoes)
    if qtd > 0:
        app.btn_sino.configure(
            text=f" +{qtd}",
            text_color=COR_GOLD,
            font=ctk.CTkFont(weight="bold", size=11),
            compound="left" if app.img_sino else "center",
            width=56           # cresce ligeiramente, mas não empurra o nome
        )
    else:
        app.btn_sino.configure(
            text="" if app.img_sino else "🔔",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=12),
            width=48
        )


def abrir_notificacoes(app):
    if hasattr(app, 'modal_notificacoes') and app.modal_notificacoes.winfo_exists():
        app.modal_notificacoes.lift()
        app.modal_notificacoes.focus()
        return

    modal = ctk.CTkToplevel(app)
    app.modal_notificacoes = modal
    modal.title("Notificações")
    modal.geometry("420x420")
    modal.attributes("-topmost", True)
    modal.configure(fg_color=COR_BG)
    modal.resizable(False, False)

    # Cabeçalho
    header = ctk.CTkFrame(modal, fg_color=COR_NAVY, height=52, corner_radius=0)
    header.pack(fill="x")
    header.pack_propagate(False)
    ctk.CTkLabel(
        header,
        text="Central de Notificacoes",
        font=ctk.CTkFont(size=14, weight="bold"),
        text_color="#FFFFFF"
    ).pack(side="left", padx=20, pady=14)

    scroll = ctk.CTkScrollableFrame(modal, fg_color="transparent", corner_radius=0)
    scroll.pack(expand=True, fill="both", padx=12, pady=(10, 0))

    try:
        img_alerta = ctk.CTkImage(Image.open("assets/icon_notificacoes_alerta.png"), size=(18, 18))
        img_info   = ctk.CTkImage(Image.open("assets/icon_notificacoes_alteracoes.png"), size=(18, 18))
    except:
        img_alerta = img_info = None

    if not app.notificacoes:
        ctk.CTkLabel(scroll, text="Nenhuma notificacao no momento.",
                     text_color="gray50", font=ctk.CTkFont(size=13)).pack(pady=30)
    else:
        for item in reversed(app.notificacoes):
            msg  = item if isinstance(item, str) else item.get("msg", "")
            tipo = "alerta" if any(p in msg.lower() for p in ["excluido", "sem titular", "cancelado"]) else "info"
            icone_usar = img_alerta if tipo == "alerta" else img_info

            card = ctk.CTkFrame(scroll, fg_color=COR_CARD, corner_radius=10,
                                border_width=1, border_color=COR_BORDA)
            card.pack(fill="x", pady=4)

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=14, pady=10)

            if icone_usar:
                ctk.CTkLabel(inner, text="", image=icone_usar).pack(side="left", padx=(0, 10))

            ctk.CTkLabel(inner, text=msg, text_color=COR_TEXT,
                         wraplength=330, justify="left",
                         font=ctk.CTkFont(size=12)).pack(side="left", fill="x", expand=True)

    # Rodape
    rodape = ctk.CTkFrame(modal, fg_color="transparent", height=56)
    rodape.pack(fill="x", padx=12, pady=10)
    rodape.pack_propagate(False)

    def limpar_tudo():
        app.notificacoes.clear()
        atualizar_sino(app)
        modal.destroy()

    ctk.CTkButton(
        rodape, text="Limpar Todas",
        fg_color="#C0392B", hover_color="#96281B",
        text_color="white", font=ctk.CTkFont(weight="bold"),
        height=36, corner_radius=8, command=limpar_tudo
    ).pack(side="right")
