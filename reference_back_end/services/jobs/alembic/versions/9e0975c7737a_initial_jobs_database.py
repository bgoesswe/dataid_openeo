"""Initial jobs database

Revision ID: 9e0975c7737a
Revises: 
Create Date: 2018-05-11 15:14:10.010760

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9e0975c7737a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'jobs',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('process_graph_id', sa.String(), nullable=False),
        sa.Column('output', sa.JSON(), default={"format": "GTiff"}),
        sa.Column('plan', sa.String(), default="free"),
        sa.Column('budget', sa.Integer(), default=0),
        sa.Column('current_costs', sa.Integer(), default=0),
        sa.Column('status', sa.String(), default="submitted"),
        sa.Column('created_at', sa.DateTime(),default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_table(
        'query',
        sa.Column('query_pid', sa.String(), primary_key=True),
        sa.Column('dataset_pid', sa.String(), nullable=True),
        sa.Column('original', sa.String(), nullable=True),
        sa.Column('normalized', sa.String(), nullable=False),
        sa.Column('norm_hash', sa.JSON(), default={"format": "GTiff"}),
        sa.Column('result_hash', sa.String(), default="free"),
        sa.Column('meta_data', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_table(
        'queryjob',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('query_pid', sa.String(), nullable=True),
        sa.Column('job_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )




class QueryJob(Base):
    __tablename__ = 'queryjob'

    id = Column(Integer, primary_key=True)
    query_pid = Column(String, nullable=False)
    job_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __init__(self, query_pid: str, job_id: str):
        self.query_pid = query_pid
        self.job_id = job_id

def downgrade():
    op.drop_table('jobs')
