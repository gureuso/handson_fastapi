"""UpdateVideoEntity

Revision ID: e29caf322760
Revises: 3a18e693779f
Create Date: 2025-07-08 13:35:59.073827

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e29caf322760'
down_revision: Union[str, None] = '3a18e693779f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Video', sa.Column('user_id', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Video', 'user_id')
    # ### end Alembic commands ###
