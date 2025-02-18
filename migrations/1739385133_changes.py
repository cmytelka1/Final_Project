"""changes

Revision ID: 1739385133
Revises: 1739384807
Create Date: 2025-02-12 13:32:13.258558

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1739385133'
down_revision: Union[str, None] = '1739384807'
branch_labels: Union[str, Sequence[str], None] = ()
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('manuscript',
    sa.Column('ms_id', sa.Integer(), nullable=False),
    sa.Column('ms_name', sa.String(), nullable=True),
    sa.Column('author_id', sa.Integer(), nullable=True),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('abstract', sa.Text(), nullable=True),
    sa.Column('submission_date', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['person.id'], ),
    sa.PrimaryKeyConstraint('ms_id')
    )
    op.create_table('keywords',
    sa.Column('kw_id', sa.Integer(), nullable=False),
    sa.Column('ms_id', sa.Integer(), nullable=True),
    sa.Column('author_id', sa.Integer(), nullable=True),
    sa.Column('keyword', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['person.id'], ),
    sa.ForeignKeyConstraint(['ms_id'], ['manuscript.ms_id'], ),
    sa.PrimaryKeyConstraint('kw_id')
    )
    op.drop_table('submission')
    op.add_column('decision', sa.Column('ms_id', sa.Integer(), nullable=True))
    op.drop_constraint(None, 'decision', type_='foreignkey')
    op.create_foreign_key(None, 'decision', 'manuscript', ['ms_id'], ['ms_id'])
    op.drop_column('decision', 'submission_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('decision', sa.Column('submission_id', sa.INTEGER(), nullable=True))
    op.drop_constraint(None, 'decision', type_='foreignkey')
    op.create_foreign_key(None, 'decision', 'submission', ['submission_id'], ['id'])
    op.drop_column('decision', 'ms_id')
    op.create_table('submission',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('title', sa.VARCHAR(), nullable=False),
    sa.Column('user_id', sa.INTEGER(), nullable=True),
    sa.Column('submission_date', sa.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['person.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('keywords')
    op.drop_table('manuscript')
    # ### end Alembic commands ###
