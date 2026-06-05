```
   _____                                      __  
  / ___/_________  ________  ____  ____ _____/ /
  \__ \/ ___/ __ \/ ___/ _ \/ __ \/ __ `/ __  / 
 ___/ / /__/ /_/ / /  /  __/ /_/ / /_/ / /_/ /  
/____/\___/\____/_/   \___/ .___/\__,_/\__,_/   
                          /_/                     by Catmaitachi
```

<p align="center">
    <img src="https://img.shields.io/badge/python-3.11%2B-blue?logo=python" alt="Python" />
    <img src="https://img.shields.io/badge/pandas-2.x-150458?logo=pandas" alt="Pandas" />
    <img src="https://img.shields.io/badge/IGDB-API-9147FF?logo=twitch" alt="IGDB API" />
    <img src="https://img.shields.io/badge/Power%20BI-visualização-F2C811?logo=powerbi" alt="Power BI" />
</p>

Scorepad é uma plataforma de análise preditiva de jogos que coleta dados públicos sobre próximos lançamentos e calcula a **chance de sucesso** de cada um com base no histórico da desenvolvedora e no engajamento da comunidade. O resultado é exportado como CSV pronto para consumo no Power BI.

---

## Pré-requisitos

- [Python 3.11+](https://www.python.org/downloads/)
- Conta de desenvolvedor na [Twitch](https://dev.twitch.tv/console) para acessar a IGDB API

## Instalação

1. **Clone o repositório:**
   ```sh
   git clone https://github.com/catmaitachi/Scorepad.git
   cd Scorepad
   ```

2. **Crie e ative o ambiente virtual:**
   ```sh
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   # source .venv/bin/activate  # Linux / macOS
   ```

3. **Instale as dependências:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Configure as credenciais:**
   ```sh
   cp .env.example .env
   ```
   Edite o `.env` com seu `Client ID` e `Client Secret` obtidos em [dev.twitch.tv/console](https://dev.twitch.tv/console).

---

## Uso

### Listar próximos lançamentos

```sh
# Padrão: top 50 ordenados por hype
python main.py list

# Ordenado por data de lançamento, 20 por página
python main.py list --order date --limit 20

# Segunda página
python main.py list --order hype --limit 50 --page 2
```

### Buscar um jogo específico

```sh
# Exibe resultado no console
python main.py search "Assassin's Creed"

# Exporta também para output/search_result.csv
python main.py search "Grand Theft Auto" --export
```

O modo `list` sempre exporta para `output/predictions.csv`, pronto para ser conectado ao Power BI.

---

## Estrutura do Projeto

```
Scorepad/
├── main.py                       # Entry point — modos list e search
├── config.py                     # Configuração centralizada (pesos, thresholds, filtros)
├── .env.example                  # Template de credenciais
├── requirements.txt
│
├── scorepad/                     # Pacote principal
│   ├── igdb_client.py            # Autenticação OAuth e queries à IGDB
│   ├── processor.py              # Normalização de dados e perfis de estúdio
│   ├── scorer.py                 # Agregação de signals com pesos
│   └── signals/
│       ├── base.py               # GameContext · Signal · SignalResult
│       ├── studio.py             # StudioHistorySignal
│       ├── hype_franchise.py     # HypeFranchiseSignal (recência + hype)
│       ├── projects.py           # SimultaneousProjectsSignal
│       └── future.py             # Stubs: MarketValueSignal · GPTWSignal
│
├── data/
│   ├── raw/                      # JSONs brutos da IGDB
│   └── processed/                # CSVs intermediários
│
└── output/
    ├── predictions.csv           # Resultado do list → Power BI
    └── search_result.csv         # Resultado do search --export
```
