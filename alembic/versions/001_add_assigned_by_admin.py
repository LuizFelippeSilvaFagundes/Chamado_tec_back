"""Add assigned_by_admin field to tickets

Revision ID: 001
Revises: 
Create Date: 2025-01-17 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Adicionar coluna assigned_by_admin à tabela tickets
    op.add_column('tickets', sa.Column('assigned_by_admin', sa.Boolean(), nullable=True, default=False))


def downgrade():
    # Remover coluna assigned_by_admin da tabela tickets
    op.drop_column('tickets', 'assigned_by_admin')
