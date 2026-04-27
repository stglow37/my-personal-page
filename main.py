from fastapi import FastAPI
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi.responses import HTMLResponse # 이 줄을 추가하세요


SQLALCHEMY_DATABASE_URL = "sqlite:///./my_notes.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(String)


Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/notes/")
def create_note(title: str, content: str):
    db = SessionLocal()
    new_note = Note(title=title, content=content)
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
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

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)