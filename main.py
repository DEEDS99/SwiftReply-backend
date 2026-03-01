
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "https://YOUR_FRONTEND_URL",  # e.g., https://swiftreply.onrender.com
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import FastAPI, Request, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
import requests
import os
from openai import OpenAI

app = FastAPI()

# =============================
# CONFIG
# =============================

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
client_ai = OpenAI(api_key=OPENAI_API_KEY)

# =============================
# DATABASE MODELS
# =============================

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    password = Column(String)
    plan = Column(String, default="FREE")

class Business(Base):
    __tablename__ = "businesses"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    business_name = Column(String)
    phone_number_id = Column(String, unique=True)
    whatsapp_token = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Lead(Base):
    __tablename__ = "leads"
    id = Column(Integer, primary_key=True)
    business_id = Column(Integer, ForeignKey("businesses.id"))
    phone = Column(String)
    message = Column(Text)
    reply = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# =============================
# AUTH FUNCTIONS
# =============================

def hash_password(password):
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def create_token(data):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

# =============================
# SCHEMAS
# =============================

class RegisterUser(BaseModel):
    email: str
    password: str

class LoginUser(BaseModel):
    email: str
    password: str

class BusinessCreate(BaseModel):
    user_id: int
    business_name: str
    phone_number_id: str
    whatsapp_token: str

class BroadcastMessage(BaseModel):
    business_id: int
    message: str

# =============================
# AUTH ENDPOINTS
# =============================

@app.post("/register")
def register(data: RegisterUser):
    db = SessionLocal()
    user = User(email=data.email, password=hash_password(data.password))
    db.add(user)
    db.commit()
    db.close()
    return {"message": "User registered"}

@app.post("/login")
def login(data: LoginUser):
    db = SessionLocal()
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token({"user_id": user.id})
    db.close()
    return {"access_token": token}

# =============================
# BUSINESS CREATION
# =============================

@app.post("/create-business")
def create_business(data: BusinessCreate):
    db = SessionLocal()
    business = Business(
        user_id=data.user_id,
        business_name=data.business_name,
        phone_number_id=data.phone_number_id,
        whatsapp_token=data.whatsapp_token
    )
    db.add(business)
    db.commit()
    db.close()
    return {"message": "Business created"}

# =============================
# AI REPLY FUNCTION
# =============================

def generate_ai_reply(message):
    response = client_ai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a professional business assistant."},
            {"role": "user", "content": message}
        ]
    )
    return response.choices[0].message.content

# =============================
# WHATSAPP SEND
# =============================

def send_whatsapp(token, phone_number_id, to, message):
    url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": message}
    }
    requests.post(url, headers=headers, json=data)

# =============================
# WEBHOOK
# =============================

@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    try:
        change = body["entry"][0]["changes"][0]["value"]
        phone_number_id = change["metadata"]["phone_number_id"]
        message = change["messages"][0]
        sender = message["from"]
        text = message["text"]["body"]

        db = SessionLocal()
        business = db.query(Business).filter(
            Business.phone_number_id == phone_number_id
        ).first()

        if business:
            user = db.query(User).filter(User.id == business.user_id).first()

            # FREE plan = keyword only
            if user.plan == "FREE":
                reply = "Thank you for contacting us. Upgrade to Pro for AI replies."
            else:
                reply = generate_ai_reply(text)

            send_whatsapp(
                business.whatsapp_token,
                business.phone_number_id,
                sender,
                reply
            )

            lead = Lead(
                business_id=business.id,
                phone=sender,
                message=text,
                reply=reply
            )
            db.add(lead)
            db.commit()

        db.close()

    except Exception as e:
        print("Error:", e)

    return {"status": "ok"}

# =============================
# DASHBOARD API
# =============================

@app.get("/leads/{business_id}")
def get_leads(business_id: int):
    db = SessionLocal()
    leads = db.query(Lead).filter(Lead.business_id == business_id).all()
    db.close()
    return leads

# =============================
# BROADCAST
# =============================

@app.post("/broadcast")
def broadcast(data: BroadcastMessage):
    db = SessionLocal()
    leads = db.query(Lead).filter(Lead.business_id == data.business_id).all()
    business = db.query(Business).filter(Business.id == data.business_id).first()

    for lead in leads:
        send_whatsapp(
            business.whatsapp_token,
            business.phone_number_id,
            lead.phone,
            data.message
        )

    db.close()
    return {"message": "Broadcast sent"}