from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Replace with your actual PostgreSQL credentials
DATABASE_URL = "postgresql://postgres:aiface_123@128.199.119.151:5432/face_attendance"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
