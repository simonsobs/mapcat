"""update atomic map coadd table

Revision ID: fd6670a1fdbe
Revises: 1195d17201ba
Create Date: 2025-12-18 19:50:23.313924

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'fd6670a1fdbe'
down_revision: Union[str, None] = '1195d17201ba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "link_coadd_map_to_coadd",
        sa.Column(
            "parent_coadd_id",
            sa.Integer(),
            sa.ForeignKey("atomic_map_coadds.coadd_id"),
            nullable=False,
        ),
        sa.Column(
            "child_coadd_id",
            sa.Integer(),
            sa.ForeignKey("atomic_map_coadds.coadd_id"),
            nullable=False,
        ),
    )
    
    op.add_column('atomic_map_coadds', sa.Column('stop_time', sa.Float(), nullable=False))
    op.add_column('atomic_map_coadds', sa.Column('prefix_path', sa.String(), nullable=False))
    op.add_column('atomic_map_coadds', sa.Column('freq_channel', sa.String(), nullable=False))
    op.add_column('atomic_map_coadds', sa.Column('geom_file_path', sa.String(), nullable=False))
    op.add_column('atomic_map_coadds', sa.Column('split_label', sa.String(), nullable=False))
    op.drop_column('atomic_map_coadds', 'end_time')
    op.drop_column('atomic_map_coadds', 'coadd_path')
    op.drop_column('atomic_map_coadds', 'frequency')


def downgrade() -> None:
    op.add_column('atomic_map_coadds', sa.Column('frequency', sa.String(), nullable=False))
    op.add_column('atomic_map_coadds', sa.Column('coadd_path', sa.String(), nullable=False))
    op.add_column('atomic_map_coadds', sa.Column('end_time', sa.Float(), nullable=False))
    op.drop_column('atomic_map_coadds', 'split_label')
    op.drop_column('atomic_map_coadds', 'geom_file_path')
    op.drop_column('atomic_map_coadds', 'freq_channel')
    op.drop_column('atomic_map_coadds', 'prefix_path')
    op.drop_column('atomic_map_coadds', 'stop_time')
    op.drop_table('link_coadd_map_to_coadd')
