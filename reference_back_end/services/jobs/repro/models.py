from sqlalchemy import Column, Integer, String, Boolean, TEXT, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from uuid import uuid4
from json import dumps

Base = declarative_base()

class Query(Base):
    __tablename__ = 'query'

    pid = Column(String, primary_key=True)
    dataset_pid = Column(String, nullable=False)
    original = Column(String, nullable=False)
    normalized = Column(JSON, nullable=False)
    norm_hash = Column(String, nullable=False)
    result_hash = Column(String, nullable=False)
    meta_data = Column(JSON, default=dumps({}))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __init__(self, dataset_pid: str, original: dict, normalized: dict, norm_hash: str,
                 result_hash: str, metadata: dict={}):
        self.pid = "Q-" + str(uuid4())
        self.dataset_pid = dataset_pid
        self.original = original
        self.normalized = normalized
        self.norm_hash = norm_hash
        self.result_hash = result_hash
        if metadata: self.metadata = metadata

class QueryJob(Base):
    __tablename__ = 'queryjob'

    id = Column(String, primary_key=True, autoincrement=True)
    query_pid = Column(String, ForeignKey('query.pid'), nullable=False)
    job_id = Column(String, ForeignKey('job.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __init__(self, query_pid: str, job_id: str):
        self.query_pid = query_pid
        self.job_id = job_id