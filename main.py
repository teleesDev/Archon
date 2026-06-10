import customtkinter as ctk
import tkinter as tk
import shutil
import openpyxl
from database.database import criar_tabelas, criar_tabela_agenda
from modules import layout, dashboard, clientes, processos, financeiro, calendario, estrategias
import os
import sys
import ctypes
import ctypes.wintypes
import threading
import pystray
from pystray import MenuItem as TrayItem
from PIL import Image, ImageDraw

diretorio_atual = os.path.dirname(os.path.abspath(__file__))

# ── Substituir ícone da cobrinha do Python na taskbar — deve rodar ANTES de tudo ──
try:
    # Define um AppUserModelID único para o Archon.
    # Isso faz o Windows tratar o processo como "Archon", não como "python.exe".
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Zenon.Archon.App.1")
except Exception:
    pass
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


def _resource_path(relative_path):
    """Retorna caminho absoluto — funciona em dev e no executável PyInstaller."""
    import sys, os
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS  # pasta temporária do PyInstaller
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative_path)

def _aplicar_icone(janela):
    """Aplica o ícone Archon em qualquer janela ou modal."""
    try:
        from PIL import Image, ImageTk as _ITk
        base = os.path.dirname(os.path.abspath(__file__))
        candidatos_ico = []
        candidatos_png = []
        for pasta in [base, os.path.dirname(base)]:
            candidatos_ico.append(os.path.join(pasta, "archon_icon.ico"))
            candidatos_png.append(os.path.join(pasta, "archon_icon.png"))

        # Preferir .ico com wm_iconbitmap (mais confiável no Windows)
        for caminho in candidatos_ico:
            if os.path.exists(caminho):
                try:
                    janela.wm_iconbitmap(caminho)
                    return
                except Exception:
                    pass

        # Fallback: .png via iconphoto
        for caminho in candidatos_png + candidatos_ico:
            if os.path.exists(caminho):
                try:
                    img = Image.open(caminho).resize((32, 32), Image.LANCZOS)
                    photo = _ITk.PhotoImage(img)
                    janela.iconphoto(True, photo)
                    janela._icon_ref = photo
                    return
                except Exception:
                    pass
    except Exception:
        pass


def _hwnd(widget):
    """Retorna o HWND nativo de qualquer widget Tkinter."""
    return ctypes.windll.user32.GetAncestor(widget.winfo_id(), 2)  # GA_ROOT=2


def _definir_icone_taskbar(hwnd):
    """
    Define o ícone que aparece na taskbar e no Alt+Tab via Windows API.
    Usa LoadImage para carregar o .ico ou .png como HICON.
    """
    try:
        import os
        base = os.path.dirname(os.path.abspath(__file__))
        # Preferir .ico (mais compatível com Windows), depois .png
        for nome in ["archon_icon.ico", "archon_icon.png"]:
            caminho = os.path.join(base, nome)
            if os.path.exists(caminho):
                if caminho.endswith(".ico"):
                    # LoadImage carrega .ico nativamente
                    IMAGE_ICON  = 1
                    LR_LOADFROMFILE = 0x00000010
                    LR_DEFAULTSIZE  = 0x00000040
                    hicon = ctypes.windll.user32.LoadImageW(
                        None, caminho, IMAGE_ICON,
                        0, 0, LR_LOADFROMFILE | LR_DEFAULTSIZE
                    )
                else:
                    # Para .png: converter para ICO em memória com Pillow
                    from PIL import Image
                    import tempfile, struct, io
                    img = Image.open(caminho).resize((32, 32), Image.LANCZOS)
                    tmp = tempfile.NamedTemporaryFile(suffix=".ico", delete=False)
                    img.save(tmp.name, format="ICO", sizes=[(32, 32)])
                    tmp.close()
                    IMAGE_ICON  = 1
                    LR_LOADFROMFILE = 0x00000010
                    LR_DEFAULTSIZE  = 0x00000040
                    hicon = ctypes.windll.user32.LoadImageW(
                        None, tmp.name, IMAGE_ICON,
                        0, 0, LR_LOADFROMFILE | LR_DEFAULTSIZE
                    )
                    os.unlink(tmp.name)

                if hicon:
                    WM_SETICON = 0x0080
                    ICON_SMALL = 0
                    ICON_BIG   = 1
                    ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, hicon)
                    ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG,   hicon)
                return
    except Exception as e:
        pass


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
    root.withdraw()                    # esconde antes de qualquer coisa
    root.overrideredirect(True)
    root.configure(bg="#1C2E45")
    _aplicar_icone(root)

    w, h = 420, 230
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    x  = (sw - w) // 2
    y  = (sh - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")
    root.update_idletasks()            # processa a geometria antes de mostrar
    root.deiconify()                   # mostra já centralizado
    root.attributes("-topmost", True)

    # Conteúdo
    tk.Label(root, text="ARCHON",
             font=("Microsoft YaHei UI", 30, "bold"),
             fg="#C9A84C", bg="#1C2E45").pack(pady=(32, 2))
    tk.Label(root, text="  ·  Developed by Guilherme Teles  ·",
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
        self.title("Archon")
        self.geometry("1400x820")
        self.minsize(1200, 700)
        self.configure(fg_color=COR_BG)

        # Define ícone (aparece no Alt+Tab mesmo com overrideredirect)
        try:
            _aplicar_icone(self)
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

        # Define o ícone na taskbar via Windows API
        _definir_icone_taskbar(self._hwnd)

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

        self.withdraw()
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
        ctk.CTkLabel(fb, text="  ·  v1.0.0  ·  ",
                     font=ctk.CTkFont(family="Microsoft YaHei UI", size=10),
                     text_color="#5E7A99").pack(side="left", pady=(3, 0))

        for w in (tb, fb):
            w.bind("<ButtonPress-1>",   self._drag_start)
            w.bind("<B1-Motion>",       self._drag_motion)
            w.bind("<Double-Button-1>", self._toggle_maximizar)

        # Perfil + Sino
        fd = ctk.CTkFrame(tb, fg_color="transparent")
        fd.grid(row=0, column=2, sticky="nsew", padx=(0, 4))

        try:
            img_u = ctk.CTkImage(Image.open(_resource_path("assets/user.png")), size=(24, 24))
        except:
            img_u = None

        ctk.CTkLabel(fd, text="  Dr. Alexandre Arantes",
                     image=img_u, compound="left",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color="#D0D8E8").pack(side="left", padx=(6, 18), pady=0)

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
                      command=self._fechar_para_tray).pack(side="left")

    # ── DRAG ──────────────────────────────────────────────────────────────────
    def _drag_start(self, event):
        self._drag_x = event.x_root - self.winfo_x()
        self._drag_y = event.y_root - self.winfo_y()
        # Guarda posicao inicial do mouse para detectar arrasto quando maximizado
        self._drag_start_x = event.x_root
        self._drag_start_y = event.y_root

    def _drag_motion(self, event):
        if self._maximized:
            dy = event.y_root - self._drag_start_y
            dx = abs(event.x_root - self._drag_start_x)
            if dy < 10 and dx < 10:
                return
            # Calcular nova posicao antes de redesenhar
            win_w = int(self._geom_restore.split("x")[0])
            ratio = event.x_root / self.winfo_screenwidth()
            new_x = int(event.x_root - win_w * ratio)
            new_y = event.y_root - 20
            nova_geom = self._geom_restore.split("+")[0] + f"+{new_x}+{new_y}"
            # Aplicar tudo de uma vez — minimiza redesenhos intermediarios
            self.geometry(nova_geom)
            self.update_idletasks()
            self._maximized = False
            self.btn_max.configure(text="□")
            self._drag_x = event.x_root - self.winfo_x()
            self._drag_y = event.y_root - self.winfo_y()
            return
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

        # Nav usa pack para toda a barra — igual às outras abas do projeto
        nav.pack_propagate(False)

        def _ic(n, t):
            try:
                return ctk.CTkImage(Image.open(_resource_path(f"assets/{n}")), size=t)
            except:
                return None

        # Frame esquerdo: abas de navegação
        self.nav_frame = ctk.CTkFrame(nav, fg_color="transparent")
        self.nav_frame.pack(side="left", fill="y", padx=16, pady=9)

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

        # Botão Backup — lado direito, mesmo frame pai (nav), mesmo padrão visual
        img_backup = _ic("icon_backup.png", (24, 24))
        ctk.CTkButton(
            nav,
            text="  Backup",
            image=img_backup,
            compound="left",
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=12, weight="bold"),
            fg_color="transparent",
            text_color=COR_TEXT,
            hover_color="#EDF0F5",
            corner_radius=8,
            height=38,
            command=self._fazer_backup
        ).pack(side="right", padx=16, pady=9)

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
        self.after(50, self.deiconify)
        # Verificar alerta de backup ao iniciar
        self.after(1000, self._verificar_alerta_backup)

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

        def _atualizar_processos():
            if getattr(self, '_processos_desatualizados', True):
                processos.atualizar_lista_processos(self)
                self._processos_desatualizados = False

        rotas = {
            "Meus Clientes":  lambda: clientes.atualizar_lista_clientes(self),
            "Meus Processos": _atualizar_processos,
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

    # ── SYSTEM TRAY ───────────────────────────────────────────────────────────
    def _iniciar_tray(self):
        """Cria o ícone na bandeja do sistema (system tray)."""
        try:
            from PIL import Image as _Image
            import os as _os
            base = _os.path.dirname(_os.path.abspath(__file__))
            # Carregar ícone do tray
            ico_path = None
            for nome in ["archon_icon.ico", "archon_icon.png"]:
                p = _os.path.join(base, nome)
                if _os.path.exists(p):
                    ico_path = p
                    break
            if ico_path:
                img_tray = _Image.open(ico_path).resize((64, 64))
            else:
                # Ícone padrão navy com Z dourado se não encontrar arquivo
                img_tray = _Image.new("RGB", (64, 64), "#1C2E45")

            menu = pystray.Menu(
                TrayItem("Exibir / Ocultar", self._toggle_visibilidade, default=True),
                pystray.Menu.SEPARATOR,
                TrayItem("Fechar", self._fechar_definitivo)
            )
            self._tray_icon = pystray.Icon(
                "Archon", img_tray,
                "ARCHON — Advocacia Digital",
                menu
            )
            # Rodar em thread separada para não bloquear o mainloop
            t = threading.Thread(target=self._tray_icon.run, daemon=True)
            t.start()
        except Exception as e:
            print(f"Tray error: {e}")

    def _fechar_para_tray(self):
        """Minimiza para o tray ao clicar no X."""
        self.withdraw()          # esconde da tela e da taskbar
        if not hasattr(self, '_tray_icon') or self._tray_icon is None:
            self._iniciar_tray()

    def _toggle_visibilidade(self, icon=None, item=None):
        """Alterna exibir/ocultar a janela principal."""
        if self.winfo_viewable():
            self.after(0, self.withdraw)
        else:
            self.after(0, self._mostrar_janela)

    def _mostrar_janela(self):
        self.deiconify()
        self.lift()
        self.focus_force()

    def _fechar_definitivo(self, icon=None, item=None):
        """Fecha o app completamente (do menu do tray)."""
        try:
            if hasattr(self, '_tray_icon') and self._tray_icon:
                self._tray_icon.stop()
        except:
            pass
        self.after(0, self.destroy)

    # ── BACKUP ────────────────────────────────────────────────────────────────
    def _verificar_alerta_backup(self):
        """Adiciona notificação no sino se backup mensal não foi feito."""
        import calendar as _cal
        import os as _os
        from datetime import datetime as _dt
        hoje = _dt.now()
        ultimo = _cal.monthrange(hoje.year, hoje.month)[1]
        if hoje.day < ultimo - 2:
            return
        # Checar se já existe backup do mês
        try:
            base = _os.path.dirname(_os.path.abspath(__file__))
            backup_dir = _os.path.join(base, "backups")
            mes_str = hoje.strftime("%m-%Y")
            if _os.path.isdir(backup_dir):
                for f in _os.listdir(backup_dir):
                    if f.startswith("backup_") and mes_str in f:
                        return   # já tem backup
        except:
            pass
        # Adicionar ao sino se ainda não foi adicionado
        msg = f"⚠ Backup mensal recomendado! Mês: {hoje.strftime('%B/%Y')}"
        if not any(msg in str(n) for n in self.notificacoes):
            self.notificacoes.append({"msg": msg, "cor": "alerta"})
            from modules import layout
            layout.atualizar_sino(self)

    def _fazer_backup(self):
        from datetime import datetime as _dt
        import os as _os
        import shutil as _sh
        import openpyxl as _opxl
        import subprocess as _sp
        import platform as _pl
        import customtkinter as _ctk

        base_dir   = _os.path.dirname(_os.path.abspath(__file__))
        template   = _os.path.join(base_dir, "template.xlsx")
        backup_dir = _os.path.join(base_dir, "backups")

        # ── Modal de confirmação ───────────────────────────────────────────────
        modal_conf = _ctk.CTkToplevel(self)
        modal_conf.after(10, lambda m=modal_conf: _aplicar_icone(m))
        modal_conf.title("Backup")
        modal_conf.geometry("360x180")
        modal_conf.resizable(False, False)
        modal_conf.attributes("-topmost", True)
        modal_conf.grab_set()
        modal_conf.configure(fg_color="#F4F5F7")

        hdr = _ctk.CTkFrame(modal_conf, fg_color="#1C2E45", height=50, corner_radius=0)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        _ctk.CTkLabel(hdr, text="Fazer Backup",
                      font=_ctk.CTkFont(size=13, weight="bold"),
                      text_color="#FFFFFF").pack(pady=13)

        _ctk.CTkLabel(modal_conf,
                      text="Deseja realizar o backup agora? Um arquivo Excel será gerado na pasta backups.",
                      font=_ctk.CTkFont(size=12), text_color="#1A1A2E",
                      justify="center", wraplength=320).pack(pady=(16, 14))

        frame_btns = _ctk.CTkFrame(modal_conf, fg_color="transparent")
        frame_btns.pack()

        def _confirmar():
            modal_conf.destroy()
            self._executar_backup(base_dir, template, backup_dir)

        _ctk.CTkButton(frame_btns, text="Sim, fazer backup",
                       fg_color="#1C2E45", hover_color="#253A56",
                       text_color="#C9A84C", font=_ctk.CTkFont(weight="bold"),
                       width=140, height=34, corner_radius=8,
                       command=_confirmar).pack(side="left", padx=6)
        _ctk.CTkButton(frame_btns, text="Cancelar",
                       fg_color="#F4F5F7", hover_color="#E0E3E8",
                       text_color="#1A1A2E", border_width=1, border_color="#E0E3E8",
                       font=_ctk.CTkFont(weight="bold"),
                       width=100, height=34, corner_radius=8,
                       command=modal_conf.destroy).pack(side="left", padx=6)

    def _executar_backup(self, base_dir, template, backup_dir):
        from datetime import datetime as _dt
        import os as _os
        import shutil as _sh
        import openpyxl as _opxl
        import subprocess as _sp
        import platform as _pl

        _os.makedirs(backup_dir, exist_ok=True)

        if not _os.path.exists(template):
            self._backup_msg("template.xlsx não encontrado!", erro=True)
            return

        hoje     = _dt.now().strftime("%d-%m-%Y")
        destino  = _os.path.join(backup_dir, f"backup_{hoje}.xlsx")
        _sh.copy2(template, destino)

        # Buscar dados do banco
        try:
            from database.database import buscar_processos, buscar_clientes
            processos_db = buscar_processos()
        except Exception as e:
            self._backup_msg(f"Erro ao ler banco: {e}", erro=True)
            return

        wb = _opxl.load_workbook(destino)
        ws = wb.active

        # Mapa de status amigável
        def _status_acao(status_str):
            partes = [s.strip() for s in status_str.split(",") if s.strip()]
            for s in ["Em Andamento", "Concluído", "Cancelado"]:
                if s in partes:
                    return s
            return partes[0] if partes else ""

        def _cert(status_str):
            if "Certidão Emitida" in status_str:
                return "Emitida"
            if "Certidão Não-Emitida" in status_str:
                return "Não Emitida"
            return ""

        def _pagto(status_str):
            if "Pagos" in status_str:
                return "Pago"
            if "Não Pagos" in status_str:
                return "Não Pago"
            return ""

        # Preencher a partir da linha 23
        for i, p in enumerate(processos_db):
            row = 23 + i
            # p = (id, nome, num_acao, razao, atuacao, vara, tipo_v,
            #      pct, prov, conv, v_fixo, parc, parc_p, status, data, obs)
            id_p, nome, acao, razao, atuacao, vara, tipo_v,                 pct, prov, conv, v_fixo, parc, parc_p, status, data, obs = p

            ws.cell(row=row, column=1,  value=nome)

            # Célula do N° da Ação com comentário: observações + processos associados
            cell_acao = ws.cell(row=row, column=2, value=acao)
            linhas_comentario = []
            if obs:
                linhas_comentario.append(obs)
            try:
                from database.database import buscar_processos_associados
                assoc = buscar_processos_associados(acao)
                if assoc:
                    linhas_comentario.append("")
                    linhas_comentario.append("Processos Associados:")
                    for a in assoc:
                        linhas_comentario.append(f"  {a}")
            except:
                pass
            if linhas_comentario:
                from openpyxl.comments import Comment as _Comment
                texto_comentario = "\n".join(linhas_comentario)
                comentario = _Comment(texto_comentario, "Archon")
                comentario.width  = 300
                comentario.height = max(80, len(linhas_comentario) * 20)
                cell_acao.comment = comentario

            ws.cell(row=row, column=3,  value=vara)
            ws.cell(row=row, column=4,  value=razao)
            ws.cell(row=row, column=5,  value=atuacao)
            ws.cell(row=row, column=6,  value=pct if tipo_v == "Porcentagem" else "")
            ws.cell(row=row, column=7,  value=prov if tipo_v == "Porcentagem" else "")
            ws.cell(row=row, column=8,  value=conv if tipo_v == "Porcentagem" else "")
            ws.cell(row=row, column=9,  value=v_fixo if tipo_v == "Fixo" else "")
            ws.cell(row=row, column=10, value=parc if tipo_v == "Fixo" else "")
            ws.cell(row=row, column=11, value=parc_p if tipo_v == "Fixo" else "")
            ws.cell(row=row, column=12, value=_pagto(status))
            ws.cell(row=row, column=13, value=_status_acao(status))
            ws.cell(row=row, column=14, value=_cert(status))

        wb.save(destino)

        # Abrir a pasta backups maximizada no explorador
        try:
            if _pl.system() == "Windows":
                _sp.Popen(f'explorer /select,"{destino}"')
            elif _pl.system() == "Darwin":
                _sp.Popen(["open", backup_dir])
            else:
                _sp.Popen(["xdg-open", backup_dir])
        except:
            pass

        # Remover notificação de backup do sino
        mes_str = _dt.now().strftime("%B/%Y")
        self.notificacoes = [
            n for n in self.notificacoes
            if not (isinstance(n, dict) and "Backup mensal" in n.get("msg", ""))
            and not (isinstance(n, str) and "Backup mensal" in n)
        ]
        from modules import layout as _layout
        _layout.atualizar_sino(self)

        # Atualizar dashboard para remover o banner
        try:
            from modules import dashboard as _dash
            _dash.criar_dashboard(self, self.frames_abas["Dashboard"])
        except:
            pass

        self._backup_msg(f"Backup realizado com sucesso! Arquivo: backup_{hoje}.xlsx | Pasta: backups/")

    def _backup_msg(self, mensagem, erro=False):
        import customtkinter as _ctk
        modal = _ctk.CTkToplevel(self)
        modal.after(10, lambda m=modal: _aplicar_icone(m))
        modal.title("Backup")
        modal.geometry("380x180")
        modal.resizable(False, False)
        modal.attributes("-topmost", True)
        modal.grab_set()
        modal.configure(fg_color="#F4F5F7")

        cor_hdr = "#B22222" if erro else "#1C2E45"
        hdr = _ctk.CTkFrame(modal, fg_color=cor_hdr, height=50, corner_radius=0)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        _ctk.CTkLabel(hdr,
                      text="Erro no Backup" if erro else "Backup Concluído",
                      font=_ctk.CTkFont(size=13, weight="bold"),
                      text_color="#FFFFFF").pack(pady=13)

        _ctk.CTkLabel(modal, text=mensagem,
                      font=_ctk.CTkFont(size=12),
                      text_color="#1A1A2E",
                      justify="center",
                      wraplength=340).pack(pady=(16, 12))

        _ctk.CTkButton(modal, text="OK",
                       fg_color="#1C2E45", hover_color="#253A56",
                       text_color="#C9A84C", font=_ctk.CTkFont(weight="bold"),
                       width=100, height=34, corner_radius=8,
                       command=modal.destroy).pack()

def _garantir_instancia_unica():
    """Cria um Mutex nomeado. Se já existir, traz a janela existente para frente."""
    MUTEX_NAME = "ArchonAdvocaciaDigital_Zenon_SingleInstance"
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, MUTEX_NAME)
    erro  = ctypes.windll.kernel32.GetLastError()

    if erro == 183:  # ERROR_ALREADY_EXISTS
        hwnd = ctypes.windll.user32.FindWindowW(None, "Archon")
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 9)   # SW_RESTORE
            ctypes.windll.user32.SetForegroundWindow(hwnd)
        sys.exit(0)

    return mutex

    
# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":


    _mutex = _garantir_instancia_unica()
    
    criar_tabelas()
    criar_tabela_agenda()

    # 1. Splash roda e fecha completamente (Tk puro, sem resíduos)
    _mostrar_splash()

    # 2. App abre como CTk raiz — aparece na taskbar, tem ícone, minimiza certo
    app = App()
    app.mainloop()