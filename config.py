import os

class Config:
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///C:/Users/G.Rajesh/.gemini/antigravity/scratch/emiva-ingestion/ingestion.db')

config = Config()
