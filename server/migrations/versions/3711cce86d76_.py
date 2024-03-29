"""empty message

Revision ID: 3711cce86d76
Revises: ced3f91d3838
Create Date: 2019-12-20 13:32:47.530554

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "3711cce86d76"
down_revision = "ced3f91d3838"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("logs", sa.Column("http_cache_control", sa.String(), nullable=True))
    op.add_column("logs", sa.Column("http_connection", sa.String(), nullable=True))
    op.add_column("logs", sa.Column("http_cookie", sa.String(), nullable=True))
    op.add_column("logs", sa.Column("http_user_agent", sa.String(), nullable=True))
    op.add_column("logs", sa.Column("remote_port", sa.Integer(), nullable=True))
    op.add_column("logs", sa.Column("server_protocol", sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("logs", "server_protocol")
    op.drop_column("logs", "remote_port")
    op.drop_column("logs", "http_user_agent")
    op.drop_column("logs", "http_cookie")
    op.drop_column("logs", "http_connection")
    op.drop_column("logs", "http_cache_control")
    # ### end Alembic commands ###
