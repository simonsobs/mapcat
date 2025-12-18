"""Add notes missing field to atomic maps

Revision ID: 1195d17201ba
Revises: bc2be980cfe7
Create Date: 2025-12-18 11:48:53.341162

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1195d17201ba'
down_revision: Union[str, None] = 'bc2be980cfe7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass