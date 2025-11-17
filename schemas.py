"""
Database Schemas for Portfolio

Each Pydantic model below maps to a MongoDB collection (lowercase name).
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

class Inquiry(BaseModel):
    """
    Inquiries from the contact form
    Collection name: "inquiry"
    """
    name: str = Field(..., min_length=2, max_length=80)
    email: EmailStr
    service: str = Field(..., description="Requested service: Photography, Video, Graphic Design, Creative Direction")
    message: Optional[str] = Field(None, max_length=2000)

class Project(BaseModel):
    """
    Highlighted projects for the portfolio grid
    Collection name: "project"
    """
    title: str
    category: str = Field(..., description="Photography | Video | Graphic Design")
    cover_url: str = Field(..., description="Public image/video thumbnail URL")
    description: Optional[str] = None
    tags: Optional[List[str]] = None
