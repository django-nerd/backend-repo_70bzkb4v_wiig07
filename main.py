import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List

from database import db, create_document, get_documents
from schemas import Inquiry, Project

app = FastAPI(title="Playful Portfolio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response

# API to submit a contact inquiry (persists to MongoDB)
@app.post("/api/contact")
async def create_contact(inquiry: Inquiry):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    try:
        inserted_id = create_document('inquiry', inquiry)
        return {"status": "ok", "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Public endpoint to get highlighted projects (seeded or added via DB tools)
@app.get("/api/projects", response_model=List[Project])
async def list_projects(limit: int = 9):
    if db is None:
        return []
    try:
        docs = get_documents('project', {}, limit)
        # Normalize mongo _id and fields
        normalized = []
        for d in docs:
            normalized.append({
                'title': d.get('title', ''),
                'category': d.get('category', ''),
                'cover_url': d.get('cover_url', ''),
                'description': d.get('description'),
                'tags': d.get('tags') or []
            })
        return normalized
    except Exception:
        return []

# Schema explorer utility
@app.get('/schema')
async def get_schema():
    return {
        'collections': ['inquiry', 'project'],
        'models': {
            'Inquiry': Inquiry.model_json_schema(),
            'Project': Project.model_json_schema(),
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
