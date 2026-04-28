from fastapi import FastAPI
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi.responses import HTMLResponse 

import os


import os # 맨 위에 import os 추가

# 기존 SQLALCHEMY_DATABASE_URL = "sqlite:///..." 부분 대신 아래 코드로 교체
# Render 환경이면 PostgreSQL 주소를 쓰고, 내 컴퓨터면 SQLite를 쓰라는 뜻입니다.
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

SQLALCHEMY_DATABASE_URL = DATABASE_URL or "sqlite:///./my_notes.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
# SQLite 전용 설정인 connect_args={"check_same_thread": False}는 지워도 됩니다.

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 1. 카테고리 모델 추가
class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True) # 폴더 이름 (예: 천체물리학, C++공부)

# 2. 메모 모델 수정 (카테고리 ID를 참조하도록)
class Note(Base):
    __tablename__ = "notes_v3" # 새로운 구조를 위해 이름을 다시 바꿉니다
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(String)
    category_id = Column(Integer) # 어떤 폴더에 속해 있는지 숫자로 저장


Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/notes/")
def create_note(title: str, content: str, category: str = "일반"):
    db = SessionLocal()
    new_note = Note(title=title, content=content)
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    db.close()
    return {"message": "Saved!", "id": new_note.id}


@app.get("/notes/")
def get_all_notes():
    db = SessionLocal()
    return db.query(Note).all()

# main.py 하단에 추가
@app.delete("/notes/{note_id}")
def delete_note(note_id: int):
    db = SessionLocal()
    note = db.query(Note).filter(Note.id == note_id).first()
    if note:
        db.delete(note)
        db.commit()
        db.close()
        return {"message": "삭제되었습니다."}
    db.close()
    return {"message": "메모를 찾을 수 없습니다."}, 404

# 3. 카테고리 생성 API 추가
@app.post("/categories/")
def create_category(name: str):
    db = SessionLocal()
    new_cat = Category(name=name)
    db.add(new_cat)
    db.commit()
    db.close()
    return {"message": "Folder created!"}

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)