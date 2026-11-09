from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import current_user
from app.models import Community, Membership, Role, User
from app.schemas import CommunityCreate, CommunityOut

router = APIRouter()


def membership(db: Session, community_id: int, user_id: int) -> Membership | None:
    return db.scalar(select(Membership).where(Membership.community_id == community_id, Membership.user_id == user_id))


@router.get("/communities", response_model=list[CommunityOut])
def list_communities(db: Session = Depends(get_db)):
    rows = db.execute(select(Community, func.count(Membership.id)).outerjoin(Membership).group_by(Community.id).order_by(Community.created_at.desc())).all()
    return [CommunityOut.model_validate(c).model_copy(update={"member_count": count}) for c, count in rows]


@router.post("/communities", response_model=CommunityOut, status_code=201)
def create_community(payload: CommunityCreate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    if db.scalar(select(Community).where(Community.name == payload.name)):
        raise HTTPException(409, "Community name is already in use")
    community = Community(**payload.model_dump(), creator_id=user.id)
    db.add(community)
    db.flush()
    db.add(Membership(user_id=user.id, community_id=community.id, role=Role.admin))
    db.commit()
    db.refresh(community)
    return community


@router.get("/communities/{community_id}", response_model=CommunityOut)
def get_community(community_id: int, db: Session = Depends(get_db)):
    community = db.get(Community, community_id)
    if not community:
        raise HTTPException(404, "Community not found")
    count = db.scalar(select(func.count(Membership.id)).where(Membership.community_id == community_id)) or 0
    return CommunityOut.model_validate(community).model_copy(update={"member_count": count})


@router.post("/communities/{community_id}/join", status_code=204)
def join(community_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    if not db.get(Community, community_id):
        raise HTTPException(404, "Community not found")
    if membership(db, community_id, user.id):
        raise HTTPException(409, "Already a member")
    db.add(Membership(user_id=user.id, community_id=community_id))
    db.commit()


@router.delete("/communities/{community_id}/leave", status_code=204)
def leave(community_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    record = membership(db, community_id, user.id)
    if not record:
        raise HTTPException(404, "Membership not found")
    if record.role == Role.admin:
        raise HTTPException(400, "Community administrators cannot leave their community")
    db.delete(record)
    db.commit()

