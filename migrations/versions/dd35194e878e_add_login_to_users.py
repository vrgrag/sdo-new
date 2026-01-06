from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "dd35194e878e"
down_revision: Union[str, Sequence[str], None] = "3a6dc3934ae4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("login", sa.String(length=50), nullable=True))
    op.create_unique_constraint("uq_users_login", "users", ["login"])


def downgrade() -> None:
    op.drop_constraint("uq_users_login", "users", type_="unique")
    op.drop_column("users", "login")
