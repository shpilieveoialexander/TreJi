"""User model

Revision ID: 88bda06dcaaa
Revises: 
Create Date: 2024-09-12 09:48:13.446279

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "88bda06dcaaa"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "user",
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password", sa.String(), nullable=True),
        sa.Column("name", sa.String(length=40), nullable=True),
        sa.Column(
            "status",
            sa.Enum("MANAGER", "DEVELOPER", name="userstatus"),
            nullable=False,
            create_type=False,
        ),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_user_id"), "user", ["id"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_user_id"), table_name="user")
    op.drop_table("user")
    # ### end Alembic commands ###
