#!/bin/bash
# =============================================================================
# 🌲 OSIS vX.3 "MARKET DOMINANCE" — Plateforme Complète
# =============================================================================
# Frontend React + Backend FastAPI + Tous les microservices
# =============================================================================
set -e

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; BLUE='\033[0;34m'; PURPLE='\033[0;35m'; NC='\033[0m'
echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║   🌲 OSIS vX.3 — MARKET DOMINANCE                                ║"
echo "║   Frontend + Backend + Microservices + IA + Mobile               ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || echo "localhost")
DOMAIN="osis.${PUBLIC_IP}.nip.io"
BASE_DIR="/opt/osis-platform"
VERSION="X.3.0"

# ------------------------------------------------------------
# PRÉREQUIS GLOBAUX
# ------------------------------------------------------------
echo -e "${YELLOW}📦 Installation des dépendances globales...${NC}"
sudo apt update && sudo apt upgrade -y
sudo apt install -y \
    python3 python3-pip python3-venv \
    nodejs npm \
    nginx redis-server sqlite3 \
    git curl wget \
    libssl-dev libsodium-dev \
    qrencode \
    golang-go rustc cargo \
    mosquitto mosquitto-clients

# ------------------------------------------------------------
# STRUCTURE DU PROJET
# ------------------------------------------------------------
sudo mkdir -p $BASE_DIR
sudo chown -R $USER:$USER $BASE_DIR

mkdir -p $BASE_DIR/{backend,frontend,mobile,services,config,logs,data,scripts}

# ============================================================
# 1. BACKEND PRINCIPAL (FastAPI Python)
# ============================================================
echo -e "${CYAN}🔧 Installation du Backend Principal (FastAPI)...${NC}"

cat > $BASE_DIR/backend/requirements.txt << 'REQ'
fastapi==0.115.0
uvicorn[standard]==0.30.6
sqlalchemy==2.0.35
pydantic[email]==2.9.2
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.1
jinja2
python-multipart
httpx
redis
celery
psutil
Pillow
qrcode
REQ

cd $BASE_DIR/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configuration
cat > $BASE_DIR/backend/.env << EOF
DATABASE_URL=sqlite:///./data/osis.db
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REDIS_URL=redis://localhost:6379/0
CORE_PORT=8000
EOF

# Base de données
cat > $BASE_DIR/backend/database.py << 'DBEOF'
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/osis.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    balance_satoshi = Column(Float, default=0.0)
    total_hashes = Column(Float, default=0.0)
    total_contributions = Column(Integer, default=0)
    total_donations = Column(Float, default=0.0)
    level = Column(Integer, default=1)
    reputation = Column(Float, default=0.0)
    referral_code = Column(String, unique=True)
    premium = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    machines = relationship("Machine", back_populates="owner")
    contributions = relationship("Contribution", back_populates="author")
    donations = relationship("Donation", back_populates="donor")
    courses_completed = relationship("Certification", back_populates="user")

class Machine(Base):
    __tablename__ = "machines"
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    hostname = Column(String, nullable=False)
    cpu_hashrate_khs = Column(Float, default=0.0)
    gpu_hashrate_khs = Column(Float, default=0.0)
    pine_value_satoshi = Column(Float, default=0.0)
    algorithm = Column(String, default="sha256")
    is_robot = Column(Boolean, default=False)
    status = Column(String, default="active")
    last_heartbeat = Column(DateTime, default=datetime.utcnow)
    
    owner = relationship("User", back_populates="machines")

class Contribution(Base):
    __tablename__ = "contributions"
    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    language = Column(String, default="fr")
    status = Column(String, default="pending")
    reward_satoshi = Column(Float, default=0.0)
    votes = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    author = relationship("User", back_populates="contributions")

class Donation(Base):
    __tablename__ = "donations"
    id = Column(Integer, primary_key=True, index=True)
    donor_id = Column(Integer, ForeignKey("users.id"))
    campaign = Column(String, nullable=False)
    amount_satoshi = Column(Float, nullable=False)
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    donor = relationship("User", back_populates="donations")

class DictionaryEntry(Base):
    __tablename__ = "dictionary"
    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, nullable=False, index=True)
    definition = Column(String, nullable=False)
    language = Column(String, nullable=False, index=True)
    contributor_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String, default="approved")
    reward_satoshi = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    content = Column(Text)
    author_id = Column(Integer, ForeignKey("users.id"))
    difficulty = Column(String, default="débutant")
    language = Column(String, default="fr")
    reward_satoshi = Column(Float, default=10.0)
    price_satoshi = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Certification(Base):
    __tablename__ = "certifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    score = Column(Integer, default=100)
    completed_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="courses_completed")
    course = relationship("Course")

class Service(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    price_satoshi = Column(Float, nullable=False)
    delivery_time_hours = Column(Integer, default=24)
    rating = Column(Float, default=0.0)
    total_sales = Column(Integer, default=0)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Loan(Base):
    __tablename__ = "loans"
    id = Column(Integer, primary_key=True, index=True)
    borrower_id = Column(Integer, ForeignKey("users.id"))
    amount_satoshi = Column(Float, nullable=False)
    purpose = Column(String, nullable=False)
    interest_rate = Column(Float, nullable=False)
    duration_days = Column(Integer, nullable=False)
    status = Column(String, default="open")
    funded_amount = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()
DBEOF

# Sécurité
cat > $BASE_DIR/backend/security.py << 'SECEOF'
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from database import get_db, User
from sqlalchemy.orm import Session
import os
import secrets

SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Identifiants invalides",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None: raise credentials_exception
    except JWTError: raise credentials_exception
    user = db.query(User).filter(User.id == user_id).first()
    if user is None: raise credentials_exception
    return user

def generate_referral_code() -> str:
    return secrets.token_hex(4)
SECEOF

# Modèles Pydantic
cat > $BASE_DIR/backend/schemas.py << 'SCHEOF'
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    referral_code: Optional[str] = None

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    balance_satoshi: float
    total_hashes: float
    level: int
    reputation: float
    premium: bool
    created_at: datetime
    class Config: from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginRequest(BaseModel):
    username: str
    password: str

class MachineRegister(BaseModel):
    hostname: str
    algorithm: str = "sha256"
    has_gpu: bool = False
    is_robot: bool = False

class MiningReport(BaseModel):
    machine_id: int
    cpu_hashrate_khs: float
    data_consumed_mb: float = 0.0
    satoshi_reward: float

class ContributionCreate(BaseModel):
    title: str
    content: str
    category: str
    language: str = "fr"

class DictionaryEntryCreate(BaseModel):
    word: str
    definition: str
    language: str = "fr"

class DonationCreate(BaseModel):
    campaign: str
    amount_satoshi: float
    message: Optional[str] = ""

class ServiceCreate(BaseModel):
    title: str
    description: str
    category: str
    price_satoshi: float
    delivery_time_hours: int = 24

class LoanCreate(BaseModel):
    amount_satoshi: float
    purpose: str
    interest_rate: float
    duration_days: int

class CourseCreate(BaseModel):
    title: str
    description: str
    content: str
    difficulty: str = "débutant"
    language: str = "fr"
    reward_satoshi: float = 10.0

class PlanRequest(BaseModel):
    style: str = "toumbouctou"
    area_m2: float = 100.0
    rooms: int = 3
    floors: int = 1
    orientation: str = "nord"

class CraftRequest(BaseModel):
    name: str
    category: str = "meuble"
    style: str = "africain"
    width_cm: float = 100.0
    height_cm: float = 80.0
    depth_cm: float = 40.0
SCHEOF

# Routes API
cat > $BASE_DIR/backend/routes.py << 'ROUTEOF'
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db, User, Machine, Contribution, Donation, DictionaryEntry
from database import Course, Certification, Service, Loan
from schemas import *
from security import get_current_user, hash_password, verify_password, create_access_token, generate_referral_code
import secrets, math, hashlib, time, os

router = APIRouter()

# =============================================
# AUTHENTIFICATION
# =============================================
@router.post("/auth/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter((User.username == user.username) | (User.email == user.email)).first():
        raise HTTPException(400, "Utilisateur déjà existant")
    
    hashed = hash_password(user.password)
    ref_code = generate_referral_code()
    new_user = User(username=user.username, email=user.email, hashed_password=hashed, referral_code=ref_code, balance_satoshi=10.0)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    token = create_access_token({"sub": new_user.id})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/auth/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == login_data.username).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(401, "Identifiants invalides")
    token = create_access_token({"sub": user.id})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/users/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

# =============================================
# MINAGE
# =============================================
@router.post("/machines/register")
def register_machine(machine: MachineRegister, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing = db.query(Machine).filter_by(owner_id=current_user.id, hostname=machine.hostname).first()
    if existing: return {"machine_id": existing.id, "message": "Machine déjà enregistrée"}
    
    new_machine = Machine(owner_id=current_user.id, hostname=machine.hostname, algorithm=machine.algorithm, is_robot=machine.is_robot)
    db.add(new_machine)
    db.commit()
    db.refresh(new_machine)
    return {"machine_id": new_machine.id, "message": "Machine enregistrée", "auto_mining": True}

@router.post("/machines/report")
def report_hashrate(report: MiningReport, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    machine = db.query(Machine).filter_by(id=report.machine_id, owner_id=current_user.id).first()
    if not machine: raise HTTPException(404, "Machine non trouvée")
    
    machine.cpu_hashrate_khs = report.cpu_hashrate_khs
    machine.pine_value_satoshi = report.satoshi_reward
    machine.last_heartbeat = datetime.utcnow()
    
    current_user.balance_satoshi += report.satoshi_reward
    current_user.total_hashes += report.cpu_hashrate_khs
    current_user.level = max(1, int((current_user.total_hashes * 0.01 + current_user.total_contributions * 10) ** 0.4))
    
    db.commit()
    return {"new_balance": current_user.balance_satoshi, "level": current_user.level}

# =============================================
# BANQUE SOCIALE
# =============================================
@router.post("/contributions/submit")
def submit_contribution(contrib: ContributionCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new = Contribution(author_id=current_user.id, title=contrib.title, content=contrib.content, category=contrib.category, language=contrib.language, reward_satoshi=25.0)
    db.add(new)
    current_user.total_contributions += 1
    db.commit()
    return {"message": "Contribution soumise", "reward": 25.0}

@router.get("/contributions")
def list_contributions(db: Session = Depends(get_db)):
    return db.query(Contribution).order_by(Contribution.created_at.desc()).limit(50).all()

# =============================================
# DICTIONNAIRE MULTILINGUE
# =============================================
SUPPORTED_LANGUAGES = ["fr","en","bambara","wolof","peul","sonrhaï","tamasheq","haoussa","lingala","swahili","zoulou"]

@router.post("/dictionary/add")
def add_word(entry: DictionaryEntryCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if entry.language not in SUPPORTED_LANGUAGES:
        raise HTTPException(400, f"Langue non supportée. Langues : {SUPPORTED_LANGUAGES}")
    new = DictionaryEntry(word=entry.word, definition=entry.definition, language=entry.language, contributor_id=current_user.id, reward_satoshi=2.0)
    db.add(new)
    current_user.balance_satoshi += 2.0
    db.commit()
    return {"message": "Mot ajouté au dictionnaire", "reward": 2.0}

@router.get("/dictionary/search")
def search_words(q: str, language: str = "fr", db: Session = Depends(get_db)):
    return db.query(DictionaryEntry).filter(DictionaryEntry.word.contains(q), DictionaryEntry.language == language, DictionaryEntry.status == "approved").all()

@router.get("/languages")
def get_languages():
    return SUPPORTED_LANGUAGES

# =============================================
# DONS
# =============================================
CAMPAIGNS = [
    {"name": "Hôpital Général de Bamako", "address": "bc1qkue2h6hy0mchup80f9me036qwywfpmmcvefnsf"},
    {"name": "Hôpital de l'Amitié", "address": "bc1qv4cez2gxvdh4ntha28at5f9mw0nv38szwn79ap"},
    {"name": "Clinique Mobile Piney", "address": "bc1qt3p7fw7fw3a3k6a82zmh4m45drgrdldx7r3u79"}
]

@router.post("/donate")
def make_donation(donation: DonationCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.balance_satoshi < donation.amount_satoshi:
        raise HTTPException(400, "Solde insuffisant")
    current_user.balance_satoshi -= donation.amount_satoshi
    current_user.total_donations += donation.amount_satoshi
    new = Donation(donor_id=current_user.id, campaign=donation.campaign, amount_satoshi=donation.amount_satoshi, message=donation.message)
    db.add(new)
    db.commit()
    return {"message": "💝 Merci pour votre don !", "new_balance": current_user.balance_satoshi}

@router.get("/campaigns")
def get_campaigns():
    return CAMPAIGNS

# =============================================
# ARCHITECTURE
# =============================================
@router.post("/build/plan")
def generate_plan(plan: PlanRequest):
    width = max(int(math.sqrt(plan.area_m2) * 10), 200)
    height = width if plan.rooms <= 4 else int(width * 1.5)
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}"><rect width="{width}" height="{height}" fill="#f5e6c8" stroke="#8b5e3c" stroke-width="2"/><rect x="10" y="10" width="{width-20}" height="{height-20}" fill="none" stroke="#8b5e3c" stroke-width="3"/><text x="{width//2}" y="20" text-anchor="middle">Nord ↑</text>'
    for i in range(plan.rooms):
        x = 20 + i * (((width - 40) // plan.rooms) + 5)
        svg += f'<rect x="{x}" y="30" width="{(width-40)//plan.rooms}" height="{height-60}" fill="#fff" stroke="#555" rx="3"/>'
    svg += f'<text x="{width//2}" y="{height-5}" text-anchor="middle" font-size="10">Plan {plan.style} - {plan.area_m2}m²</text></svg>'
    return {"svg": svg, "reward": 0.5}

# =============================================
# MENUISERIE
# =============================================
@router.post("/craft/model")
def generate_furniture(craft: CraftRequest):
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {craft.width_cm+20} {craft.height_cm+20}"><rect x="10" y="10" width="{craft.width_cm}" height="{craft.height_cm}" fill="#c19a6b" stroke="#5c3a1e" stroke-width="2" rx="5"/>'
    if craft.style == "africain":
        svg += f'<line x1="15" y1="15" x2="{craft.width_cm+5}" y2="15" stroke="#5c3a1e" stroke-dasharray="4"/>'
    svg += f'<text x="{(craft.width_cm+20)//2}" y="{craft.height_cm+15}" text-anchor="middle">{craft.name}</text></svg>'
    return {"svg": svg, "reward": 0.3}

# =============================================
# ÉDUCATION
# =============================================
@router.get("/courses")
def list_courses(db: Session = Depends(get_db)):
    return db.query(Course).all()

@router.post("/courses/{course_id}/complete")
def complete_course(course_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    course = db.query(Course).get(course_id)
    if not course: raise HTTPException(404, "Cours introuvable")
    cert = Certification(user_id=current_user.id, course_id=course_id, score=100)
    db.add(cert)
    current_user.balance_satoshi += course.reward_satoshi
    db.commit()
    return {"message": f"Certifié ! +{course.reward_satoshi} sat"}

# =============================================
# STATISTIQUES
# =============================================
@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    return {
        "users": db.query(User).count(),
        "machines": db.query(Machine).count(),
        "hashrate": db.query(Machine).filter_by(status="active").with_entities(Machine.cpu_hashrate_khs).all(),
        "total_donations": db.query(Donation).with_entities(Donation.amount_satoshi).all(),
        "dictionary_words": db.query(DictionaryEntry).filter_by(status="approved").count()
    }
ROUTEOF

# Application principale
cat > $BASE_DIR/backend/main.py << 'MAINEOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routes import router
import uvicorn
import os

app = FastAPI(title="OSIS API", version="X.3.0", description="Backend Principal OSIS")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(router, prefix="/api")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return {"message": "OSIS API vX.3.0", "docs": "/docs"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("CORE_PORT", 8000)))
MAINEOF

# ------------------------------------------------------------
# 2. FRONTEND REACT
# ------------------------------------------------------------
echo -e "${CYAN}🎨 Création du Frontend React...${NC}"

cat > $BASE_DIR/frontend/package.json << 'PKGJSON'
{
  "name": "osis-frontend",
  "version": "3.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.0",
    "recharts": "^2.10.0",
    "lucide-react": "^0.294.0",
    "qrcode.react": "^3.1.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build"
  },
  "devDependencies": {
    "react-scripts": "5.0.1"
  },
  "browserslist": {
    "production": [">0.2%", "not dead", "not op_mini all"],
    "development": ["last 1 chrome version", "last 1 firefox version", "last 1 safari version"]
  }
}
PKGJSON

cat > $BASE_DIR/frontend/public/index.html << 'IDXHTML'
<!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1.0"/><title>🌲 OSIS Platform</title><link rel="manifest" href="/manifest.json"/><meta name="theme-color" content="#00c853"/></head><body><div id="root"></div></body></html>
IDXHTML

cat > $BASE_DIR/frontend/src/index.js << 'IDXJS'
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<React.StrictMode><App /></React.StrictMode>);
IDXJS

cat > $BASE_DIR/frontend/src/App.js << 'APPJS'
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Thème
const theme = {
  bg: '#0a0a1a',
  card: '#1a1a3e',
  accent: '#00c853',
  gold: '#ffd700',
  blue: '#448aff',
  red: '#ff1744',
  text: '#ffffff',
  muted: '#888888'
};

const styles = {
  container: { background: theme.bg, color: theme.text, minHeight: '100vh', fontFamily: 'sans-serif' },
  header: { background: theme.card, padding: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: `2px solid ${theme.accent}` },
  logo: { color: theme.accent, fontSize: '24px', fontWeight: 'bold', textDecoration: 'none' },
  nav: { display: 'flex', gap: '20px' },
  navLink: { color: theme.text, textDecoration: 'none', padding: '5px 10px' },
  card: { background: theme.card, padding: '20px', borderRadius: '10px', margin: '10px 0' },
  grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px', padding: '20px' },
  btn: { padding: '10px 20px', background: theme.accent, color: '#000', border: 'none', borderRadius: '25px', cursor: 'pointer', fontWeight: 'bold' },
  input: { padding: '10px', borderRadius: '5px', border: '1px solid #333', background: '#0a0a2a', color: 'white', width: '100%', margin: '5px 0' }
};

function Home() {
  const [stats, setStats] = useState(null);
  useEffect(() => { axios.get(`${API_URL}/stats`).then(r => setStats(r.data)).catch(() => {}); }, []);
  
  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <Link to="/" style={styles.logo}>🌲 OSIS</Link>
        <nav style={styles.nav}>
          <Link to="/mining" style={styles.navLink}>⛏️ Minage</Link>
          <Link to="/services" style={styles.navLink}>💼 Services</Link>
          <Link to="/dictionary" style={styles.navLink}>📖 Dictionnaire</Link>
          <Link to="/build" style={styles.navLink}>🏗️ Architecture</Link>
          <Link to="/craft" style={styles.navLink}>🪚 Menuiserie</Link>
          <Link to="/education" style={styles.navLink}>🎓 Cours</Link>
          <Link to="/donate" style={styles.navLink}>💝 Dons</Link>
          <Link to="/login" style={{...styles.navLink, background: theme.accent, color: '#000', borderRadius: '20px', padding: '5px 15px'}}>Connexion</Link>
        </nav>
      </header>
      
      <div style={{padding: '40px', textAlign: 'center'}}>
        <h1 style={{color: theme.accent, fontSize: '3em'}}>OSIS Platform</h1>
        <p style={{color: theme.muted, fontSize: '1.2em', maxWidth: '600px', margin: '20px auto'}}>
          L'écosystème qui valorise chaque ressource, chaque savoir, chaque geste de solidarité
        </p>
      </div>
      
      {stats && (
        <div style={{display: 'flex', justifyContent: 'center', gap: '40px', flexWrap: 'wrap', padding: '20px'}}>
          <div style={{textAlign: 'center'}}><div style={{fontSize: '2.5em', color: theme.gold, fontWeight: 'bold'}}>{stats.users || 0}</div><div style={{color: theme.muted}}>Utilisateurs</div></div>
          <div style={{textAlign: 'center'}}><div style={{fontSize: '2.5em', color: theme.gold, fontWeight: 'bold'}}>{stats.machines || 0}</div><div style={{color: theme.muted}}>Machines</div></div>
          <div style={{textAlign: 'center'}}><div style={{fontSize: '2.5em', color: theme.gold, fontWeight: 'bold'}}>{stats.dictionary_words || 0}</div><div style={{color: theme.muted}}>Mots</div></div>
        </div>
      )}
    </div>
  );
}

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  
  const handleLogin = async () => {
    try {
      const res = await axios.post(`${API_URL}/auth/login`, { username, password });
      localStorage.setItem('token', res.data.access_token);
      window.location.href = '/';
    } catch(e) { alert('Identifiants invalides'); }
  };
  
  return (
    <div style={{...styles.container, display: 'flex', justifyContent: 'center', alignItems: 'center'}}>
      <div style={{...styles.card, width: '400px'}}>
        <h2 style={{color: theme.accent}}>Connexion</h2>
        <input style={styles.input} placeholder="Nom d'utilisateur" value={username} onChange={e => setUsername(e.target.value)} />
        <input style={styles.input} type="password" placeholder="Mot de passe" value={password} onChange={e => setPassword(e.target.value)} />
        <button style={{...styles.btn, width: '100%', marginTop: '10px'}} onClick={handleLogin}>Se connecter</button>
      </div>
    </div>
  );
}

function Dictionary() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  
  const search = async () => {
    const res = await axios.get(`${API_URL}/dictionary/search?q=${query}&language=fr`);
    setResults(res.data);
  };
  
  return (
    <div style={styles.container}>
      <header style={styles.header}><Link to="/" style={styles.logo}>🌲 OSIS</Link></header>
      <div style={{padding: '40px', maxWidth: '800px', margin: '0 auto'}}>
        <h1 style={{color: theme.accent}}>📖 Dictionnaire Universel</h1>
        <div style={{display: 'flex', gap: '10px', margin: '20px 0'}}>
          <input style={styles.input} placeholder="Rechercher un mot..." value={query} onChange={e => setQuery(e.target.value)} onKeyPress={e => e.key === 'Enter' && search()} />
          <button style={styles.btn} onClick={search}>Rechercher</button>
        </div>
        {results.map(w => (
          <div key={w.id} style={styles.card}>
            <h3 style={{color: theme.accent}}>{w.word} <small style={{color: theme.muted}}>({w.language})</small></h3>
            <p>{w.definition}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/dictionary" element={<Dictionary />} />
        <Route path="*" element={<div style={{...styles.container, textAlign:'center', paddingTop:'100px'}}><h1>404</h1><Link to="/" style={{color:theme.accent}}>Retour</Link></div>} />
      </Routes>
    </Router>
  );
}

export default App;
APPJS

# ------------------------------------------------------------
# 3. SERVICE WORKER PWA
# ------------------------------------------------------------
cat > $BASE_DIR/frontend/public/sw.js << 'SWJS'
const CACHE = 'osis-vx3';
self.addEventListener('install', e => e.waitUntil(caches.open(CACHE).then(c => c.addAll(['/','/static/manifest.json']))));
self.addEventListener('fetch', e => e.respondWith(caches.match(e.request).then(r => r || fetch(e.request))));
self.addEventListener('push', e => {
  const data = e.data.json();
  self.registration.showNotification('OSIS', { body: data.message, icon: '/icon-192.png' });
});
SWJS

cat > $BASE_DIR/frontend/public/manifest.json << 'MANIFEST'
{"name":"OSIS Platform","short_name":"OSIS","start_url":"/","display":"standalone","background_color":"#0a0a1a","theme_color":"#00c853","icons":[{"src":"/icon-192.png","sizes":"192x192","type":"image/png"},{"src":"/icon-512.png","sizes":"512x512","type":"image/png"}]}
MANIFEST

# ------------------------------------------------------------
# 4. SCRIPTS DE DÉMARRAGE
# ------------------------------------------------------------
cat > $BASE_DIR/scripts/start-all.sh << 'STARTALL'
#!/bin/bash
echo "🌲 Démarrage de l'écosystème OSIS vX.3..."

# Backend
cd /opt/osis-platform/backend
source venv/bin/activate
python3 main.py &
echo "✅ Backend (port 8000)"

# Services
for svc in freelance lending agriculture pineforge; do
    if [ -f /opt/osis-platform/services/$svc/server.py ]; then
        python3 /opt/osis-platform/services/$svc/server.py &
        echo "✅ Service $svc démarré"
    fi
done

# Gateway
python3 /opt/osis-platform/gateway.py &
echo "✅ Gateway (port 8080)"

echo "🌐 Dashboard: http://localhost:8080"
echo "📚 Docs: http://localhost:8000/docs"
STARTALL

cat > $BASE_DIR/scripts/stop-all.sh << 'STOPALL'
#!/bin/bash
echo "🛑 Arrêt de l'écosystème..."
pkill -f "backend/main.py" 2>/dev/null
pkill -f "gateway.py" 2>/dev/null
pkill -f "services/" 2>/dev/null
echo "✅ Écosystème arrêté"
STOPALL

chmod +x $BASE_DIR/scripts/*.sh

# ------------------------------------------------------------
# 5. NGINX CONFIGURATION
# ------------------------------------------------------------
sudo tee /etc/nginx/sites-available/osis > /dev/null << 'NGX'
server {
    listen 80;
    server_name _;
    location /api { proxy_pass http://127.0.0.1:8000; }
    location /docs { proxy_pass http://127.0.0.1:8000; }
    location / { proxy_pass http://127.0.0.1:8080; }
}
NGX
sudo ln -sf /etc/nginx/sites-available/osis /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx

# ------------------------------------------------------------
# FIN
# ------------------------------------------------------------
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                                                          ║"
echo -e "║   ${GREEN}🌲 OSIS vX.3 — INSTALLATION TERMINÉE !${NC}                  ║"
echo "║                                                          ║"
echo "║   🔧 Backend  : http://localhost:8000                   ║"
echo "║   🎨 Frontend : http://localhost:3000                   ║"
echo "║   🌐 Gateway  : http://localhost:8080                   ║"
echo "║                                                          ║"
echo "║   🚀 /scripts/start-all.sh                              ║"
echo "╚══════════════════════════════════════════════════════════╝"