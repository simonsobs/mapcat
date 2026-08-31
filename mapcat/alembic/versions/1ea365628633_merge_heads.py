"""merge heads

Revision ID: 1ea365628633
Revises: 0762b3c7694d, fa43e5586322
Create Date: 2026-08-31 13:46:54.313874

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1ea365628633'
down_revision: Union[str, None] = ('0762b3c7694d', 'fa43e5586322')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass