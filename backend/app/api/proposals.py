from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.communities import membership
from app.db.session import get_db
from app.deps import current_user
from app.models import Comment, Community, Membership, Proposal, Status, User, Vote
from app.schemas import CommentCreate, ProposalCreate, VoteIn

router = APIRouter()


def proposal_or_404(db: Session, proposal_id: int) -> Proposal:
    proposal = db.get(Proposal, proposal_id)
    if not proposal:
        raise HTTPException(404, "Proposal not found")
    return proposal


@router.get("/communities/{community_id}/proposals")
def list_proposals(community_id: int, db: Session = Depends(get_db)):
    return db.scalars(select(Proposal).where(Proposal.community_id == community_id).order_by(Proposal.created_at.desc())).all()


@router.post("/communities/{community_id}/proposals", status_code=201)
def create_proposal(community_id: int, payload: ProposalCreate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    if not membership(db, community_id, user.id):
        raise HTTPException(403, "Join the community before creating proposals")
    if not db.get(Community, community_id):
        raise HTTPException(404, "Community not found")
    proposal = Proposal(**payload.model_dump(), community_id=community_id, author_id=user.id)
    db.add(proposal)
    db.commit()
    db.refresh(proposal)
    return proposal


@router.get("/proposals/{proposal_id}")
def get_proposal(proposal_id: int, db: Session = Depends(get_db)):
    proposal = proposal_or_404(db, proposal_id)
    up = db.scalar(select(func.count(Vote.id)).where(Vote.proposal_id == proposal_id, Vote.value == 1)) or 0
    down = db.scalar(select(func.count(Vote.id)).where(Vote.proposal_id == proposal_id, Vote.value == -1)) or 0
    return {"proposal": proposal, "results": {"upvotes": up, "downvotes": down, "total": up + down}}


@router.patch("/proposals/{proposal_id}/close")
def close_proposal(proposal_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    proposal = proposal_or_404(db, proposal_id)
    record = membership(db, proposal.community_id, user.id)
    if not record or (record.role != "admin" and proposal.author_id != user.id):
        raise HTTPException(403, "Only the author or an administrator can close proposals")
    proposal.status = Status.closed
    db.commit()
    return proposal


@router.get("/proposals/{proposal_id}/comments")
def comments(proposal_id: int, db: Session = Depends(get_db)):
    proposal_or_404(db, proposal_id)
    return db.execute(select(Comment, User.username).join(User, User.id == Comment.author_id).where(Comment.proposal_id == proposal_id).order_by(Comment.created_at.asc())).all()


@router.post("/proposals/{proposal_id}/comments", status_code=201)
def add_comment(proposal_id: int, payload: CommentCreate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    proposal = proposal_or_404(db, proposal_id)
    if not membership(db, proposal.community_id, user.id):
        raise HTTPException(403, "Only community members can comment")
    comment = Comment(proposal_id=proposal_id, author_id=user.id, content=payload.content)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.delete("/comments/{comment_id}", status_code=204)
def delete_comment(comment_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    comment = db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(404, "Comment not found")
    proposal = proposal_or_404(db, comment.proposal_id)
    record = membership(db, proposal.community_id, user.id)
    if comment.author_id != user.id and (not record or record.role != "admin"):
        raise HTTPException(403, "Not authorized to remove this comment")
    db.delete(comment)
    db.commit()


@router.put("/proposals/{proposal_id}/vote")
def vote(proposal_id: int, payload: VoteIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    proposal = proposal_or_404(db, proposal_id)
    if proposal.status != Status.open:
        raise HTTPException(400, "Voting is closed")
    if not membership(db, proposal.community_id, user.id):
        raise HTTPException(403, "Only community members can vote")
    current = db.scalar(select(Vote).where(Vote.proposal_id == proposal_id, Vote.user_id == user.id))
    if current:
        current.value = payload.value
    else:
        db.add(Vote(proposal_id=proposal_id, user_id=user.id, value=payload.value))
    db.commit()
    return get_proposal(proposal_id, db)

