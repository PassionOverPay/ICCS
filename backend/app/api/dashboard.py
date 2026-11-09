from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import current_user
from app.models import Community, Membership, Proposal, User, Vote

router = APIRouter()


@router.get("")
def dashboard(db: Session = Depends(get_db), user: User = Depends(current_user)):
    community_ids = select(Membership.community_id).where(Membership.user_id == user.id)
    communities = db.scalars(select(Community).where(Community.id.in_(community_ids)).order_by(Community.created_at.desc())).all()
    proposals = db.scalars(select(Proposal).where(Proposal.community_id.in_(community_ids)).order_by(Proposal.created_at.desc()).limit(10)).all()
    votes = db.scalar(select(func.count(Vote.id)).where(Vote.user_id == user.id)) or 0
    return {"communities": communities, "recent_proposals": proposals, "stats": {"votes_cast": votes, "communities": len(communities)}}

