; ══════════════════════════════════════════════════════════════════════════════
;  ARCHON
;  Script de instalação — Inno Setup 6+
;  Developed by Guilherme Teles (Zenon)
;
;  ANTES DE COMPILAR:
;    1. Rode no terminal: pyinstaller Archon.spec
;    2. Confirme que existe a pasta dist\Archon\ com o Archon.exe
;    3. Compile este .iss no Inno Setup (F9)
;    4. O instalador final fica em Output\Archon_Setup.exe
; ══════════════════════════════════════════════════════════════════════════════

[Setup]
AppName=Archon
AppVersion=1.0
AppVerName=Archon 1.00.0
AppPublisher=Guilherme Teles
AppCopyright=Copyright (C) 2026 Guilherme Teles

DefaultDirName={autopf}\Archon
DefaultGroupName=Archon

OutputDir=Output
OutputBaseFilename=Archon_Setup

SetupIconFile=archon_icon.ico
UninstallDisplayIcon={app}\Archon.exe

Compression=lzma
SolidCompression=yes

PrivilegesRequired=admin

DisableWelcomePage=no
DisableDirPage=no
DisableProgramGroupPage=yes
ShowLanguageDialog=no


[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"


[Tasks]
Name: "desktopicon"; \
  Description: "Criar atalho na Área de Trabalho"; \
  GroupDescription: "Ícones adicionais:"

Name: "startupwin"; \
  Description: "Iniciar automaticamente com o Windows (como Administrador)"; \
  GroupDescription: "Opções de inicialização:"


[Files]
Source: "dist\Archon\*"; \
  DestDir: "{app}"; \
  Flags: ignoreversion recursesubdirs createallsubdirs


[Icons]
Name: "{group}\Archon"; \
  Filename: "{app}\Archon.exe"

Name: "{commondesktop}\Archon"; \
  Filename: "{app}\Archon.exe"; \
  Tasks: desktopicon

Name: "{group}\Desinstalar Archon"; \
  Filename: "{uninstallexe}"


[Run]
Filename: "{app}\Archon.exe"; \
  Description: "Executar Archon agora"; \
  Flags: nowait postinstall skipifsilent runasoriginaluser


[UninstallRun]
Filename: "schtasks"; \
  Parameters: "/Delete /TN ""Archon_Startup"" /F"; \
  Flags: runhidden; \
  RunOnceId: "RemoveArchonTask"


[Code]

procedure CriarTarefaAgendada();
var
  ExePath: String;
  ResultCode: Integer;
  Params: String;
begin
  ExePath := ExpandConstant('{app}\Archon.exe');
  Params := '/Create /F /SC ONLOGON /RL HIGHEST /TN "Archon_Startup" /TR "' + ExePath + '"';
  Exec('schtasks', Params, '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;

procedure RemoverTarefaAgendada();
var
  ResultCode: Integer;
begin
  Exec('schtasks', '/Delete /TN "Archon_Startup" /F', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    if IsTaskSelected('startupwin') then
      CriarTarefaAgendada();
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
    RemoverTarefaAgendada();
end;
