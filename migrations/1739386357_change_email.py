"""change email

Revision ID: 1739386357
Revises: 1739386287
Create Date: 2025-02-12 13:52:37.480839

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1739386357'
down_revision: Union[str, None] = '1739386287'
branch_labels: Union[str, Sequence[str], None] = ()
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('person', 'email',
               existing_type=sa.VARCHAR(),
               type_=sa.Text(),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('person', 'email',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(),
               existing_nullable=True)
    # ### end Alembic commands ###
