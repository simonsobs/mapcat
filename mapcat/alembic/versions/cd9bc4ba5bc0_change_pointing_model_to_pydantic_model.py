"""Change pointing model to pydantic model

Revision ID: cd9bc4ba5bc0
Revises: 6ce7e94dfd2d
Create Date: 2026-04-22 12:36:02.164930

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "cd9bc4ba5bc0"
down_revision: Union[str, None] = "6ce7e94dfd2d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("depth_one_pointing_residuals") as batch:
        batch.add_column(sa.Column("residual_model", sa.JSON(), nullable=False))

        batch.drop_column("ra_offset")
        batch.drop_column("dec_offset")


def downgrade() -> None:
    with op.batch_alter_table("depth_one_pointing_residuals") as batch:
        batch.add_column(sa.Column("ra_offset", sa.Float, nullable=False))
        batch.add_column(sa.Column("dec_offset", sa.Float, nullable=False))

        batch.drop_column("residual_model")
