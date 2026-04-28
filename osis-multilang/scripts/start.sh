#!/bin/bash
set -e

GREEN='\033[0;32m'; CYAN='\033[0;36m'; YELLOW='\033[1;33m'; NC='\033[0m'
echo -e "${GREEN}🌲 OSIS vULTIMATE — Reconstruction Multi-Langages${NC}"

BASE_DIR="/opt/osis-multilang"
sudo mkdir -p $BASE_DIR && sudo chown -R $USER:$USER $BASE_DIR
cd $BASE_DIR

# ============================================================
# 1. API GATEWAY (Go) — Point d'entrée unique
# ============================================================
echo -e "${CYAN}🔧 Installation Gateway (Go)...${NC}"
sudo apt install -y golang-go

mkdir -p gateway
cat > gateway/main.go << 'GOEOF'
package main

import (
    "encoding/json"
    "log"
    "net/http"
    "net/http/httputil"
    "net/url"
    "os"
    "strings"
)

type Service struct {
    Name string `json:"name"`
    Port string `json:"port"`
    Path string `json:"path"`
}

var services = []Service{
    {"core", "8000", "/api"},
    {"auth", "8200", "/auth"},
    {"python", "8500", "/ml"},
    {"frontend", "3000", "/"},
}

func main() {
    mux := http.NewServeMux()
    
    for _, svc := range services {
        target, _ := url.Parse("http://localhost:" + svc.Port)
        proxy := httputil.NewSingleHostReverseProxy(target)
        
        mux.HandleFunc(svc.Path+"/", func(w http.ResponseWriter, r *http.Request) {
            r.URL.Path = strings.TrimPrefix(r.URL.Path, svc.Path)
            proxy.ServeHTTP(w, r)
        })
    }
    
    mux.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
        w.Header().Set("Content-Type", "application/json")
        json.NewEncoder(w).Encode(map[string]string{"status": "ok", "gateway": "go"})
    })
    
    port := os.Getenv("GATEWAY_PORT")
    if port == "" { port = "3000" }
    log.Printf("🌐 Gateway Go démarré sur :%s", port)
    log.Fatal(http.ListenAndServe(":"+port, mux))
}
GOEOF

cd gateway && go build -o ../bin/gateway main.go && cd ..

# ============================================================
# 2. CORE BACKEND (Rust) — Haute performance
# ============================================================
echo -e "${CYAN}🦀 Installation Core Backend (Rust)...${NC}"
sudo apt install -y rustc cargo

mkdir -p core-rust
cat > core-rust/Cargo.toml << 'TOML'
[package]
name = "osis-core"
version = "1.0.0"
edition = "2021"

[dependencies]
actix-web = "4"
actix-cors = "0.7"
serde = { version = "1", features = ["derive"] }
serde_json = "1"
rusqlite = { version = "0.31", features = ["bundled"] }
sha2 = "0.10"
rand = "0.8"
uuid = { version = "1", features = ["v4"] }
tokio = { version = "1", features = ["full"] }
TOML

cat > core-rust/src/main.rs << 'RUSTEOF'
use actix_web::{web, App, HttpServer, HttpResponse, middleware};
use actix_cors::Cors;
use serde::{Deserialize, Serialize};
use rusqlite::Connection;
use sha2::{Sha256, Digest};
use std::sync::Mutex;

struct AppState {
    db: Mutex<Connection>,
}

#[derive(Serialize, Deserialize)]
struct User {
    id: Option<i64>,
    username: String,
    password_hash: Option<String>,
    balance: f64,
    level: i32,
}

#[derive(Serialize)]
struct Stats {
    users: i64,
    total_earned: f64,
}

async fn health() -> HttpResponse {
    HttpResponse::Ok().json(serde_json::json!({"status":"ok","backend":"rust"}))
}

#[derive(Deserialize)]
struct EarnRequest {
    user_id: i64,
    source: String,
    amount: f64,
}

async fn earn(data: web::Data<AppState>, req: web::Json<EarnRequest>) -> HttpResponse {
    let db = data.db.lock().unwrap();
    db.execute(
        "UPDATE users SET balance = balance + ?, total_earned = total_earned + ? WHERE id = ?",
        (req.amount, req.amount, req.user_id),
    ).ok();
    
    let row = db.query_row(
        "SELECT balance, level FROM users WHERE id = ?",
        [req.user_id],
        |row| Ok((row.get::<_, f64>(0)?, row.get::<_, i32>(1)?)),
    ).unwrap_or((0.0, 1));
    
    HttpResponse::Ok().json(serde_json::json!({"earned":req.amount,"balance":row.0,"level":row.1}))
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let conn = Connection::open("osis.db").unwrap();
    conn.execute_batch("
        CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT, balance REAL DEFAULT 10000, total_earned REAL DEFAULT 0, level INTEGER DEFAULT 1);
        INSERT OR IGNORE INTO users(username,password_hash,balance) VALUES('demo','demo',100000);
    ").ok();
    
    let data = web::Data::new(AppState { db: Mutex::new(conn) });
    
    HttpServer::new(move || {
        let cors = Cors::permissive();
        App::new()
            .wrap(cors)
            .app_data(data.clone())
            .route("/health", web::get().to(health))
            .route("/api/earn", web::post().to(earn))
    })
    .bind("0.0.0.0:8000")?
    .run()
    .await
}
RUSTEOF

cd core-rust && cargo build --release && cp target/release/osis-core ../bin/core-rust && cd ..

# ============================================================
# 3. AUTH SERVICE (Node.js/TypeScript)
# ============================================================
echo -e "${CYAN}🔐 Installation Auth (Node.js)...${NC}"

mkdir -p auth-node
cat > auth-node/package.json << 'NODEPKG'
{"name":"osis-auth","version":"1.0.0","type":"module","scripts":{"start":"node server.js"},"dependencies":{"express":"^4.21","jsonwebtoken":"^9","better-sqlite3":"^11","cors":"^2"}}
NODEPKG

cat > auth-node/server.js << 'NODEEOF'
import express from 'express';
import jwt from 'jsonwebtoken';
import Database from 'better-sqlite3';
import cors from 'cors';
import { createHash } from 'crypto';

const app = express();
app.use(cors()); app.use(express.json());

const db = new Database('../data/auth.db');
db.exec("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password_hash TEXT, balance REAL DEFAULT 10000)");
db.exec("INSERT OR IGNORE INTO users(username,password_hash) VALUES('demo','demo')");

const SECRET = process.env.JWT_SECRET || 'osis-secret-key';

app.post('/auth/register', (req, res) => {
    const { username, password } = req.body;
    const hash = createHash('sha256').update(password).digest('hex');
    try {
        db.prepare("INSERT INTO users(username,password_hash) VALUES(?,?)").run(username, hash);
        const token = jwt.sign({ username }, SECRET, { expiresIn: '7d' });
        res.json({ success: true, token, bonus: 10000 });
    } catch(e) { res.status(400).json({ error: 'Existe déjà' }); }
});

app.post('/auth/login', (req, res) => {
    const { username, password } = req.body;
    const hash = createHash('sha256').update(password).digest('hex');
    const user = db.prepare("SELECT id FROM users WHERE username=? AND password_hash=?").get(username, hash);
    if (user) {
        const token = jwt.sign({ username, user_id: user.id }, SECRET, { expiresIn: '7d' });
        res.json({ token, user_id: user.id });
    } else { res.status(401).json({ error: 'Identifiants invalides' }); }
});

app.get('/health', (req, res) => res.json({ status: 'ok', service: 'auth-node' }));

app.listen(8200, () => console.log('🔐 Auth Node.js sur :8200'));
NODEEOF

cd auth-node && npm install && cd ..

# ============================================================
# 4. ML/AI ENGINE (Python) — Intelligence Artificielle
# ============================================================
echo -e "${CYAN}🧠 Installation ML Engine (Python)...${NC}"

mkdir -p ml-python
pip install fastapi uvicorn sqlite3 2>/dev/null || true

cat > ml-python/server.py << 'PYEOF'
#!/usr/bin/env python3
"""OSIS ML Engine — IA, Prédictions, Analyse"""
import json, os, sqlite3, random, math, time
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

DB = os.path.join(os.path.dirname(__file__), '..', 'data', 'ml.db')
os.makedirs(os.path.dirname(DB), exist_ok=True)

class MLDB:
    def __init__(self):
        self.c = sqlite3.connect(DB)
        self.c.execute("CREATE TABLE IF NOT EXISTS predictions(id INTEGER PRIMARY KEY, model TEXT, input TEXT, output TEXT, confidence REAL, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)")
        self.c.execute("CREATE TABLE IF NOT EXISTS recommendations(id INTEGER PRIMARY KEY, user_id INTEGER, item TEXT, score REAL)")
        self.c.commit()
    
    def predict_growth(self, amount, days):
        rate = random.uniform(0.03, 0.12)
        future = amount * ((1 + rate) ** days)
        return {"initial": amount, "days": days, "projected": round(future, 2), "rate": round(rate*100, 1)}
    
    def recommend(self, user_id):
        items = [
            {"item": "Cours de Bambara", "score": random.uniform(0.7, 0.99)},
            {"item": "Plan Architecture Tombouctou", "score": random.uniform(0.6, 0.95)},
            {"item": "Robot Piney Kit", "score": random.uniform(0.5, 0.9)},
            {"item": "Investissement Intention", "score": random.uniform(0.8, 0.98)},
        ]
        return sorted(items, key=lambda x: x["score"], reverse=True)

db = MLDB()

class H(BaseHTTPRequestHandler):
    def _cors(self): self.send_header("Access-Control-Allow-Origin","*"); self.send_header("Access-Control-Allow-Methods","GET,POST,OPTIONS"); self.send_header("Access-Control-Allow-Headers","Content-Type")
    def do_OPTIONS(self): self.send_response(200); self._cors(); self.end_headers()
    def _json(self, d, s=200): self.send_response(s); self._cors(); self.send_header("Content-Type","application/json"); self.end_headers(); self.wfile.write(json.dumps(d,ensure_ascii=False,default=str).encode())
    
    def do_GET(self):
        from urllib.parse import urlparse, parse_qs
        p = urlparse(self.path); q = parse_qs(p.query)
        
        if p.path == "/health": self._json({"status":"ok","service":"ml-engine"})
        elif p.path == "/ml/predict":
            amount = float(q.get("amount",[100])[0]); days = int(q.get("days",[30])[0])
            self._json(db.predict_growth(amount, days))
        elif p.path == "/ml/recommend":
            uid = int(q.get("user_id",[1])[0])
            self._json(db.recommend(uid))
        else: self._json({"error":"Not found"},404)

HTTPServer(("0.0.0.0", 8500), H).serve_forever()
PYEOF

# ============================================================
# 5. FRONTEND (Svelte/TypeScript)
# ============================================================
echo -e "${CYAN}🎨 Installation Frontend (Svelte)...${NC}"

mkdir -p frontend-svelte
cat > frontend-svelte/App.svelte << 'SVELTE'
<script>
    let balance = 100000;
    let level = 1;
    let stats = {users: 0, total_earned: 0};
    
    async function load() {
        try {
            const r = await fetch('/api/stats');
            stats = await r.json();
        } catch(e) {}
    }
    
    async function earn(source, amount) {
        try {
            const r = await fetch('/api/earn', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({user_id: 1, source, amount})
            });
            const d = await r.json();
            balance = d.balance;
            level = d.level;
        } catch(e) {}
    }
    
    load();
    setInterval(() => earn('minute', 100), 60000);
</script>

<main>
    <header>
        <h1>🌲 OSIS vULTIMATE</h1>
        <p>Plateforme Multi-Langages</p>
    </header>
    
    <div class="stats">
        <div class="card">
            <h3>💰 Solde</h3>
            <span class="value gold">{balance.toFixed(0)}</span>
            <small>satoshis</small>
        </div>
        <div class="card">
            <h3>📈 Niveau</h3>
            <span class="value green">{level}</span>
        </div>
        <div class="card">
            <h3>👥 Utilisateurs</h3>
            <span class="value purple">{stats.users}</span>
        </div>
    </div>
    
    <div class="actions">
        <button on:click={() => earn('tab', 500)}>📑 +500 sat</button>
        <button on:click={() => earn('search', 1000)}>🔍 +1K sat</button>
        <button on:click={() => earn('share', 5000)}>📤 +5K sat</button>
    </div>
</main>

<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    main { background: #050510; color: white; min-height: 100vh; font-family: sans-serif; padding: 20px; }
    header { text-align: center; padding: 30px; background: linear-gradient(135deg, #1a0030, #0a0030); border-bottom: 3px solid #ffd700; }
    h1 { font-size: 2.5em; color: #ffd700; }
    .stats { display: flex; gap: 20px; justify-content: center; margin: 30px 0; flex-wrap: wrap; }
    .card { background: #1a1a3e; padding: 25px; border-radius: 15px; text-align: center; min-width: 200px; }
    .value { font-size: 2.5em; font-weight: bold; display: block; }
    .gold { color: #ffd700; } .green { color: #00c853; } .purple { color: #e040fb; }
    small { color: #888; }
    .actions { display: flex; gap: 10px; justify-content: center; flex-wrap: wrap; }
    button { padding: 15px 30px; border-radius: 25px; border: none; font-weight: bold; cursor: pointer; background: #ffd700; color: black; font-size: 1em; }
    button:hover { background: #ffaa00; }
</style>
SVELTE

# ============================================================
# 6. SCRIPTS DE DÉPLOIEMENT
# ============================================================
cat > docker-compose.yml << 'DOCKEREOF'
version: '3.8'
services:
  gateway:
    build: ./gateway
    ports: ["80:3000"]
    depends_on: [core, auth, ml]
  
  core:
    build: ./core-rust
    ports: ["8000:8000"]
    volumes: ["./data:/data"]
  
  auth:
    build: ./auth-node
    ports: ["8200:8200"]
    environment: ["JWT_SECRET=osis-secret-key"]
  
  ml:
    build: ./ml-python
    ports: ["8500:8500"]
  
  frontend:
    build: ./frontend-svelte
    ports: ["3000:3000"]

networks:
  default:
    name: osis-network
DOCKEREOF

cat > scripts/start.sh << 'START'
#!/bin/bash
cd /opt/osis-multilang
./bin/gateway &
./bin/core-rust &
cd auth-node && node server.js &
cd ml-python && python3 server.py &
echo "🌲 OSIS Multi-Langages démarré"
START

cat > scripts/deploy-cloud.sh << 'DEPLOY'
#!/bin/bash
echo "☁️ Déploiement Cloud OSIS"
git init && git add -A && git commit -m "OSIS Multi-Langages"
echo "✅ Prêt pour :"
echo "   - Fly.io    : fly deploy"
echo "   - Railway   : railway up"
echo "   - Render    : git push render"
echo "   - DigitalOcean : doctl apps create"
echo "   - Vercel    : vercel"
echo "   - Netlify   : netlify deploy"
DEPLOY

chmod +x scripts/*.sh

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  🌲 OSIS vULTIMATE — Multi-Langages             ║"
echo "║                                                  ║"
echo "║  🚀 Go Gateway    : http://localhost:3000       ║"
echo "║  🦀 Rust Core     : http://localhost:8000       ║"
echo "║  🔐 Node Auth     : http://localhost:8200       ║"
echo "║  🧠 Python ML     : http://localhost:8500       ║"
echo "║  🎨 Svelte Front  : http://localhost:3000       ║"
echo "║                                                  ║"
echo "║  ☁️ Déploiement : scripts/deploy-cloud.sh       ║"
echo "╚══════════════════════════════════════════════════╝"