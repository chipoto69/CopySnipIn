from __future__ import annotations

from pathlib import Path

from sqlalchemy import Index, Table, UniqueConstraint

from copysnipin.db.models import Base

ROOT = Path(__file__).resolve().parents[2]
MIGRATION_PATH = (
    ROOT / "src" / "copysnipin" / "db" / "migrations" / "versions" / "02_baseline.py"
)

REQUIRED_TABLES = {
    "wallets",
    "scanner_runs",
    "qualification_evidence",
    "trades",
    "watermarks",
    "simulation_portfolios",
    "simulated_trades",
    "positions",
    "price_updates",
    "correlations",
    "notifications",
    "component_heartbeats",
    "validation_evidence",
}

REQUIRED_COLUMNS = {
    "wallets": {
        "id",
        "address",
        "label",
        "status",
        "pinned",
        "blocked",
        "first_seen_at",
        "last_seen_at",
        "created_at",
        "updated_at",
    },
    "scanner_runs": {
        "id",
        "run_key",
        "status",
        "started_at",
        "completed_at",
        "processed_wallets",
        "qualified_wallets",
        "error_message",
        "created_at",
    },
    "qualification_evidence": {
        "id",
        "wallet_id",
        "scanner_run_id",
        "sharpe_ratio",
        "max_drawdown_pct",
        "total_trades",
        "total_volume_usd",
        "pnl_total_usd",
        "qualified",
        "status",
        "raw_payload",
        "created_at",
    },
    "trades": {
        "id",
        "wallet_id",
        "provider_trade_id",
        "dedupe_key",
        "market_id",
        "side",
        "size",
        "price",
        "trade_timestamp",
        "tracker_ingested_at",
        "raw_payload",
        "created_at",
    },
    "watermarks": {
        "id",
        "wallet_id",
        "component",
        "source",
        "last_seen_trade_id",
        "last_seen_trade_timestamp",
        "updated_at",
    },
    "simulation_portfolios": {
        "id",
        "name",
        "strategy",
        "seed_amount_usd",
        "cash_balance_usd",
        "status",
        "created_at",
        "updated_at",
    },
    "simulated_trades": {
        "id",
        "portfolio_id",
        "source_trade_id",
        "wallet_id",
        "market_id",
        "side",
        "simulated_size",
        "simulated_price",
        "notional_usd",
        "realized_pnl_usd",
        "skipped_reason",
        "created_at",
    },
    "positions": {
        "id",
        "portfolio_id",
        "wallet_id",
        "market_id",
        "outcome",
        "open_size",
        "average_entry_price",
        "realized_pnl_usd",
        "unrealized_pnl_usd",
        "updated_at",
    },
    "price_updates": {
        "id",
        "provider",
        "symbol",
        "price",
        "confidence",
        "exponent",
        "publish_time",
        "received_at",
        "latency_ms",
        "raw_payload",
        "created_at",
    },
    "correlations": {
        "id",
        "price_update_id",
        "market_id",
        "window_start_at",
        "window_end_at",
        "confidence_score",
        "description",
        "created_at",
    },
    "notifications": {
        "id",
        "wallet_id",
        "channel",
        "event_type",
        "idempotency_key",
        "status",
        "sent_at",
        "error_message",
        "created_at",
    },
    "component_heartbeats": {
        "id",
        "component",
        "state",
        "last_success_at",
        "last_error_at",
        "last_error",
        "stale_after_seconds",
        "updated_at",
    },
    "validation_evidence": {
        "id",
        "assertion_id",
        "evidence_key",
        "owner_phase",
        "status",
        "evidence_path",
        "recorded_at",
        "details",
    },
}

REQUIRED_UNIQUE_CONSTRAINTS = {
    "wallets": {"uq_wallets_address"},
    "scanner_runs": {"uq_scanner_runs_run_key"},
    "qualification_evidence": {
        "uq_qualification_evidence_scanner_run_id_wallet_id"
    },
    "trades": {"uq_trades_provider_trade_id", "uq_trades_dedupe_key"},
    "watermarks": {"uq_watermarks_wallet_id_component_source"},
    "simulation_portfolios": {"uq_simulation_portfolios_name"},
    "simulated_trades": {"uq_simulated_trades_portfolio_id_source_trade_id"},
    "positions": {"uq_positions_portfolio_id_wallet_id_market_id_outcome"},
    "price_updates": {"uq_price_updates_provider_symbol_publish_time"},
    "correlations": {"uq_correlations_price_update_id_market_id_window_start_at"},
    "notifications": {"uq_notifications_idempotency_key"},
    "component_heartbeats": {"uq_component_heartbeats_component"},
    "validation_evidence": {"uq_validation_evidence_assertion_id_evidence_key"},
}

REQUIRED_INDEXES = {
    "wallets": {"ix_wallets_status"},
    "qualification_evidence": {
        "ix_qualification_evidence_wallet_id_created_at",
        "ix_qualification_evidence_qualified",
    },
    "trades": {
        "ix_trades_wallet_id_trade_timestamp",
        "ix_trades_market_id",
    },
    "watermarks": {"ix_watermarks_component_source"},
    "simulated_trades": {
        "ix_simulated_trades_portfolio_id_created_at",
        "ix_simulated_trades_wallet_id_market_id",
    },
    "positions": {"ix_positions_portfolio_id_market_id"},
    "price_updates": {
        "ix_price_updates_symbol_publish_time",
        "ix_price_updates_received_at",
    },
    "correlations": {"ix_correlations_market_id_window_start_at"},
    "notifications": {"ix_notifications_wallet_id_created_at"},
    "component_heartbeats": {"ix_component_heartbeats_state"},
    "validation_evidence": {"ix_validation_evidence_assertion_id_status"},
}


def test_metadata_declares_required_data_backbone_tables() -> None:
    assert set(Base.metadata.tables) == REQUIRED_TABLES


def test_metadata_declares_required_columns() -> None:
    for table_name, required_columns in REQUIRED_COLUMNS.items():
        table = Base.metadata.tables[table_name]

        assert set(table.columns).issuperset(required_columns)


def test_metadata_declares_idempotency_unique_constraints() -> None:
    for table_name, required_constraints in REQUIRED_UNIQUE_CONSTRAINTS.items():
        table = Base.metadata.tables[table_name]

        assert unique_constraint_names(table).issuperset(required_constraints)


def test_metadata_declares_query_indexes() -> None:
    for table_name, required_indexes in REQUIRED_INDEXES.items():
        table = Base.metadata.tables[table_name]

        assert index_names(table).issuperset(required_indexes)


def unique_constraint_names(table: Table) -> set[str]:
    return {
        str(constraint.name)
        for constraint in table.constraints
        if isinstance(constraint, UniqueConstraint)
    }


def index_names(table: Table) -> set[str]:
    return {str(index.name) for index in table.indexes if isinstance(index, Index)}
