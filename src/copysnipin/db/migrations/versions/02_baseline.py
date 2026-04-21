"""Create CopySnipIn durable schema baseline."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "02_baseline"
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "wallets",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("address", sa.String(length=128), nullable=False),
        sa.Column("label", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("pinned", sa.Boolean(), nullable=False),
        sa.Column("blocked", sa.Boolean(), nullable=False),
        sa.Column(
            "first_seen_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("address", name="uq_wallets_address"),
    )
    op.create_index("ix_wallets_status", "wallets", ["status"])

    op.create_table(
        "scanner_runs",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("run_key", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("processed_wallets", sa.Integer(), nullable=False),
        sa.Column("qualified_wallets", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("raw_payload", postgresql.JSONB(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("run_key", name="uq_scanner_runs_run_key"),
    )

    op.create_table(
        "qualification_evidence",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("wallet_id", sa.BigInteger(), nullable=False),
        sa.Column("scanner_run_id", sa.BigInteger(), nullable=False),
        sa.Column("sharpe_ratio", sa.Numeric(18, 8), nullable=True),
        sa.Column("max_drawdown_pct", sa.Numeric(18, 8), nullable=True),
        sa.Column("total_trades", sa.Integer(), nullable=False),
        sa.Column("total_volume_usd", sa.Numeric(24, 8), nullable=False),
        sa.Column("pnl_total_usd", sa.Numeric(24, 8), nullable=True),
        sa.Column("qualified", sa.Boolean(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("exclusion_reasons", postgresql.JSONB(), nullable=True),
        sa.Column("raw_payload", postgresql.JSONB(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["wallet_id"], ["wallets.id"]),
        sa.ForeignKeyConstraint(["scanner_run_id"], ["scanner_runs.id"]),
        sa.UniqueConstraint(
            "scanner_run_id",
            "wallet_id",
            name="uq_qualification_evidence_scanner_run_id_wallet_id",
        ),
    )
    op.create_index(
        "ix_qualification_evidence_wallet_id_created_at",
        "qualification_evidence",
        ["wallet_id", "created_at"],
    )
    op.create_index(
        "ix_qualification_evidence_qualified",
        "qualification_evidence",
        ["qualified"],
    )

    op.create_table(
        "trades",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("wallet_id", sa.BigInteger(), nullable=False),
        sa.Column("provider_trade_id", sa.String(length=255), nullable=False),
        sa.Column("dedupe_key", sa.String(length=255), nullable=False),
        sa.Column("market_id", sa.String(length=255), nullable=False),
        sa.Column("side", sa.String(length=16), nullable=False),
        sa.Column("size", sa.Numeric(24, 8), nullable=False),
        sa.Column("price", sa.Numeric(24, 8), nullable=False),
        sa.Column("trade_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "tracker_ingested_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("raw_payload", postgresql.JSONB(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["wallet_id"], ["wallets.id"]),
        sa.UniqueConstraint("dedupe_key", name="uq_trades_dedupe_key"),
    )
    op.create_index("ix_trades_provider_trade_id", "trades", ["provider_trade_id"])
    op.create_index(
        "ix_trades_wallet_id_trade_timestamp",
        "trades",
        ["wallet_id", "trade_timestamp"],
    )
    op.create_index("ix_trades_market_id", "trades", ["market_id"])

    op.create_table(
        "watermarks",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("wallet_id", sa.BigInteger(), nullable=False),
        sa.Column("component", sa.String(length=64), nullable=False),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("last_seen_trade_id", sa.String(length=255), nullable=True),
        sa.Column(
            "last_seen_trade_timestamp",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["wallet_id"], ["wallets.id"]),
        sa.UniqueConstraint(
            "wallet_id",
            "component",
            "source",
            name="uq_watermarks_wallet_id_component_source",
        ),
    )
    op.create_index(
        "ix_watermarks_component_source",
        "watermarks",
        ["component", "source"],
    )

    op.create_table(
        "simulation_portfolios",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("strategy", sa.String(length=64), nullable=False),
        sa.Column("seed_amount_usd", sa.Numeric(24, 8), nullable=False),
        sa.Column("cash_balance_usd", sa.Numeric(24, 8), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("name", name="uq_simulation_portfolios_name"),
    )

    op.create_table(
        "simulated_trades",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("portfolio_id", sa.BigInteger(), nullable=False),
        sa.Column("source_trade_id", sa.BigInteger(), nullable=False),
        sa.Column("wallet_id", sa.BigInteger(), nullable=False),
        sa.Column("market_id", sa.String(length=255), nullable=False),
        sa.Column("side", sa.String(length=16), nullable=False),
        sa.Column("simulated_size", sa.Numeric(24, 8), nullable=True),
        sa.Column("simulated_price", sa.Numeric(24, 8), nullable=True),
        sa.Column("notional_usd", sa.Numeric(24, 8), nullable=True),
        sa.Column("realized_pnl_usd", sa.Numeric(24, 8), nullable=True),
        sa.Column("skipped_reason", sa.String(length=128), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["portfolio_id"], ["simulation_portfolios.id"]),
        sa.ForeignKeyConstraint(["source_trade_id"], ["trades.id"]),
        sa.ForeignKeyConstraint(["wallet_id"], ["wallets.id"]),
        sa.UniqueConstraint(
            "portfolio_id",
            "source_trade_id",
            name="uq_simulated_trades_portfolio_id_source_trade_id",
        ),
    )
    op.create_index(
        "ix_simulated_trades_portfolio_id_created_at",
        "simulated_trades",
        ["portfolio_id", "created_at"],
    )
    op.create_index(
        "ix_simulated_trades_wallet_id_market_id",
        "simulated_trades",
        ["wallet_id", "market_id"],
    )

    op.create_table(
        "positions",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("portfolio_id", sa.BigInteger(), nullable=False),
        sa.Column("wallet_id", sa.BigInteger(), nullable=False),
        sa.Column("market_id", sa.String(length=255), nullable=False),
        sa.Column("outcome", sa.String(length=255), nullable=False),
        sa.Column("open_size", sa.Numeric(24, 8), nullable=False),
        sa.Column("average_entry_price", sa.Numeric(24, 8), nullable=False),
        sa.Column("realized_pnl_usd", sa.Numeric(24, 8), nullable=False),
        sa.Column("unrealized_pnl_usd", sa.Numeric(24, 8), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["portfolio_id"], ["simulation_portfolios.id"]),
        sa.ForeignKeyConstraint(["wallet_id"], ["wallets.id"]),
        sa.UniqueConstraint(
            "portfolio_id",
            "wallet_id",
            "market_id",
            "outcome",
            name="uq_positions_portfolio_id_wallet_id_market_id_outcome",
        ),
    )
    op.create_index(
        "ix_positions_portfolio_id_market_id",
        "positions",
        ["portfolio_id", "market_id"],
    )

    op.create_table(
        "price_updates",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("symbol", sa.String(length=64), nullable=False),
        sa.Column("price", sa.Numeric(24, 10), nullable=False),
        sa.Column("confidence", sa.Numeric(24, 10), nullable=True),
        sa.Column("exponent", sa.Integer(), nullable=True),
        sa.Column("publish_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("latency_ms", sa.Numeric(18, 3), nullable=True),
        sa.Column("raw_payload", postgresql.JSONB(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "provider",
            "symbol",
            "publish_time",
            name="uq_price_updates_provider_symbol_publish_time",
        ),
    )
    op.create_index(
        "ix_price_updates_symbol_publish_time",
        "price_updates",
        ["symbol", "publish_time"],
    )
    op.create_index(
        "ix_price_updates_received_at",
        "price_updates",
        ["received_at"],
    )

    op.create_table(
        "correlations",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("price_update_id", sa.BigInteger(), nullable=False),
        sa.Column("market_id", sa.String(length=255), nullable=False),
        sa.Column("window_start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("window_end_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("confidence_score", sa.Numeric(10, 8), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["price_update_id"], ["price_updates.id"]),
        sa.UniqueConstraint(
            "price_update_id",
            "market_id",
            "window_start_at",
            name="uq_correlations_price_update_id_market_id_window_start_at",
        ),
    )
    op.create_index(
        "ix_correlations_market_id_window_start_at",
        "correlations",
        ["market_id", "window_start_at"],
    )

    op.create_table(
        "notifications",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("wallet_id", sa.BigInteger(), nullable=True),
        sa.Column("channel", sa.String(length=64), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("idempotency_key", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("payload_ref", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["wallet_id"], ["wallets.id"]),
        sa.UniqueConstraint("idempotency_key", name="uq_notifications_idempotency_key"),
    )
    op.create_index(
        "ix_notifications_wallet_id_created_at",
        "notifications",
        ["wallet_id", "created_at"],
    )

    op.create_table(
        "component_heartbeats",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("component", sa.String(length=64), nullable=False),
        sa.Column("state", sa.String(length=32), nullable=False),
        sa.Column("last_success_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("stale_after_seconds", sa.Integer(), nullable=True),
        sa.Column("details", postgresql.JSONB(), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("component", name="uq_component_heartbeats_component"),
    )
    op.create_index(
        "ix_component_heartbeats_state",
        "component_heartbeats",
        ["state"],
    )

    op.create_table(
        "validation_evidence",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("assertion_id", sa.String(length=64), nullable=False),
        sa.Column("evidence_key", sa.String(length=255), nullable=False),
        sa.Column("owner_phase", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("evidence_path", sa.String(length=512), nullable=True),
        sa.Column(
            "recorded_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("details", postgresql.JSONB(), nullable=True),
        sa.UniqueConstraint(
            "assertion_id",
            "evidence_key",
            name="uq_validation_evidence_assertion_id_evidence_key",
        ),
    )
    op.create_index(
        "ix_validation_evidence_assertion_id_status",
        "validation_evidence",
        ["assertion_id", "status"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_validation_evidence_assertion_id_status",
        table_name="validation_evidence",
    )
    op.drop_table("validation_evidence")

    op.drop_index("ix_component_heartbeats_state", table_name="component_heartbeats")
    op.drop_table("component_heartbeats")

    op.drop_index("ix_notifications_wallet_id_created_at", table_name="notifications")
    op.drop_table("notifications")

    op.drop_index(
        "ix_correlations_market_id_window_start_at",
        table_name="correlations",
    )
    op.drop_table("correlations")

    op.drop_index("ix_price_updates_received_at", table_name="price_updates")
    op.drop_index("ix_price_updates_symbol_publish_time", table_name="price_updates")
    op.drop_table("price_updates")

    op.drop_index("ix_positions_portfolio_id_market_id", table_name="positions")
    op.drop_table("positions")

    op.drop_index(
        "ix_simulated_trades_wallet_id_market_id",
        table_name="simulated_trades",
    )
    op.drop_index(
        "ix_simulated_trades_portfolio_id_created_at",
        table_name="simulated_trades",
    )
    op.drop_table("simulated_trades")

    op.drop_table("simulation_portfolios")

    op.drop_index("ix_watermarks_component_source", table_name="watermarks")
    op.drop_table("watermarks")

    op.drop_index("ix_trades_market_id", table_name="trades")
    op.drop_index("ix_trades_wallet_id_trade_timestamp", table_name="trades")
    op.drop_index("ix_trades_provider_trade_id", table_name="trades")
    op.drop_table("trades")

    op.drop_index(
        "ix_qualification_evidence_qualified",
        table_name="qualification_evidence",
    )
    op.drop_index(
        "ix_qualification_evidence_wallet_id_created_at",
        table_name="qualification_evidence",
    )
    op.drop_table("qualification_evidence")

    op.drop_table("scanner_runs")

    op.drop_index("ix_wallets_status", table_name="wallets")
    op.drop_table("wallets")
