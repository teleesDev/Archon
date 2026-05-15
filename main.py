import customtkinter as ctk
import tkinter as tk
from database.database import criar_tabelas, criar_tabela_agenda
from modules import layout, dashboard, clientes, processos, financeiro, calendario, estrategias
import os
import sys
import ctypes
import ctypes.wintypes
from PIL import Image, ImageDraw

diretorio_atual = os.path.dirname(os.path.abspath(__file__))
sys.path.append(diretorio_atual)
caminho_tema = os.path.join(diretorio_atual, "styles", "theme_premium.json")

ctk.set_appearance_mode("light")
if os.path.exists(caminho_tema):
    ctk.set_default_color_theme(caminho_tema)
else:
    ctk.set_default_color_theme("blue")

# ── Paleta ────────────────────────────────────────────────────────────────────
COR_NAVY  = "#1C2E45"
COR_GOLD  = "#C9A84C"
COR_BG    = "#F4F5F7"
COR_CARD  = "#FFFFFF"
COR_BORDA = "#E0E3E8"
COR_TEXT  = "#1A1A2E"


# ── Windows API ───────────────────────────────────────────────────────────────
def _hwnd(widget):
    """Retorna o HWND nativo de qualquer widget Tkinter."""
    return ctypes.windll.user32.GetAncestor(widget.winfo_id(), 2)  # GA_ROOT=2


def _win_minimize(hwnd):
    ctypes.windll.user32.ShowWindow(hwnd, 6)   # SW_MINIMIZE


def _win_fix_redraw(hwnd):
    """
    Adiciona WS_EX_LAYERED ao extended style.
    Corrige o bug de janela overrideredirect sumir ao ser coberta.
    """
    GWL_EXSTYLE   = -20
    WS_EX_LAYERED = 0x00080000
    style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_LAYERED)
    # Opacidade 255 = totalmente opaco, só ativa o compositor
    ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0, 255, 2)  # LWA_ALPHA=2


def _gerar_logo_z(size=22):
    try:
        canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        d  = ImageDraw.Draw(canvas)
        m  = int(size * 0.12)
        lw = max(2, int(size * 0.10))
        gold = (201, 168, 76, 255)
        d.line([(m, m + lw//2),       (size-m, m + lw//2)      ], fill=gold, width=lw)
        d.line([(size-m, m),           (m, size-m)              ], fill=gold, width=lw)
        d.line([(m, size-m - lw//2),   (size-m, size-m - lw//2)], fill=gold, width=lw)
        return ctk.CTkImage(light_image=canvas, dark_image=canvas, size=(size, size))
    except Exception:
        return None


# ── Splash com Tk puro (fecha completamente antes do App abrir) ───────────────
def _mostrar_splash():
    """
    Cria e exibe um splash em Tk puro, anima a barra, e destrói tudo.
    Retorna só quando o splash fecha — síncrono, sem event loop residual.
    """
    root = tk.Tk()
    root.overrideredirect(True)
    root.configure(bg="#1C2E45")

    w, h = 420, 230
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
    root.attributes("-topmost", True)

    # Conteúdo
    tk.Label(root, text="ARCHON",
             font=("Microsoft YaHei UI", 30, "bold"),
             fg="#C9A84C", bg="#1C2E45").pack(pady=(32, 2))
    tk.Label(root, text="by Zenon  ·  Advocacia Digital",
             font=("Microsoft YaHei UI", 11),
             fg="#5E7A99", bg="#1C2E45").pack()

    # Barra de progresso manual com Canvas
    canvas = tk.Canvas(root, width=320, height=6, bg="#2A3F5A",
                       highlightthickness=0, bd=0)
    canvas.pack(pady=22)
    barra = canvas.create_rectangle(0, 0, 0, 6, fill="#C9A84C", outline="")

    root.update()

    # Anima de 0% a 100%
    for i in range(101):
        canvas.coords(barra, 0, 0, int(320 * i / 100), 6)
        root.update()
        root.after(12)   # ~12ms por frame → ~1.2s total

    root.destroy()


# ── App Principal ─────────────────────────────────────────────────────────────
class App(ctk.CTk):
    """
    Janela principal como CTk raiz — aparece na taskbar, tem ícone,
    minimiza corretamente.
    """
    def __init__(self):
        super().__init__()

        # Frameless — sem barra nativa do Windows
        self.overrideredirect(True)
        self.title("ARCHON")
        self.geometry("1400x820")
        self.minsize(1200, 700)
        self.configure(fg_color=COR_BG)

        # Define ícone (aparece no Alt+Tab mesmo com overrideredirect)
        try:
            self.iconbitmap("assets/icone.ico")
        except Exception:
            pass

        # Centralizar
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"1400x820+{(sw-1400)//2}+{(sh-820)//2}")

        # Guarda o HWND para operações nativas
        self.update()
        self._hwnd = _hwnd(self)
        _win_fix_redraw(self._hwnd)

        # Aparece na taskbar mesmo com overrideredirect via extended style
        self._registrar_na_taskbar()

        self._drag_x   = 0
        self._drag_y   = 0
        self._maximized = False
        self._geom_restore = ""
        self.notificacoes  = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)

        self._criar_titlebar()
        self._criar_navbar()
        self._criar_conteudo()

    def _registrar_na_taskbar(self):
        """
        Com overrideredirect=True a janela some da taskbar.
        Adicionar WS_EX_APPWINDOW força o Windows a exibi-la.
        """
        try:
            GWL_EXSTYLE      = -20
            WS_EX_APPWINDOW  = 0x00040000
            WS_EX_TOOLWINDOW = 0x00000080
            style = ctypes.windll.user32.GetWindowLongW(self._hwnd, GWL_EXSTYLE)
            # Remove ToolWindow (que esconde da taskbar) e adiciona AppWindow
            style = (style & ~WS_EX_TOOLWINDOW) | WS_EX_APPWINDOW
            ctypes.windll.user32.SetWindowLongW(self._hwnd, GWL_EXSTYLE, style)
            # Força atualização do frame para a taskbar registrar
            SWP_NOMOVE = 0x0002; SWP_NOSIZE = 0x0001
            SWP_NOZORDER = 0x0004; SWP_FRAMECHANGED = 0x0020
            ctypes.windll.user32.SetWindowPos(
                self._hwnd, 0, 0, 0, 0, 0,
                SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_FRAMECHANGED
            )
        except Exception:
            pass

    # ── TITLEBAR ──────────────────────────────────────────────────────────────
    def _criar_titlebar(self):
        tb = ctk.CTkFrame(self, fg_color=COR_NAVY, height=44, corner_radius=0)
        tb.grid(row=0, column=0, sticky="ew")
        tb.grid_propagate(False)
        tb.grid_columnconfigure(1, weight=1)

        # Marca
        img_z = _gerar_logo_z(22)
        fb = ctk.CTkFrame(tb, fg_color="transparent")
        fb.grid(row=0, column=0, padx=(14, 0), sticky="ns")

        if img_z:
            ctk.CTkLabel(fb, text="", image=img_z,
                         fg_color="transparent").pack(side="left", pady=11, padx=(0, 6))
        ctk.CTkLabel(fb, text="ARCHON",
                     font=ctk.CTkFont(family="Microsoft YaHei UI", size=13, weight="bold"),
                     text_color=COR_GOLD).pack(side="left")
        ctk.CTkLabel(fb, text="  ·  by Zenon (Z)",
                     font=ctk.CTkFont(family="Microsoft YaHei UI", size=10),
                     text_color="#5E7A99").pack(side="left", pady=(3, 0))

        for w in (tb, fb):
            w.bind("<ButtonPress-1>",   self._drag_start)
            w.bind("<B1-Motion>",       self._drag_motion)
            w.bind("<Double-Button-1>", self._toggle_maximizar)

        # Perfil + Sino
        fd = ctk.CTkFrame(tb, fg_color="transparent")
        fd.grid(row=0, column=2, sticky="ns", padx=(0, 4))

        try:
            img_u = ctk.CTkImage(Image.open("assets/user.png"), size=(24, 24))
        except:
            img_u = None

        ctk.CTkLabel(fd, text="  Dr. Alexandre Arantes",
                     image=img_u, compound="left",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color="#D0D8E8").pack(side="left", padx=(6, 18), pady=10)

        layout.criar_sino_notificacoes_tb(self, fd)

        # Botões window controls
        fc = ctk.CTkFrame(tb, fg_color="transparent")
        fc.grid(row=0, column=3, sticky="ns")

        ctk.CTkButton(fc, text="─", width=46, height=44,
                      fg_color="transparent", hover_color="#2A4065",
                      text_color="#FFF", font=ctk.CTkFont(size=13),
                      corner_radius=0,
                      command=self._minimizar).pack(side="left")

        self.btn_max = ctk.CTkButton(fc, text="□", width=46, height=44,
                                     fg_color="transparent", hover_color="#2A4065",
                                     text_color="#FFF", font=ctk.CTkFont(size=14),
                                     corner_radius=0,
                                     command=self._toggle_maximizar)
        self.btn_max.pack(side="left")

        ctk.CTkButton(fc, text="✕", width=46, height=44,
                      fg_color="transparent", hover_color="#C0392B",
                      text_color="#FFF", font=ctk.CTkFont(size=13),
                      corner_radius=0,
                      command=self.destroy).pack(side="left")

    # ── DRAG ──────────────────────────────────────────────────────────────────
    def _drag_start(self, event):
        if self._maximized: return
        self._drag_x = event.x_root - self.winfo_x()
        self._drag_y = event.y_root - self.winfo_y()

    def _drag_motion(self, event):
        if self._maximized: return
        self.geometry(f"+{event.x_root - self._drag_x}+{event.y_root - self._drag_y}")

    # ── MINIMIZAR — 100% via ctypes, nunca toca em overrideredirect ───────────
    def _minimizar(self):
        _win_minimize(self._hwnd)

    # ── MAXIMIZAR ─────────────────────────────────────────────────────────────
    def _toggle_maximizar(self, event=None):
        if self._maximized:
            self.geometry(self._geom_restore)
            self._maximized = False
            self.btn_max.configure(text="□")
        else:
            self._geom_restore = self.geometry()
            sw = self.winfo_screenwidth()
            sh = self.winfo_screenheight()
            self.geometry(f"{sw}x{sh}+0+0")
            self._maximized = True
            self.btn_max.configure(text="❐")

    # ── NAVBAR ────────────────────────────────────────────────────────────────
    def _criar_navbar(self):
        nav = ctk.CTkFrame(self, fg_color=COR_CARD, height=56, corner_radius=0)
        nav.grid(row=1, column=0, sticky="ew")
        nav.grid_propagate(False)
        nav.grid_columnconfigure(0, weight=1)

        ctk.CTkFrame(nav, height=2, fg_color=COR_GOLD, corner_radius=0).place(
            relx=0, rely=1.0, anchor="sw", relwidth=1.0)

        self.nav_frame = ctk.CTkFrame(nav, fg_color="transparent")
        self.nav_frame.grid(row=0, column=0, sticky="ns", pady=9, padx=16)

        def _ic(n, t):
            try: return ctk.CTkImage(Image.open(f"assets/{n}"), size=t)
            except: return None

        self.botoes_abas = {}
        for nome, img, texto in [
            ("Dashboard",      _ic("icone_dashboard.png",  (18,18)), "Dashboard"),
            ("Meus Clientes",  _ic("icone_clientes.png",   (18,18)), "Clientes"),
            ("Meus Processos", _ic("icone_processos.png",  (18,18)), "Processos"),
            ("Estratégias",    _ic("icon_strategy.png",    (18,18)), "Estratégias"),
            ("Financeiro",     _ic("icone_financeiro.png", (18,18)), "Financeiro"),
            ("Calendário",     _ic("icone_calendario.png", (20,20)), "Agenda"),
        ]:
            btn = ctk.CTkButton(
                self.nav_frame, image=img, text=f"  {texto}",
                font=ctk.CTkFont(family="Microsoft YaHei UI", size=12, weight="bold"),
                fg_color="transparent", text_color=COR_TEXT,
                hover_color="#EDF0F5", corner_radius=8, height=38, compound="left",
                command=lambda n=nome: self.selecionar_aba(n)
            )
            btn.pack(side="left", padx=3)
            self.botoes_abas[nome] = btn

    # ── CONTEÚDO ──────────────────────────────────────────────────────────────
    def _criar_conteudo(self):
        self.main_container = ctk.CTkFrame(self, fg_color=COR_BG, corner_radius=0)
        self.main_container.grid(row=2, column=0, sticky="nsew")
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        self.frames_abas = {
            "Dashboard":      ctk.CTkFrame(self.main_container, fg_color="transparent"),
            "Meus Clientes":  ctk.CTkFrame(self.main_container, fg_color="transparent"),
            "Meus Processos": ctk.CTkFrame(self.main_container, fg_color="transparent"),
            "Estratégias":    ctk.CTkFrame(self.main_container, fg_color="transparent"),
            "Financeiro":     ctk.CTkFrame(self.main_container, fg_color="transparent"),
            "Calendário":     ctk.CTkFrame(self.main_container, fg_color="transparent"),
        }

        for frame in self.frames_abas.values():
            frame.grid(row=0, column=0, sticky="nsew")

        dashboard.criar_dashboard(self, self.frames_abas["Dashboard"])
        clientes.criar_aba_clientes(self, self.frames_abas["Meus Clientes"])
        processos.criar_aba_processos(self, self.frames_abas["Meus Processos"])
        financeiro.criar_aba_financeiro(self, self.frames_abas["Financeiro"])
        calendario.criar_aba_calendario(self, self.frames_abas["Calendário"])
        estrategias.criar_aba_estrategias(self, self.frames_abas["Estratégias"])

        financeiro.atualizar_tela_financeira(self)
        self.selecionar_aba("Dashboard")

    # ── SELEÇÃO DE ABA ────────────────────────────────────────────────────────
    def selecionar_aba(self, nome_aba):
        for nome, frame in self.frames_abas.items():
            frame.grid_remove()
            btn = self.botoes_abas.get(nome)
            if btn:
                btn.configure(fg_color="transparent", text_color=COR_TEXT)

        self.frames_abas[nome_aba].grid(row=0, column=0, sticky="nsew")

        btn_ativo = self.botoes_abas.get(nome_aba)
        if btn_ativo:
            btn_ativo.configure(fg_color=COR_NAVY, text_color=COR_GOLD)

        rotas = {
            "Meus Clientes":  lambda: clientes.atualizar_lista_clientes(self),
            "Meus Processos": lambda: processos.atualizar_lista_processos(self),
            "Financeiro":     lambda: financeiro.atualizar_tela_financeira(self),
            "Estratégias":    lambda: estrategias.carregar_lista_estrategias(self),
            "Dashboard":      lambda: dashboard.criar_dashboard(self, self.frames_abas["Dashboard"]),
            "Calendário":     lambda: calendario.atualizar_calendario(self),
        }
        if nome_aba in rotas:
            rotas[nome_aba]()

    def ir_para_novo_cliente(self):
        self.selecionar_aba("Meus Clientes")
        clientes.mostrar_form_cliente(self)

    def ir_para_novo_processo(self):
        self.selecionar_aba("Meus Processos")
        processos.mostrar_form_processo(self)


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    criar_tabelas()
    criar_tabela_agenda()

    # 1. Splash roda e fecha completamente (Tk puro, sem resíduos)
    _mostrar_splash()

    # 2. App abre como CTk raiz — aparece na taskbar, tem ícone, minimiza certo
    app = App()
    app.mainloop()
