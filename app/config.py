from __future__ import annotations
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///tradefit.db")


# --- Bankroll policy (internal only) ---
def _get_bool(name: str, default: bool = "true") -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.strip().lower() in {"1", "true", "yes", "y"}


def get_env_float(name: str, default: float = 1) -> float:
    v = os.getenv(name)
    if v is None:
        if default is not None:
            return default
        raise RuntimeError(f"Missing required environment variable: {name}")
    return float(v)


BANKROLL_your_psychology_SCALE = _get_bool("BANKROLL_your_psychology_SCALE")
BANKROLL_BASE_PCT = get_env_float("BANKROLL_BASE_PCT")
risk_per_trade_pct = get_env_float("risk_per_trade_pct")
stop_loss_pct = get_env_float("stop_loss_pct")
