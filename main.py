from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

import os

app = FastAPI()

# 🔥 IMPORTANT (for frontend to work)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE_URL = os.getenv("postgresql://cards_ch12_user:f4zBEDf1muMSGWuu4P5QbbYJ9J3kG6OC@dpg-d7ekat8sfn5c738e16mg-a"
                         ".frankfurt-postgres.render.com/cards_ch12")  # from Render


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


# Table
class Entry(Base):
    __tablename__ = "entries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    number = Column(Integer, unique=True)  # no duplicate numbers


Base.metadata.create_all(bind=engine)


# Request model
class EntryCreate(BaseModel):
    name: str
    email: str
    number: int


@app.post("/submit")
def submit(entry: EntryCreate):
    db = SessionLocal()

    # Check if number already taken
    existing = db.query(Entry).filter(Entry.number == entry.number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Number already taken")

    new_entry = Entry(
        name=entry.name,
        email=entry.email,
        number=entry.number
    )

    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)

    return {"message": "Number reserved successfully"}
