from sqlalchemy import create_engine, Column, Integer, String, JSON, DateTime
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

engine = create_engine('sqlite:///C:\\Users\\G.Rajesh\\.gemini\\antigravity\\scratch\\emiva-ingestion\\ingestion.db')
Session = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)

def save_raw_data(source, payload, event_type=None):
    session = Session()
    new_data = RawWebhookData(source=source, payload=payload, event_type=event_type)
    session.add(new_data)
    session.commit()
    session.close()
