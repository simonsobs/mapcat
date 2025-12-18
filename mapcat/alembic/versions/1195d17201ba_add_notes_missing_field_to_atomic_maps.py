"""Add notes missing field to atomic maps

Revision ID: 1195d17201ba
Revises: bc2be980cfe7
Create Date: 2025-12-18 11:48:53.341162

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '1195d17201ba'
down_revision: Union[str, None] = 'bc2be980cfe7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('atomic_maps', sa.Column('rqu_avg', sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column('atomic_maps', 'rqu_avg')