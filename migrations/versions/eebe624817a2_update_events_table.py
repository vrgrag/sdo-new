"""update events table

Revision ID: eebe624817a2
Revises: a0415060ceb0
Create Date: 2026-01-05 17:00:32.874356

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eebe624817a2'
down_revision: Union[str, Sequence[str], None] = 'a0415060ceb0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
