from sqlalchemy import Column, Integer, String, Boolean, TEXT, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from uuid import uuid4
from json import dumps

Base = declarative_base()

class Job(Base):
    __tablename__ = 'jobs'

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    title = Column(String, nullable=True)
    description = Column(String, nullable=True)
    process_graph_id = Column(String, nullable=False)
    output = Column(JSON, default=dumps({"format": "GTiff"}))    # Integrate output formats in table at data/volume service
    plan = Column(String, default="free")   # Implement plans in database/service
    budget = Column(Integer, default=0)
    current_costs = Column(Integer, default=0, nullable=False)
    status = Column(String, default="submitted", nullable=False)
    logs = Column(String, default=dumps({}))
    metrics = Column(JSON, default=dumps({}))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __init__(self, user_id: str, process_graph_id: str, title: str=None, description: str=None, output: dict=None,
                 plan: str=None, budget: int=None):
        self.id = "jb-" + str(uuid4())
        self.user_id = user_id
        self.process_graph_id = process_graph_id
        if title: self.title = title
        if description: self.description = description
        if output: self.output = dumps(output)
        if plan: self.plan = plan
        if budget: self.budget = budget


class Query(Base):
    __tablename__ = 'query'

    pid = Column("query_pid", String, primary_key=True)
    dataset_pid = Column(String, nullable=False)
    original = Column(String, nullable=False)
    normalized = Column(String, nullable=False)
    norm_hash = Column(String, nullable=False)
    result_hash = Column(String, nullable=False)
    meta_data = Column("meta_data", String, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __init__(self, dataset_pid: str, original: dict, normalized: dict, norm_hash: str,
                 result_hash: str, metadata: dict={}):
        self.pid = "qu-" + str(uuid4())
        self.dataset_pid = dataset_pid
        self.original = original
        self.normalized = normalized
        self.norm_hash = norm_hash
        self.result_hash = result_hash
        if metadata: self.meta_data = metadata

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