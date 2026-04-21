from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

NAMING_CONVENTION: dict[str, str] = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Shared SQLAlchemy declarative base for CopySnipIn table metadata."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)


JsonObject = dict[str, Any]


class Wallet(Base):
    """Canonical wallet identity used by scanner, tracker, and simulation state."""

    __tablename__ = "wallets"
    __table_args__ = (
        UniqueConstraint("address", name="uq_wallets_address"),
        Index("ix_wallets_status", "status"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    address: Mapped[str] = mapped_column(String(128), nullable=False)
    label: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    pinned: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    blocked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class ScannerRun(Base):
    """Durable record of a scanner cycle and its aggregate outcome."""

    __tablename__ = "scanner_runs"
    __table_args__ = (UniqueConstraint("run_key", name="uq_scanner_runs_run_key"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    run_key: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    processed_wallets: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    qualified_wallets: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_message: Mapped[str | None] = mapped_column(Text)
    raw_payload: Mapped[JsonObject | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class QualificationEvidence(Base):
    """Per-wallet scanner evidence and threshold decision for a scanner run."""

    __tablename__ = "qualification_evidence"
    __table_args__ = (
        UniqueConstraint(
            "scanner_run_id",
            "wallet_id",
            name="uq_qualification_evidence_scanner_run_id_wallet_id",
        ),
        Index(
            "ix_qualification_evidence_wallet_id_created_at",
            "wallet_id",
            "created_at",
        ),
        Index("ix_qualification_evidence_qualified", "qualified"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    wallet_id: Mapped[int] = mapped_column(ForeignKey("wallets.id"), nullable=False)
    scanner_run_id: Mapped[int] = mapped_column(
        ForeignKey("scanner_runs.id"),
        nullable=False,
    )
    sharpe_ratio: Mapped[Decimal | None] = mapped_column(Numeric(18, 8))
    max_drawdown_pct: Mapped[Decimal | None] = mapped_column(Numeric(18, 8))
    total_trades: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_volume_usd: Mapped[Decimal] = mapped_column(
        Numeric(24, 8),
        nullable=False,
        default=0,
    )
    pnl_total_usd: Mapped[Decimal | None] = mapped_column(Numeric(24, 8))
    qualified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    exclusion_reasons: Mapped[JsonObject | None] = mapped_column(JSONB)
    raw_payload: Mapped[JsonObject | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class Trade(Base):
    """Canonical Polymarket trade observed by the tracker."""

    __tablename__ = "trades"
    __table_args__ = (
        UniqueConstraint("provider_trade_id", name="uq_trades_provider_trade_id"),
        UniqueConstraint("dedupe_key", name="uq_trades_dedupe_key"),
        Index("ix_trades_wallet_id_trade_timestamp", "wallet_id", "trade_timestamp"),
        Index("ix_trades_market_id", "market_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    wallet_id: Mapped[int] = mapped_column(ForeignKey("wallets.id"), nullable=False)
    provider_trade_id: Mapped[str] = mapped_column(String(255), nullable=False)
    dedupe_key: Mapped[str] = mapped_column(String(255), nullable=False)
    market_id: Mapped[str] = mapped_column(String(255), nullable=False)
    side: Mapped[str] = mapped_column(String(16), nullable=False)
    size: Mapped[Decimal] = mapped_column(Numeric(24, 8), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(24, 8), nullable=False)
    trade_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    tracker_ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    raw_payload: Mapped[JsonObject | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class Watermark(Base):
    """Persistent per-wallet checkpoint for tracker/scanner consumers."""

    __tablename__ = "watermarks"
    __table_args__ = (
        UniqueConstraint(
            "wallet_id",
            "component",
            "source",
            name="uq_watermarks_wallet_id_component_source",
        ),
        Index("ix_watermarks_component_source", "component", "source"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    wallet_id: Mapped[int] = mapped_column(ForeignKey("wallets.id"), nullable=False)
    component: Mapped[str] = mapped_column(String(64), nullable=False)
    source: Mapped[str] = mapped_column(String(64), nullable=False)
    last_seen_trade_id: Mapped[str | None] = mapped_column(String(255))
    last_seen_trade_timestamp: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class SimulationPortfolio(Base):
    """Paper-trading portfolio state for a simulation strategy."""

    __tablename__ = "simulation_portfolios"
    __table_args__ = (
        UniqueConstraint("name", name="uq_simulation_portfolios_name"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    strategy: Mapped[str] = mapped_column(String(64), nullable=False)
    seed_amount_usd: Mapped[Decimal] = mapped_column(Numeric(24, 8), nullable=False)
    cash_balance_usd: Mapped[Decimal] = mapped_column(Numeric(24, 8), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class SimulatedTrade(Base):
    """Paper trade or skipped mirror attempt linked to a canonical trade."""

    __tablename__ = "simulated_trades"
    __table_args__ = (
        UniqueConstraint(
            "portfolio_id",
            "source_trade_id",
            name="uq_simulated_trades_portfolio_id_source_trade_id",
        ),
        Index(
            "ix_simulated_trades_portfolio_id_created_at",
            "portfolio_id",
            "created_at",
        ),
        Index("ix_simulated_trades_wallet_id_market_id", "wallet_id", "market_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    portfolio_id: Mapped[int] = mapped_column(
        ForeignKey("simulation_portfolios.id"),
        nullable=False,
    )
    source_trade_id: Mapped[int] = mapped_column(
        ForeignKey("trades.id"),
        nullable=False,
    )
    wallet_id: Mapped[int] = mapped_column(ForeignKey("wallets.id"), nullable=False)
    market_id: Mapped[str] = mapped_column(String(255), nullable=False)
    side: Mapped[str] = mapped_column(String(16), nullable=False)
    simulated_size: Mapped[Decimal | None] = mapped_column(Numeric(24, 8))
    simulated_price: Mapped[Decimal | None] = mapped_column(Numeric(24, 8))
    notional_usd: Mapped[Decimal | None] = mapped_column(Numeric(24, 8))
    realized_pnl_usd: Mapped[Decimal | None] = mapped_column(Numeric(24, 8))
    skipped_reason: Mapped[str | None] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class Position(Base):
    """Open paper position aggregated by strategy, wallet, market, and outcome."""

    __tablename__ = "positions"
    __table_args__ = (
        UniqueConstraint(
            "portfolio_id",
            "wallet_id",
            "market_id",
            "outcome",
            name="uq_positions_portfolio_id_wallet_id_market_id_outcome",
        ),
        Index("ix_positions_portfolio_id_market_id", "portfolio_id", "market_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    portfolio_id: Mapped[int] = mapped_column(
        ForeignKey("simulation_portfolios.id"),
        nullable=False,
    )
    wallet_id: Mapped[int] = mapped_column(ForeignKey("wallets.id"), nullable=False)
    market_id: Mapped[str] = mapped_column(String(255), nullable=False)
    outcome: Mapped[str] = mapped_column(String(255), nullable=False)
    open_size: Mapped[Decimal] = mapped_column(Numeric(24, 8), nullable=False)
    average_entry_price: Mapped[Decimal] = mapped_column(Numeric(24, 8), nullable=False)
    realized_pnl_usd: Mapped[Decimal] = mapped_column(
        Numeric(24, 8),
        nullable=False,
        default=0,
    )
    unrealized_pnl_usd: Mapped[Decimal | None] = mapped_column(Numeric(24, 8))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class PriceUpdate(Base):
    """Decoded read-only market price update used for context and correlation."""

    __tablename__ = "price_updates"
    __table_args__ = (
        UniqueConstraint(
            "provider",
            "symbol",
            "publish_time",
            name="uq_price_updates_provider_symbol_publish_time",
        ),
        Index("ix_price_updates_symbol_publish_time", "symbol", "publish_time"),
        Index("ix_price_updates_received_at", "received_at"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    symbol: Mapped[str] = mapped_column(String(64), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(24, 10), nullable=False)
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(24, 10))
    exponent: Mapped[int | None] = mapped_column(Integer)
    publish_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    latency_ms: Mapped[Decimal | None] = mapped_column(Numeric(18, 3))
    raw_payload: Mapped[JsonObject | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class Correlation(Base):
    """Non-causal link between a price window and Polymarket market movement."""

    __tablename__ = "correlations"
    __table_args__ = (
        UniqueConstraint(
            "price_update_id",
            "market_id",
            "window_start_at",
            name="uq_correlations_price_update_id_market_id_window_start_at",
        ),
        Index(
            "ix_correlations_market_id_window_start_at",
            "market_id",
            "window_start_at",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    price_update_id: Mapped[int] = mapped_column(
        ForeignKey("price_updates.id"),
        nullable=False,
    )
    market_id: Mapped[str] = mapped_column(String(255), nullable=False)
    window_start_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    window_end_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    confidence_score: Mapped[Decimal | None] = mapped_column(Numeric(10, 8))
    description: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class Notification(Base):
    """Notification delivery record keyed for idempotent alerting."""

    __tablename__ = "notifications"
    __table_args__ = (
        UniqueConstraint("idempotency_key", name="uq_notifications_idempotency_key"),
        Index("ix_notifications_wallet_id_created_at", "wallet_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    wallet_id: Mapped[int | None] = mapped_column(ForeignKey("wallets.id"))
    channel: Mapped[str] = mapped_column(String(64), nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[str | None] = mapped_column(Text)
    payload_ref: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class ComponentHeartbeat(Base):
    """One durable freshness row per component for health and dashboard state."""

    __tablename__ = "component_heartbeats"
    __table_args__ = (
        UniqueConstraint("component", name="uq_component_heartbeats_component"),
        Index("ix_component_heartbeats_state", "state"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    component: Mapped[str] = mapped_column(String(64), nullable=False)
    state: Mapped[str] = mapped_column(String(32), nullable=False)
    last_success_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_error_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_error: Mapped[str | None] = mapped_column(Text)
    stale_after_seconds: Mapped[int | None] = mapped_column(Integer)
    details: Mapped[JsonObject | None] = mapped_column(JSONB)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class ValidationEvidence(Base):
    """Durable validation observation keyed by assertion and evidence identity."""

    __tablename__ = "validation_evidence"
    __table_args__ = (
        UniqueConstraint(
            "assertion_id",
            "evidence_key",
            name="uq_validation_evidence_assertion_id_evidence_key",
        ),
        Index(
            "ix_validation_evidence_assertion_id_status",
            "assertion_id",
            "status",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    assertion_id: Mapped[str] = mapped_column(String(64), nullable=False)
    evidence_key: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_phase: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    evidence_path: Mapped[str | None] = mapped_column(String(512))
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    details: Mapped[JsonObject | None] = mapped_column(JSONB)
