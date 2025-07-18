from fastapi import APIRouter, HTTPException, Response
from sqlmodel import Session as DBSession, select
from database import engine
from models import Session as SessionModel, SessionCreate
import hashlib

router = APIRouter()


def generate_session_id(alice_pubkey: str, bob_pubkey: str) -> str:
  chave_ordenada = "".join(sorted([alice_pubkey, bob_pubkey]))
  return hashlib.sha256(chave_ordenada.encode()).hexdigest()


@router.post("/session")
def get_session(session: SessionCreate, response: Response):

  # Get the session ID based on the public keys or get an existing session
  session_id = generate_session_id(session.sender_pubkey, session.receiver_pubkey)
  
  with DBSession(engine) as db_session:
  
    smtm = select(SessionModel).where(SessionModel.session_id == session_id)
    existing_session = db_session.exec(smtm).first()
    
    if existing_session:
      response.status_code = 409
      return {
        "message": "Session already exists or is being created.",
      }

    
    new_session = SessionModel(
      session_id=session_id,
      sender_pubkey=session.sender_pubkey,
      receiver_pubkey=session.receiver_pubkey,
      status="pending",
    )

    db_session.add(new_session)
    db_session.commit()
    db_session.refresh(new_session)
    response.status_code = 201
    return {
      "session_id": new_session.session_id,
    }
  

@router.get("/session/pendings/{pubkey}")
def get_pending_sessions(pubkey: str, response: Response):
  with DBSession(engine) as db_session:
    smtm = select(SessionModel).where(
      (SessionModel.receiver_pubkey == pubkey) & (SessionModel.status == "pending")
    )

    pending_sesssions = db_session.exec(smtm).all()
    if not pending_sesssions:
      response.status_code = 404
      return {"message": "No pending sessions found."}
    response.status_code = 200
    return {
      "pending_sessions": [
        {
          "session_id": session.session_id,
          "sender_pubkey": session.sender_pubkey,
          "receiver_pubkey": session.receiver_pubkey,
          "status": session.status,
          "created_at": session.created_at.isoformat(),
        }
        for session in pending_sesssions
      ]
    }

@router.get("/session/accept/{pubkey}/{session_id}")
def acccept_session(pubkey: str, session_id: str, response: Response):
  with DBSession(engine) as db_session:
    smtm = select(SessionModel).where(
      (SessionModel.session_id == session_id) &
      (SessionModel.receiver_pubkey == pubkey) &
      (SessionModel.status == "pending")
    )

    session = db_session.exec(smtm).first()
    if not session:
      response.status_code = 404
      return {"message": "Session not found or already accepted."}
    session.status = "accepted"
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    response.status_code = 200
    return {
      "message": "Session accepted.",
      "session_id": session.session_id,
      "status": session.status,
      "created_at": session.created_at.isoformat(),
    }
  
@router.get("/session/reject/{pubkey}/{session_id}")
def reject_session(pubkey: str, session_id: str, response: Response):
  with DBSession(engine) as db_session:
    smtm = select(SessionModel).where(
      (SessionModel.session_id == session_id) & 
      (SessionModel.receiver_pubkey == pubkey) & 
      (SessionModel.status == "pending")
    )

    session = db_session.exec(smtm).first()
    if not session:
      response.status_code = 404
      return {"message": "Session not found or already rejected."}
    session.status = "rejected"
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    response.status_code = 200
    return {
      "message": "Session rejected.",
      "session_id": session.session_id,
      "status": session.status,
      "created_at": session.created_at.isoformat(),
    }
  

@router.get("/session/consult/{session_id}")
def get_session_status(session_id: str, response: Response):
  with DBSession(engine) as db_session:
    smtm = select(SessionModel).where(SessionModel.session_id == session_id)
    session = db_session.exec(smtm).first()
    
    if not session:
      response.status_code = 404
      return {"message": "Session not found."}
    
    response.status_code = 200
    return {
      "session_id": session.session_id,
      "sender_pubkey": session.sender_pubkey,
      "receiver_pubkey": session.receiver_pubkey,
      "status": session.status,
      "created_at": session.created_at.isoformat(),
    }