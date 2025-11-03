# EmotionalShieldAI API

FastAPI service that computes trading risk guidance from sleep/exercise inputs, sizes positions using bankroll policy, and persists scans to SQLite. Includes optional price/ATR lookup via `yfinance`.

---

## 1) Project structure (key files)

```

EmotionalShieldAI/
├── .env
├── .git/
├── .gitignore
├── README.md
├── TradeFit.postman_collection.json
├── __pycache__/
├── app/
│   ├── __init__.py
│   ├── __pycache__/
│   ├── config.py
│   ├── crud.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   └── utils.py
├── compose.yml
├── env_emotionalshieldai/
│   ├── .gitignore
│   ├── bin/
│   ├── include/
│   ├── lib/
│   └── pyvenv.cfg
├── requirements.txt
├── run.sh
├── sqlite_to_mysql.md
└── tradefit.db

```

> **Important:** The app calls `load_dotenv(dotenv_path=".env")`, so **run from the project root** where the `.env` file lives.

---

## 2) Requirements

* Python 3.10+ (recommended)
* SQLite (bundled with Python)

---

## 3) Setup

### Mac/Linux (bash or zsh)

```bash
# 1) Clone / unzip the project, then cd into the project root
cd EmotionalShieldAI

# 2) Create & activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 3) Install dependencies
pip install -r requirements.txt

# 4) Create .env (see template below)
cp .env.example .env  # if present, else create manually
```

### Windows (PowerShell)

```powershell
# 1) cd into the project root
cd EmotionalShieldAI

# 2) Create & activate a virtual environment
python -m venv venv
venv\Scripts\Activate

# 3) Install dependencies
pip install -r requirements.txt

# 4) Create .env (see template below)
ni .env  # creates an empty .env; then edit it
```

---

## 4) Environment variables (.env)

**Create a `.env` file in the project root**. Safe defaults are strongly recommended. Example:

```ini
# Database
DATABASE_URL=sqlite:///tradefit.db

# Bankroll policy
# Fraction of total account used as bankroll (0.25 = 25%)
BANKROLL_BASE_PCT=0.25
# Whether to scale bankroll by the health/psychology factor
BANKROLL_your_psychology_SCALE=true

# Risk policy (as fractions 0..1)
# Portion of bankroll risked per trade (e.g., 0.01 = 1%)
risk_per_trade_pct=0.01
# Stop loss size relative to entry (e.g., 0.01 = 1%)
stop_loss_pct=0.01
```

> **Why this matters:** If `.env` is missing or variables are unset, earlier versions defaulted to `1.0` for some settings, which can cause invalid outputs (e.g., `stop_loss_at = 0.0`). Always provide sane values here.

---

## 5) Run the API

### Start the server (development)

```bash
# From project root, with venv active
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open docs at: `http://localhost:8000/docs`

> On Windows, if `uvicorn` isn’t found, try `python -m uvicorn app.main:app --reload`.

---

## 6) Database

* Default DB is SQLite at `tradefit.db` in the project root.
* Tables are auto-created by `Base.metadata.create_all(bind=engine)` on app startup.
* To change DB (e.g., Postgres), set `DATABASE_URL` accordingly.

**Examples**

* Postgres: `DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/dbname`
* MySQL: `DATABASE_URL=mysql+pymysql://user:pass@host:3306/dbname`

---

## 7) License

Add your license of choice (MIT/Apache-2.0/etc.).
