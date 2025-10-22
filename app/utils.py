from __future__ import annotations
from typing import Optional
import math
import numpy as np
from .config import BANKROLL_BASE_PCT, BANKROLL_your_psychology_SCALE

try:
    import yfinance as yf  # type: ignore

    _HAS_YF = True
except Exception:
    _HAS_YF = False


# --- your_psychology & bankroll ---
def your_psychology_score(sleep_hours: float, exercise_minutes: int) -> tuple[float, str, str, str]:
    """
    Compute risk factor using exponential penalty on deficits from targets.

    - Sleep target: 7h (5–7h ramp).
    - Exercise target: 90m (60–90m ramp).
    - Weighted: sleep 65%, exercise 35%.
    - Output f scaled into [0.2, 1.0].
    """

    # --- Sleep score with richer notes ---
    if sleep_hours >= 6:
        s_note = "Well-rested"
    elif 4 <= sleep_hours < 6:
        s_note = "Light rest"
    else:
        s_note = "Sleep-deprived"

    # --- Exercise score with richer notes ---
    if exercise_minutes < 20:
        e_note = "Inactive"
    elif 20 <= exercise_minutes < 40:
        e_note = "Moderate activity"
    else:
        e_note = "High activity"

    sleep_level = s_note
    exercise_level = e_note

    # --- Risk matrix (descriptions tuned) ---
    risk_matrix = {
        "Sleep-deprived": {
            "Inactive": (
                "🔴 High Risk",
                "Severe fatigue and inactivity — judgment, focus, and discipline highly compromised.",
            ),
            "Moderate activity": (
                "🔴 High Risk",
                "Exercise provides some balance, but lack of sleep dominates — high chance of costly mistakes.",
            ),
            "High activity": (
                "🔴 High Risk",
                "Strong fitness helps, but poor rest still limits focus and reaction time.",
            ),
        },
        "Light rest": {
            "Inactive": ("🔴 High Risk", "Partial rest + inactivity → sluggish responses, reactive decision-making."),
            "Moderate activity": (
                "🟠 Moderate Risk",
                "Fair balance, but not peak performance — reduce trade size and frequency.",
            ),
            "High activity": ("🟡 Caution", "Reasonable discipline, but endurance may fade in longer sessions."),
        },
        "Well-rested": {
            "Inactive": ("🟠 Moderate Risk", "Mind is sharp, but low fitness = reduced stamina in volatile markets."),
            "Moderate activity": (
                "🟡 Caution",
                "Balanced state; trade cautiously with discipline, avoid overconfidence.",
            ),
            "High activity": ("🟢 Optimal", "Peak focus, strong discipline, and endurance — ideal trading state."),
        },
    }

    # --- Trading guidance updated ---
    trading_guidance = {
        "🟢 Optimal": "Conditions are excellent — trade normally within your risk rules.",
        "🟡 Caution": "Conditions are decent — reduce position size slightly and monitor stamina.",
        "🟠 Moderate Risk": "Conditions are mixed — reduce trade frequency and size; stay defensive.",
        "🟠 Elevated Risk": "Conditions are imbalanced — fitness helps, but lack of rest makes errors likely.",
        "🔴 High Risk": "Avoid trading — high probability of emotional or impulsive mistakes.",
    }

    # --- Exponential penalty fusion ---
    def fuse_exp_penalty() -> float:
        # Deficits normalized: 0 = no deficit, 1 = serious deficit
        ds = max(0.0, min(1.0, (6.0 - sleep_hours) / 2.0))
        de = max(0.0, min(1.0, (40.0 - exercise_minutes) / 20.0))
        w_s, w_e = 0.95, 0.05
        alpha = 3.0
        score = math.exp(-alpha * (w_s * ds + w_e * de))
        return 0.2 + 0.8 * score

    f = fuse_exp_penalty()

    # --- Lookup alert/guidance ---
    try:
        alert, description = risk_matrix[sleep_level][exercise_level]
        guidance = trading_guidance.get(alert, "")
    except KeyError:
        alert, description, guidance = "❓", "Unexpected combination.", ""

    return (f, f"{description} (sleep={sleep_level}, exercise={exercise_level}, risk scale x{f:.2f})", alert, guidance)


def compute_dynamic_bankroll(total_value: float, h_factor: float) -> tuple[float, float]:
    """
    Compute bankroll (amount, pct of total_value).
    - Start from BANKROLL_BASE_PCT
    - Optionally scale by your_psychology factor
    - Clamp to [BANKROLL_MIN_PCT, BANKROLL_MAX_PCT]
    """
    pct = BANKROLL_BASE_PCT
    if BANKROLL_your_psychology_SCALE:
        pct = pct * h_factor
    # pct = max(BANKROLL_MIN_PCT, min(BANKROLL_MAX_PCT, pct))
    amount = total_value * pct
    return amount, pct


# --- Market data & ATR ---


def fetch_price_and_atr(symbol: str, lookback: int) -> tuple[Optional[float], Optional[float]]:
    if not _HAS_YF:
        return None, None
    try:
        hist = yf.Ticker(symbol).history(period="6mo")
        if hist.empty:
            return None, None
        highs = hist["High"].to_numpy()
        lows = hist["Low"].to_numpy()
        closes = hist["Close"].to_numpy()
        prev_close = np.roll(closes, 1)
        prev_close[0] = closes[0]
        tr = np.maximum(highs - lows, np.maximum(np.abs(highs - prev_close), np.abs(lows - prev_close)))
        if len(tr) < lookback:
            return float(closes[-1]), None
        atr = float(np.mean(tr[-lookback:]))
        return float(closes[-1]), atr
    except Exception:
        return None, None
