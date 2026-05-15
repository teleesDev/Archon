# ⚖️ Advocacia Digital - Sistema de Gestão Jurídica

Um sistema de gestão de escritórios de advocacia moderno, modular e autossuficiente, desenvolvido em Python com interface gráfica **CustomTkinter** e banco de dados **SQLite**.

## 🚀 Funcionalidades Principais
* **Dashboard Interativo:** Visão panorâmica de processos e saúde financeira do escritório.
* **Gestão de Clientes (PF/PJ):** Cadastro completo com divisão inteligente de formulários e status de matriz/filial.
* **Gestão de Processos:** Controle de honorários (percentuais ou fixos/parcelados), conversão automática de valores e checklist de status nas abas.
* **Módulo Financeiro:** Fluxo de caixa com reversão inteligente (se um honorário for apagado, o processo volta automaticamente para "Não Pago").
* **Agenda Inteligente:** Calendário interativo com cálculo automático de feriados nacionais e datas importantes.

## 📂 Arquitetura do Projeto (Modular)
O sistema foi construído visando escalabilidade e fácil manutenção:

Projeto_Advocacia/
├── main.py                 # Ponto de entrada (O Maestro)
├── requirements.txt        # Dependências do projeto
├── README.md               # Documentação
├── database/
│   └── database.py         # Motor SQL e regras de negócio
├── modules/
│   ├── __init__.py         # Inicializador do pacote
│   ├── utils.py            # Máscaras unificadas (CPF, CNPJ, Data, CNJ)
│   ├── layout.py           # Header e Central de Notificações
│   ├── dashboard.py        # Gráficos e indicadores
│   ├── clientes.py         # Interface de Clientes
│   ├── processos.py        # Interface de Processos
│   ├── financeiro.py       # Interface Financeira
│   └── calendario.py       # Lógica do Calendário e Feriados
├── assets/                 # (Opcional) Ícones e logotipos
└── styles/                 # (Opcional) Temas JSON customizados


## 🛠️ Instalação e Execução

1. **Clone o repositório ou baixe a pasta:**
   Certifique-se de ter o Python 3.10+ instalado.

2. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt