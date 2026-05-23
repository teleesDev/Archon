# ⚖️ ARCHON — Advocacia Digital

> **Developed by Guilherme Teles · Zenon**
> Sistema de gestão jurídica para advogados autônomos e pequenos escritórios.

---

## 📋 Sobre o Projeto

O **Archon** é um aplicativo desktop completo para gestão da advocacia, construído com Python e CustomTkinter. Desenvolvido com identidade visual própria — azul marinho `#1C2E45` e dourado `#C9A84C` — o sistema oferece uma interface moderna, fluida e sem a barra nativa do Windows.

O nome **Archon** vem do grego antigo: magistrado/governante. O monograma **Z** representa a marca **Zenon**, desenvolvedor do sistema.

---

## 🚀 Funcionalidades

### 📁 Meus Clientes
- Cadastro completo de Pessoa Física e Pessoa Jurídica
- Campos: nome, CPF/CNPJ, RG, telefone, e-mail, endereço, observações
- Busca em tempo real por nome, CPF ou CNPJ
- Filtro por tipo de pessoa (Todos / PF / PJ)
- Visualização expandida com processos vinculados
- Redirecionamento direto para o processo do cliente

### 📂 Meus Processos
- Cadastro completo de processos jurídicos
- Configuração de valores: Porcentagem (%), Fixo/Parcelado ou Pro Bono
- Cálculo automático de conversão de honorários
- Sistema de status múltiplos por checklist:
  - Em Andamento / Concluído
  - Não Pagos / Pagos
  - Certidão Não-Emitida / Certidão Emitida
  - Cancelado
- Processos Associados (vínculos entre processos relacionados)
- Integração automática com Financeiro ao marcar como Pago
- Ícone dinâmico de estratégia vinculada por processo (criar/editar)

### 🏛️ Estratégias
- Planos estratégicos vinculados a processos
- Título, descrição, checklist e nível de urgência (Baixa / Moderada / Alta)
- Sidebar com lista de estratégias e seleção visual destacada
- Um processo aceita apenas uma estratégia vinculada
- Acesso direto da lista de processos via ícone dedicado

### 💰 Financeiro
- Lançamentos de Receita (+) e Despesa (-)
- Dropdown com texto colorido (verde/vermelho) e seta sempre branca
- Integração automática com processos pagos
- Filtros por mês e ano (dropdowns navy)
- Histórico com faixa colorida: manual=preto, PF=azul, PJ=dourado
- Edição de data de lançamento
- Reversão automática ao excluir lançamento vinculado a processo

### 📅 Agenda / Calendário
- Calendário mensal visual completo
- Dois tipos de evento: Compromisso (azul) e Data Importante (vermelho)
- Exibição de feriados nacionais, estaduais e comemorativas
- Máximo 1 barra de cada tipo por célula + contador de extras
- Modal moderno com cabeçalho navy para adicionar eventos
- Alerta no Dashboard para eventos do dia

### 📊 Dashboard
- Controle de Pagamentos (barras de progresso)
- Distribuição de Processos (gráfico de barras com separadores)
- Controle Financeiro (Faturamento Bruto, Saídas/Despesas, Saldo em Caixa)
- Alerta de agenda do dia
- Banner de alerta de backup mensal (últimos 3 dias do mês)

### 💾 Backup
- Botão na navbar com ícone `icon_backup.png`
- Modal de confirmação antes de gerar
- Geração de planilha Excel a partir do `template.xlsx`
- Preenchimento automático a partir da linha 23:
  - A: Nome Cliente | B: N° Ação (com comentário: obs + processos associados)
  - C: Vara | D: Razão | E: Atuação | F: % | G: Proveito | H: Conversão
  - I: Valor Fixo | J: Parcelas | K: Parcelas Pagas | L: Pagamento
  - M: Status Ação | N: Certidão
- Arquivo salvo em `backups/backup_DD-MM-YYYY.xlsx`
- Abre o Explorer no arquivo gerado automaticamente
- Alerta mensal no sino e no Dashboard nos últimos 3 dias do mês
- Ao fazer backup, alerta some automaticamente

### 🔔 System Tray
- Clicar no **X** minimiza para a bandeja do sistema (não fecha)
- Ícone na bandeja com menu de contexto:
  - **Exibir / Ocultar** — alterna visibilidade da janela
  - **Fechar** — encerra o programa completamente

---

## 🗂️ Estrutura do Projeto

```
Projeto Alexandre/
├── main.py                  # Ponto de entrada, janela principal, backup, tray
├── archon_icon.ico          # Ícone do aplicativo (taskbar, modais, instalador)
├── template.xlsx            # Template Excel para backup
├── requirements.txt         # Dependências Python
├── Archon.spec              # Configuração do PyInstaller
├── Archon_Setup.iss         # Script do instalador (Inno Setup)
│
├── database.py              # SQLite — todas as funções de banco de dados
│
├── modules/
│   ├── layout.py            # Titlebar, sino de notificações
│   ├── dashboard.py         # Tela principal com métricas e alertas
│   ├── clientes.py          # Gestão de clientes PF e PJ
│   ├── processos.py         # Gestão de processos jurídicos
│   ├── financeiro.py        # Controle financeiro
│   ├── estrategias.py       # Planos estratégicos
│   ├── calendario.py        # Agenda e calendário mensal
│   └── utils.py             # Formatadores (CPF, CNPJ, telefone, data)
│
├── assets/                  # Ícones PNG da interface
├── styles/
│   └── theme_premium.json   # Tema CustomTkinter
└── backups/                 # Backups Excel gerados (criado automaticamente)
```

---

## ⚙️ Instalação (modo desenvolvedor)

### 1. Pré-requisitos
- Python 3.10 ou superior (testado em 3.14)
- Windows 10/11

### 2. Instalar dependências
```bash
pip install -r requirements.txt
```

### 3. Executar
```bash
python main.py
```

---

## 📦 Distribuição (gerar instalador)

### 1. Gerar o executável
```bash
pip install pyinstaller
pyinstaller Archon.spec
```

### 2. Compilar o instalador
Abrir `Archon_Setup.iss` no **Inno Setup 6+** e pressionar **F9**.
O instalador `Output\Archon_Setup.exe` estará pronto para distribuição.

### O instalador inclui:
- Escolha da pasta de instalação
- Atalho na Área de Trabalho (opcional)
- Iniciar automaticamente com o Windows como Administrador (via Task Scheduler)
- Desinstalação limpa (remove tarefa agendada automaticamente)

---

## 🎨 Identidade Visual

| Elemento        | Cor       | Uso                           |
|-----------------|-----------|-------------------------------|
| Navy Principal  | `#1C2E45` | Titlebar, botões, cabeçalhos  |
| Dourado         | `#C9A84C` | Destaques, ações primárias    |
| Fundo Geral     | `#F4F5F7` | Background das abas           |
| Card            | `#FFFFFF` | Cards e painéis               |
| Borda           | `#E0E3E8` | Separadores e bordas          |
| Texto Principal | `#1A1A2E` | Labels e títulos              |
| Muted           | `#7A8499` | Textos secundários            |
| Verde           | `#1A7A4A` | Receitas, positivo            |
| Vermelho        | `#B22222` | Despesas, exclusões, alertas  |

---

## 🗄️ Banco de Dados

SQLite local (`advocacia.db`) gerado automaticamente na primeira execução, na mesma pasta do executável.

**Tabelas:**
- `clientes` — dados cadastrais de PF e PJ
- `processos` — processos jurídicos com todos os campos
- `associacoes` — vínculos entre processos
- `transacoes` — lançamentos financeiros
- `estrategias` — planos estratégicos vinculados a processos
- `agenda` — eventos e compromissos do calendário

---

## 📦 Dependências

| Pacote          | Versão mín. | Uso                               |
|-----------------|-------------|-----------------------------------|
| `customtkinter` | 5.2.2       | Interface gráfica moderna         |
| `Pillow`        | 10.0.0      | Imagens, ícones, logo Z           |
| `openpyxl`      | 3.1.0       | Geração de backup Excel           |
| `pystray`       | 0.19.0      | Ícone na bandeja do sistema       |
| `darkdetect`    | 0.8.0       | Detecção de tema do sistema       |
| `packaging`     | 23.0        | Dependência do customtkinter      |

---

## 👤 Autor

**Guilherme Teles** · Zenon
Sistema desenvolvido para uso profissional na advocacia.

---

*ARCHON — Do grego antigo: magistrado, governante. Autoridade. Proteção.*
