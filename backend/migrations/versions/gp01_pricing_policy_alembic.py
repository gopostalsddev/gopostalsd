"""Adopt pricing_policies into Alembic ownership.

Revision ID: gp01_pricing_policy
Revises: refund_payment_id_nullable
"""

from alembic import op
import sqlalchemy as sa


revision = "gp01_pricing_policy"
down_revision = "refund_payment_id_nullable"
branch_labels = None
depends_on = None


_EXPECTED_COLUMNS = {
    "id",
    "vendor_currency",
    "display_currency",
    "cad_to_usd_rate",
    "exchange_buffer_percent",
    "markup_percent",
    "fixed_fee_usd",
    "minimum_profit_usd",
    "rounding_increment",
    "customization_file_review_fee_usd",
    "customization_design_assist_fee_usd",
    "created_at",
    "updated_at",
}


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # Existing production databases may already have this table because old
    # application startup created it directly. Adopt only the exact expected
    # shape; fail rather than silently masking schema drift.
    if inspector.has_table("pricing_policies"):
        actual_columns = {
            column["name"] for column in inspector.get_columns("pricing_policies")
        }
        missing = sorted(_EXPECTED_COLUMNS - actual_columns)
        if missing:
            raise RuntimeError(
                "Existing pricing_policies table is incompatible; missing column(s): "
                + ", ".join(missing)
            )
        return

    op.create_table(
        "pricing_policies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("vendor_currency", sa.String(length=8), nullable=False),
        sa.Column("display_currency", sa.String(length=8), nullable=False),
        sa.Column("cad_to_usd_rate", sa.Numeric(10, 4), nullable=False),
        sa.Column("exchange_buffer_percent", sa.Numeric(10, 2), nullable=False),
        sa.Column("markup_percent", sa.Numeric(10, 2), nullable=False),
        sa.Column("fixed_fee_usd", sa.Numeric(10, 2), nullable=False),
        sa.Column("minimum_profit_usd", sa.Numeric(10, 2), nullable=False),
        sa.Column("rounding_increment", sa.Numeric(10, 2), nullable=False),
        sa.Column("customization_file_review_fee_usd", sa.Numeric(10, 2), nullable=False),
        sa.Column("customization_design_assist_fee_usd", sa.Numeric(10, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    raise RuntimeError(
        "gp01_pricing_policy is forward-only because it may adopt a legacy "
        "runtime-created table containing production data"
    )
