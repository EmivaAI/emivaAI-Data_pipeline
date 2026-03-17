from sqlalchemy import create_engine, Column, Integer, String, JSON, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import os

Base = declarative_base()

class RawWebhookData(Base):
    __tablename__ = 'raw_webhook_data'
    id = Column(Integer, primary_key=True)
    source = Column(String(50), nullable=False) # github, slack, jira
    event_type = Column(String(100))
    payload = Column(JSON, nullable=False)
    received_at = Column(DateTime, default=datetime.datetime.utcnow)
    processed = Column(Boolean, default=False)

class ChangeEvent(Base):
    __tablename__ = 'change_event'
    id = Column(Integer, primary_key=True)
    source_event_ids = Column(JSON, nullable=False) # List of RawWebhookData IDs
    change_type = Column(String(50)) # bug_fix, feature, chore, docs, unknown
    component = Column(String(100))
    summary = Column(String(255))
    severity = Column(String(50)) # low, medium, high, critical
    linked_issues = Column(JSON) # List of Jira keys
    linked_prs = Column(JSON) # List of PR numbers
    linked_threads = Column(JSON) # List of Slack thread IDs
    actors = Column(JSON) # List of unique actor names/IDs
    raw_signals = Column(JSON) # Consistently structured flags (pr_merged, issue_resolved, etc.)
    processed = Column(Boolean, default=False) # For Stage 3 analysis
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

from config import config

engine = create_engine(config.DATABASE_URL)
Session = sessionmaker(bind=engine)

def init_db():
    # Ensure directory exists for SQLite
    if config.DATABASE_URL.startswith('sqlite:///'):
        db_path = config.DATABASE_URL.replace('sqlite:///', '')
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
            
    Base.metadata.create_all(engine)

def save_raw_data(source, payload, event_type=None):
    session = Session()
    new_data = RawWebhookData(source=source, payload=payload, event_type=event_type)
    session.add(new_data)
    session.commit()
    session.close()
