from datetime import datetime
from sqlmodel import SQLModel, Field
from typing import Optional
from pydantic import BaseModel


class SessionCreate(BaseModel):
  sender_pubkey: str
  receiver_pubkey: str

class Session(SQLModel, table=True):
  id: Optional[int] = Field(default=None, primary_key=True)
  session_id: str = Field(index=True, unique=True) # Unique identifier for the session between two points
  sender_pubkey: str # Sender public key
  receiver_pubkey: str # Receiver public key
  status: str = "pending" # (pending, accepted, rejected, completed)
  qber: Optional[float] = None # Quantum Bit Error Rate, if applicable
  created_at: datetime = Field(default_factory=datetime.utcnow)
  updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})


class SessionDebugData(SQLModel, table=True):
  id: Optional[int] = Field(default=None, primary_key=True)
  session_id: str = Field(index=True)

  sender_bases: Optional[str] = None
  receiver_bases: Optional[str] = None
  sender_bits: Optional[str] = None
  receiver_bits: Optional[str] = None
  qber: Optional[float] = None

  created_at: datetime = Field(default_factory=datetime.utcnow)



