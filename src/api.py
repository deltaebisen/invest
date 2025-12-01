"""Stock API Server"""

from datetime import date

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.database import get_db
from src.models import Stock, StockPrice

app = FastAPI(
    title="Japan Stock API",
    description="日本株の株価データAPI",
    version="1.0.0",
)

# CORS設定（開発時は全許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class StockResponse(BaseModel):
    """銘柄レスポンス"""

    code: str
    name: str
    market: str | None
    sector: str | None

    class Config:
        from_attributes = True


class StockPriceResponse(BaseModel):
    """株価レスポンス"""

    code: str
    trade_date: date
    open: float | None
    high: float | None
    low: float | None
    close: float | None
    volume: int | None
    adjusted_close: float | None

    class Config:
        from_attributes = True


class StockListResponse(BaseModel):
    """銘柄一覧レスポンス"""

    total: int
    items: list[StockResponse]


class StockPriceListResponse(BaseModel):
    """株価一覧レスポンス"""

    total: int
    items: list[StockPriceResponse]


@app.get("/health")
def health_check():
    """ヘルスチェック"""
    return {"status": "ok"}


@app.get("/stocks", response_model=StockListResponse)
def get_stocks(
    market: str | None = Query(None, description="市場区分でフィルタ"),
    sector: str | None = Query(None, description="業種でフィルタ"),
    limit: int = Query(100, ge=1, le=1000, description="取得件数"),
    offset: int = Query(0, ge=0, description="オフセット"),
    db: Session = Depends(get_db),
):
    """銘柄一覧を取得"""
    query = db.query(Stock)

    if market:
        query = query.filter(Stock.market == market)
    if sector:
        query = query.filter(Stock.sector == sector)

    total = query.count()
    items = query.order_by(Stock.code).offset(offset).limit(limit).all()

    return StockListResponse(total=total, items=items)


@app.get("/stocks/{code}", response_model=StockResponse)
def get_stock(code: str, db: Session = Depends(get_db)):
    """銘柄詳細を取得"""
    stock = db.query(Stock).filter(Stock.code == code).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    return stock


@app.get("/stocks/{code}/prices", response_model=StockPriceListResponse)
def get_stock_prices(
    code: str,
    start_date: date | None = Query(None, description="開始日"),
    end_date: date | None = Query(None, description="終了日"),
    limit: int = Query(100, ge=1, le=1000, description="取得件数"),
    offset: int = Query(0, ge=0, description="オフセット"),
    db: Session = Depends(get_db),
):
    """銘柄の株価履歴を取得"""
    # 銘柄存在チェック
    stock = db.query(Stock).filter(Stock.code == code).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")

    query = db.query(StockPrice).filter(StockPrice.code == code)

    if start_date:
        query = query.filter(StockPrice.trade_date >= start_date)
    if end_date:
        query = query.filter(StockPrice.trade_date <= end_date)

    total = query.count()
    items = query.order_by(StockPrice.trade_date.desc()).offset(offset).limit(limit).all()

    return StockPriceListResponse(total=total, items=items)


@app.get("/prices/latest", response_model=StockPriceListResponse)
def get_latest_prices(
    codes: str | None = Query(None, description="銘柄コード（カンマ区切り）"),
    limit: int = Query(100, ge=1, le=1000, description="取得件数"),
    offset: int = Query(0, ge=0, description="オフセット"),
    db: Session = Depends(get_db),
):
    """最新の株価を取得"""
    # 最新日付を取得
    latest_date = db.query(func.max(StockPrice.trade_date)).scalar()
    if not latest_date:
        return StockPriceListResponse(total=0, items=[])

    query = db.query(StockPrice).filter(StockPrice.trade_date == latest_date)

    if codes:
        code_list = [c.strip() for c in codes.split(",")]
        query = query.filter(StockPrice.code.in_(code_list))

    total = query.count()
    items = query.order_by(StockPrice.code).offset(offset).limit(limit).all()

    return StockPriceListResponse(total=total, items=items)


@app.get("/markets")
def get_markets(db: Session = Depends(get_db)):
    """市場区分の一覧を取得"""
    markets = db.query(Stock.market).distinct().filter(Stock.market.isnot(None)).all()
    return {"markets": [m[0] for m in markets]}


@app.get("/sectors")
def get_sectors(db: Session = Depends(get_db)):
    """業種の一覧を取得"""
    sectors = db.query(Stock.sector).distinct().filter(Stock.sector.isnot(None)).all()
    return {"sectors": [s[0] for s in sectors]}
