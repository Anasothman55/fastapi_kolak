"""remove is_verify

Revision ID: a42a831f8a84
Revises: 4674682f0258
Create Date: 2025-01-18 21:18:01.025118

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'a42a831f8a84'
down_revision: Union[str, None] = '4674682f0258'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('usermodels', 'is_verified')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('usermodels', sa.Column('is_verified', sa.BOOLEAN(), autoincrement=False, nullable=False))
    # ### end Alembic commands ###
