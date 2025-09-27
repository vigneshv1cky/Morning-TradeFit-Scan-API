from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ScanInput(BaseModel):
    # Minimal inputs; bankroll & cap are computed internally from config/policy
    total_value: float = Field(..., gt=0)
    sleep_hours: float = Field(..., ge=0, le=12)
    exercise_minutes: int = Field(..., ge=0, le=120)
    trade_symbol: str

    # risk & stop settings
    # risk_per_trade_pct: Optional[float] = Field(None, gt=0.0, le=0.05)
    # stop_loss_pct: Optional[float] = Field(None, gt=0.0, le=0.005)


class your_psychologyBlock(BaseModel):
    sleep_hours: float
    exercise_minutes: int
    factor: float
    note: str
    alert: str
    guidance: str


class BankrollBlock(BaseModel):
    mode: str
    amount: float
    pct_of_total: float


class RiskBlock(BaseModel):
    risk_per_trade_pct: float
    risk_per_trade_usd: float
    stop_loss_pct: float


class PositionBlock(BaseModel):
    entry_price: float
    normal_pos_size: float
    stop_loss_at: float
    risk_per_share: float


class ScanOutput(BaseModel):
    record_id: Optional[int] = None
    symbol: str
    timestamp_utc: str
    your_psychology: your_psychologyBlock
    bankroll: BankrollBlock
    risk: RiskBlock
    position: PositionBlock


class ScanRow(BaseModel):
    id: int
    created_at: datetime
    symbol: str
    risk_per_trade: float
    stop_loss_used_pct: float
