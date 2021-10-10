from .database import SessionLocal, engine


# TODO: delegate DB initalization to migrations library
models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# ==================
# Dependencies
# ==================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==================
# Endpoints
# ==================
@app.get("/")
def read_root():
    return {"Hello": "World"}
