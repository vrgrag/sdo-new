"""seed users with login

Revision ID: a0415060ceb0
Revises: dd35194e878e
Create Date: 2025-12-29 13:17:43.466522

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a0415060ceb0'
down_revision: Union[str, Sequence[str], None] = 'dd35194e878e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
