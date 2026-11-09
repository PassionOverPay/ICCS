from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    email: EmailStr
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class CommunityCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str = Field(min_length=1, max_length=2000)


class CommunityOut(CommunityCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    creator_id: int
    created_at: datetime
    member_count: int = 0


class ProposalCreate(BaseModel):
    title: str = Field(min_length=2, max_length=180)
    description: str = Field(min_length=1, max_length=10000)


class CommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=5000)


class VoteIn(BaseModel):
    value: int = Field(ge=-1, le=1)

