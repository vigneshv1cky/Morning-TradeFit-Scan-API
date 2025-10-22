from __future__ import annotations
from typing import List, Optional
from sqlalchemy.orm import Session
from .models import ScanRecord


def create_scan(db: Session, rec: ScanRecord) -> ScanRecord:
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


def list_scans(db: Session, limit: int = 50, offset: int = 0, symbol: Optional[str] = None) -> List[ScanRecord]:
    q = db.query(ScanRecord).order_by(ScanRecord.id.desc())
    if symbol:
        q = q.filter(ScanRecord.symbol == symbol.upper())
    return q.offset(offset).limit(limit).all()


def get_scan_by_id(db: Session, scan_id: int) -> Optional[ScanRecord]:
    return db.get(ScanRecord, scan_id)
