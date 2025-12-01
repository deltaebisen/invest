"""Add technical indicators

Revision ID: 002
Revises: 001
Create Date: 2024-12-01 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("stock_prices", sa.Column("ma5", sa.Float(), nullable=True))
    op.add_column("stock_prices", sa.Column("ma20", sa.Float(), nullable=True))
    op.add_column("stock_prices", sa.Column("rsi9", sa.Float(), nullable=True))
    op.add_column("stock_prices", sa.Column("bb_upper", sa.Float(), nullable=True))
    op.add_column("stock_prices", sa.Column("bb_middle", sa.Float(), nullable=True))
    op.add_column("stock_prices", sa.Column("bb_lower", sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column("stock_prices", "bb_lower")
    op.drop_column("stock_prices", "bb_middle")
    op.drop_column("stock_prices", "bb_upper")
    op.drop_column("stock_prices", "rsi9")
    op.drop_column("stock_prices", "ma20")
    op.drop_column("stock_prices", "ma5")
