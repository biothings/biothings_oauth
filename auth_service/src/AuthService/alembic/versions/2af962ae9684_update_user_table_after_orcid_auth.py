"""Update User table after ORCID auth

Revision ID: 2af962ae9684
Revises: cd07806c1dd5
Create Date: 2021-02-18 05:56:54.873610+00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2af962ae9684'
down_revision = 'cd07806c1dd5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('full_name', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('last_login', sa.DateTime(), nullable=False))
    op.alter_column('users', 'identity_provider',
               existing_type=postgresql.ENUM('GITHUB', 'ORCID', name='useridentityprovider'),
               nullable=False)
    op.alter_column('users', 'identity_provider_user_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.drop_column('users', 'last_identity_provider_authentication')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('last_identity_provider_authentication', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.alter_column('users', 'identity_provider_user_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('users', 'identity_provider',
               existing_type=postgresql.ENUM('GITHUB', 'ORCID', name='useridentityprovider'),
               nullable=True)
    op.drop_column('users', 'last_login')
    op.drop_column('users', 'full_name')
    # ### end Alembic commands ###