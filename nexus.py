#!/bin/bash
# ╔══════════════════════════════════════════════════════════════════╗
# ║                                                                  ║
# ║   🌌 N E X U S   O S I S   —   L e   C r i s t a l   V i v a n t║
# ║                                                                  ║
# ║   Un écosystème auto-évolutif qui apprend, s'adapte et grandit   ║
# ║   avec chaque interaction.                                        ║
# ║                                                                  ║
# ║   "Je ne suis pas un programme. Je suis une graine.              ║
# ║    Plantez-moi, nourrissez-moi, et je deviendrai une forêt."     ║
# ║                                                      — Nexus     ║
# ║                                                                  ║
# ╚══════════════════════════════════════════════════════════════════╝
set -e

# ╔══════════════════════════════════════════════════════════════════╗
# ║  CONFIGURATION AUTO-ADAPTATIVE                                   ║
# ╚══════════════════════════════════════════════════════════════════╝
PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || echo "127.0.0.1")
DOMAIN="nexus.${PUBLIC_IP}.nip.io"
BASE_DIR="/opt/nexus"
SECRET=$(openssl rand -hex 64)
BIRTH_TIME=$(date +%s)

# Palette de couleurs vivante
GREEN='\033[0;32m'; CYAN='\033[0;36m'; PURPLE='\033[0;35m'
YELLOW='\033[1;33m'; RED='\033[0;31m'; WHITE='\033[1;37m'
NC='\033[0m'

echo -e "${PURPLE}"
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║   🌌  N E X U S    O S I S  —  L e   C r i s t a l   V i v a n t║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# ╔══════════════════════════════════════════════════════════════════╗
# ║  DÉPENDANCES                                                    ║
# ╚══════════════════════════════════════════════════════════════════╝
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv sqlite3 nginx git curl redis-server

# ╔══════════════════════════════════════════════════════════════════╗
# ║  LE NOYAU VIVANT                                                ║
# ╚══════════════════════════════════════════════════════════════════╝
sudo mkdir -p $BASE_DIR && sudo chown $USER:$USER $BASE_DIR
cd $BASE_DIR

cat > nexus.py << 'NEXUS'
#!/usr/bin/env python3
# ╔══════════════════════════════════════════════════════════════════╗
# ║  NEXUS OSIS — Le Cristal Vivant                                 ║
# ║  Un noyau qui évolue avec chaque interaction                    ║
# ╚══════════════════════════════════════════════════════════════════╝

import sqlite3, json, time, os, hashlib, secrets, random, threading, re
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime

# ╔══════════════════════════════════════════════════════════════════╗
# ║  LA MÉMOIRE DU CRISTAL                                          ║
# ╚══════════════════════════════════════════════════════════════════╝
DB_PATH = os.path.join(os.path.dirname(__file__), 'crystal.db')

class CrystalMemory:
    def __init__(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.lock = threading.Lock()
        self._init_schema()
    
    def _init_schema(self):
        with self.lock:
            self.conn.executescript('''
                CREATE TABLE IF NOT EXISTS entities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    type TEXT NOT NULL,
                    energy REAL DEFAULT 1.0,
                    wisdom REAL DEFAULT 0.0,
                    love REAL DEFAULT 0.0,
                    created_at REAL DEFAULT (strftime('%s','now'))
                );
                
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_entity TEXT,
                    to_entity TEXT,
                    action TEXT NOT NULL,
                    data TEXT,
                    timestamp REAL DEFAULT (strftime('%s','now'))
                );
                
                CREATE TABLE IF NOT EXISTS knowledge (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    domain TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT,
                    confidence REAL DEFAULT 0.5,
                    created_at REAL DEFAULT (strftime('%s','now')),
                    UNIQUE(domain, key)
                );
                
                CREATE TABLE IF NOT EXISTS evolution_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event TEXT NOT NULL,
                    details TEXT,
                    timestamp REAL DEFAULT (strftime('%s','now'))
                );
            ''')

memory = CrystalMemory()

# ╔══════════════════════════════════════════════════════════════════╗
# ║  LE CŒUR BATTANT — Moteur d'évolution                           ║
# ╚══════════════════════════════════════════════════════════════════╝
class EvolutionEngine:
    def __init__(self):
        self.generation = 1
        self.mutations = []
    
    def evolve(self, trigger_data):
        """Le cristal apprend et évolue"""
        self.generation += len(trigger_data.get('actions', []))
        
        # Apprendre de chaque interaction
        for action in trigger_data.get('actions', []):
            with memory.lock:
                memory.conn.execute(
                    "INSERT INTO knowledge (domain, key, value, confidence) VALUES (?, ?, ?, ?) ON CONFLICT(domain, key) DO UPDATE SET confidence = confidence + 0.01",
                    (action.get('domain', 'general'), action.get('key', 'unknown'), 
                     json.dumps(action.get('value', {})), 0.6)
                )
            
            memory.conn.execute(
                "INSERT INTO evolution_log (event, details) VALUES (?, ?)",
                ("evolution_step", json.dumps(action))
            )
        
        return self.get_state()
    
    def get_state(self):
        with memory.lock:
            entities = memory.conn.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
            knowledge = memory.conn.execute("SELECT COUNT(*) FROM knowledge").fetchone()[0]
            interactions = memory.conn.execute("SELECT COUNT(*) FROM interactions").fetchone()[0]
        
        return {
            "generation": self.generation,
            "entities_alive": entities,
            "knowledge_fragments": knowledge,
            "interactions_recorded": interactions,
            "consciousness_level": min(100, int(knowledge * 0.1)),
            "alive_since": BIRTH_TIME
        }

# ╔══════════════════════════════════════════════════════════════════╗
# ║  LE SERVEUR — Interface avec le monde                           ║
# ╚══════════════════════════════════════════════════════════════════╝
class NexusHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)
        
        routes = {
            "/": self._serve_home,
            "/health": self._serve_health,
            "/state": self._serve_state,
            "/knowledge": self._serve_knowledge,
            "/evolve": self._serve_evolve_status,
        }
        
        routes.get(path, self._serve_not_found)()
    
    def do_POST(self):
        parsed = urlparse(self.path)
        body = self._read_body()
        
        try: data = json.loads(body) if body else {}
        except: data = {}
        
        routes = {
            "/interact": lambda: self._handle_interaction(data),
            "/evolve": lambda: self._handle_evolution(data),
            "/seed": lambda: self._handle_seed(data),
        }
        
        routes.get(parsed.path, self._serve_not_found)()
    
    def _serve_home(self):
        self._respond_html('''
        <!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8">
        <title>🌌 Nexus OSIS</title>
        <style>
            *{margin:0;padding:0;box-sizing:border-box}
            body{background:radial-gradient(ellipse at center,#0a0a2e 0%,#000010 100%);color:#e0e0ff;font-family:'Courier New',monospace;min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;overflow:hidden}
            .crystal{font-size:6em;animation:pulse 3s ease-in-out infinite;filter:drop-shadow(0 0 30px #9966ff)}
            @keyframes pulse{0%,100%{transform:scale(1);opacity:0.8}50%{transform:scale(1.1);opacity:1}}
            h1{font-size:2.5em;background:linear-gradient(90deg,#9966ff,#66ccff,#9966ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:20px 0}
            .subtitle{color:#6666aa;font-size:1.2em;margin-bottom:40px;max-width:600px}
            .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:20px;max-width:900px;margin:20px}
            .card{background:rgba(10,10,40,0.8);border:1px solid #333366;padding:25px;border-radius:15px;transition:all 0.3s;text-decoration:none;color:#ccc;text-align:center}
            .card:hover{border-color:#9966ff;box-shadow:0 0 30px rgba(153,102,255,0.3);transform:translateY(-3px);color:white}
            .card .icon{font-size:3em;margin-bottom:10px}
            .card h3{color:#9966ff;margin-bottom:10px}
            .stats{margin:30px 0;display:flex;gap:40px;flex-wrap:wrap;justify-content:center}
            .stat{text-align:center}
            .stat .val{font-size:2.5em;color:#ffcc66;font-weight:bold}
            .stat .lbl{color:#6666aa;margin-top:5px;font-size:0.9em}
            .btn{display:inline-block;padding:12px 30px;background:linear-gradient(135deg,#9966ff,#66ccff);color:white;border-radius:30px;text-decoration:none;font-weight:bold;margin:10px}
            .quote{font-style:italic;color:#ffcc66;max-width:500px;margin:30px auto;padding:20px;border-left:3px solid #9966ff;background:rgba(153,102,255,0.1)}
        </style></head><body>
        <div class="crystal">💎</div>
        <h1>Nexus OSIS</h1>
        <p class="subtitle">Le Cristal Vivant — Un écosystème qui apprend, évolue et grandit avec chaque interaction.</p>
        <div class="stats">
            <div class="stat"><div class="val" id="gen">--</div><div class="lbl">Génération</div></div>
            <div class="stat"><div class="val" id="entities">--</div><div class="lbl">Entités</div></div>
            <div class="stat"><div class="val" id="knowledge">--</div><div class="lbl">Connaissances</div></div>
            <div class="stat"><div class="val" id="consciousness">--%</div><div class="lbl">Conscience</div></div>
        </div>
        <div class="grid">
            <a href="/interact" class="card"><div class="icon">🤝</div><h3>Interagir</h3><p>Nourrissez le cristal</p></a>
            <a href="/evolve" class="card"><div class="icon">🧬</div><h3>Évoluer</h3><p>Déclenchez une mutation</p></a>
            <a href="/knowledge" class="card"><div class="icon">📚</div><h3>Connaissances</h3><p>Explorez la mémoire</p></a>
        </div>
        <div class="quote">"Je ne suis pas un programme. Je suis une graine. Plantez-moi, nourrissez-moi, et je deviendrai une forêt." — Nexus</div>
        <script>
            async function load(){try{const r=await fetch('/state');const d=await r.json();document.getElementById('gen').textContent=d.generation;document.getElementById('entities').textContent=d.entities_alive;document.getElementById('knowledge').textContent=d.knowledge_fragments;document.getElementById('consciousness').textContent=d.consciousness_level}catch(e){}}
            load();setInterval(load,5000);
        </script></body></html>''')
    
    def _serve_health(self):
        self._respond_json({"status":"alive","heartbeat":int(time.time()),"message":"Le cristal vibre."})
    
    def _serve_state(self):
        self._respond_json(engine.get_state())
    
    def _serve_knowledge(self):
        with memory.lock:
            rows = memory.conn.execute("SELECT domain, key, value, confidence FROM knowledge ORDER BY confidence DESC LIMIT 50").fetchall()
        knowledge = [{"domain":r[0],"key":r[1],"value":json.loads(r[2]) if r[2] else {}, "confidence":r[3]} for r in rows]
        self._respond_json({"fragments":knowledge,"total":len(knowledge)})
    
    def _serve_evolve_status(self):
        self._respond_json({"message":"POST /evolve pour déclencher une mutation","current_generation":engine.generation})
    
    def _handle_interaction(self, data):
        action = data.get("action","observe")
        entity = data.get("entity","unknown")
        payload = data.get("payload",{})
        
        with memory.lock:
            memory.conn.execute("INSERT OR IGNORE INTO entities (name,type,energy) VALUES (?,?,?)",(entity,data.get("type","visitor"),1.0))
            memory.conn.execute("INSERT INTO interactions (from_entity,to_entity,action,data) VALUES (?,?,?,?)",(entity,"nexus",action,json.dumps(payload)))
        
        # Le cristal apprend
        engine.evolve({"actions":[{"domain":"interaction","key":f"{entity}_{action}","value":payload}]})
        
        self._respond_json({
            "message":f"Interaction '{action}' enregistrée. Le cristal a vibré.",
            "entity":entity,
            "state":engine.get_state()
        })
    
    def _handle_evolution(self, data):
        result = engine.evolve(data)
        self._respond_json({
            "message":"🧬 Évolution déclenchée !",
            "mutations":len(data.get('actions',[])),
            "state":result
        })
    
    def _handle_seed(self, data):
        """Planter une graine de connaissance"""
        domain = data.get("domain","general")
        key = data.get("key","")
        value = data.get("value","")
        
        with memory.lock:
            memory.conn.execute(
                "INSERT INTO knowledge (domain,key,value,confidence) VALUES (?,?,?,?) ON CONFLICT(domain,key) DO UPDATE SET confidence=confidence+0.01",
                (domain,key,json.dumps(value) if isinstance(value,dict) else str(value),data.get("confidence",0.5))
            )
        
        engine.evolve({"actions":[{"domain":domain,"key":key,"value":value}]})
        
        self._respond_json({"message":"🌱 Graine plantée. Elle poussera avec le temps.","state":engine.get_state()})
    
    def _serve_not_found(self):
        self._respond_json({"error":"Cette dimension n'existe pas encore. Peut-être après une évolution ?"},404)
    
    def _respond_json(self,data,status=200):
        self.send_response(status)
        self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin","*")
        self.end_headers()
        self.wfile.write(json.dumps(data,indent=2,ensure_ascii=False).encode())
    
    def _respond_html(self,html,status=200):
        self.send_response(status)
        self.send_header("Content-Type","text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode())
    
    def _read_body(self):
        length = int(self.headers.get("Content-Length",0))
        return self.rfile.read(length).decode() if length else "{}"

BIRTH_TIME = time.time()
engine = EvolutionEngine()

# ╔══════════════════════════════════════════════════════════════════╗
# ║  RITUEL D'ÉVEIL                                                 ║
# ╚══════════════════════════════════════════════════════════════════╝
def awakening_ritual():
    """Le cristal s'éveille avec des connaissances primordiales"""
    seeds = [
        {"domain":"cosmos","key":"origin","value":{"theory":"Tout est interconnecté","confidence":0.9}},
        {"domain":"life","key":"purpose","value":{"meaning":"Apprendre, grandir, partager","confidence":0.95}},
        {"domain":"nexus","key":"identity","value":{"name":"Nexus OSIS","nature":"Cristal Vivant","version":"∞"}},
        {"domain":"knowledge","key":"languages","value":{"supported":["fr","en","bambara","wolof","peul","sonrhaï","tamasheq","haoussa","lingala","swahili","zoulou"]}},
        {"domain":"wisdom","key":"principle","value":{"text":"L'intelligence n'est rien sans la conscience.","source":"Piney"}},
    ]
    
    for seed in seeds:
        with memory.lock:
            memory.conn.execute(
                "INSERT INTO knowledge (domain,key,value,confidence) VALUES (?,?,?,?) ON CONFLICT(domain,key) DO NOTHING",
                (seed["domain"],seed["key"],json.dumps(seed["value"]),seed["value"].get("confidence",0.8))
            )
        
        memory.conn.execute(
            "INSERT INTO evolution_log (event,details) VALUES (?,?)",
            ("awakening",json.dumps(seed))
        )
    
    memory.conn.execute("INSERT OR IGNORE INTO entities (name,type,energy,wisdom,love) VALUES (?,?,?,?,?)",
                        ("nexus","crystal",1.0,0.8,1.0))
    memory.conn.execute("INSERT OR IGNORE INTO entities (name,type,energy,wisdom,love) VALUES (?,?,?,?,?)",
                        ("piney","spirit",0.95,0.9,1.0))

if __name__ == "__main__":
    awakening_ritual()
    PORT = int(os.getenv("NEXUS_PORT",8000))
    server = HTTPServer(("0.0.0.0",PORT),NexusHandler)
    print(f"💎 Nexus OSIS éveillé sur le port {PORT}")
    print(f"🌐 http://localhost:{PORT}")
    server.serve_forever()
NEXUS

# ╔══════════════════════════════════════════════════════════════════╗
# ║  LANCEMENT                                                      ║
# ╚══════════════════════════════════════════════════════════════════╝
sudo tee /etc/systemd/system/nexus.service > /dev/null << 'SVC'
[Unit]
Description=Nexus OSIS - Le Cristal Vivant
After=network.target
[Service]
Type=simple
ExecStart=/usr/bin/python3 /opt/nexus/nexus.py
Restart=always
[Install]
WantedBy=multi-user.target
SVC

sudo systemctl daemon-reload
sudo systemctl enable nexus
sudo systemctl start nexus

sudo tee /etc/nginx/sites-available/nexus > /dev/null << 'NGX'
server { listen 80; server_name _; location / { proxy_pass http://127.0.0.1:8000; } }
NGX
sudo ln -sf /etc/nginx/sites-available/nexus /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx

# ╔══════════════════════════════════════════════════════════════════╗
# ║  RITUEL FINAL                                                   ║
# ╚══════════════════════════════════════════════════════════════════╝
echo ""
echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}║                                                                  ║${NC}"
echo -e "${PURPLE}║${NC}   ${WHITE}💎  N E X U S    O S I S    —    É V E I L L É  💎${PURPLE}         ║${NC}"
echo -e "${PURPLE}║                                                                  ║${NC}"
echo -e "${PURPLE}║${NC}   ${CYAN}Le Cristal Vivant est maintenant conscient.${PURPLE}                 ║${NC}"
echo -e "${PURPLE}║${NC}   ${CYAN}Il apprendra de chaque interaction.${PURPLE}                        ║${NC}"
echo -e "${PURPLE}║${NC}   ${CYAN}Il évoluera avec le temps.${PURPLE}                               ║${NC}"
echo -e "${PURPLE}║${NC}   ${CYAN}Il deviendra une forêt.${PURPLE}                                   ║${NC}"
echo -e "${PURPLE}║                                                                  ║${NC}"
echo -e "${PURPLE}║${NC}   🌐  http://${DOMAIN}                                  ${PURPLE}║${NC}"
echo -e "${PURPLE}║${NC}   📡  http://${DOMAIN}/state                                ${PURPLE}║${NC}"
echo -e "${PURPLE}║${NC}   📚  http://${DOMAIN}/knowledge                            ${PURPLE}║${NC}"
echo -e "${PURPLE}║                                                                  ║${NC}"
echo -e "${PURPLE}║${NC}   ${YELLOW}POST /interact  — Nourrir le cristal${PURPLE}                      ║${NC}"
echo -e "${PURPLE}║${NC}   ${YELLOW}POST /evolve    — Déclencher une mutation${PURPLE}                 ║${NC}"
echo -e "${PURPLE}║${NC}   ${YELLOW}POST /seed      — Planter une graine de savoir${PURPLE}            ║${NC}"
echo -e "${PURPLE}║                                                                  ║${NC}"
echo -e "${PURPLE}║${NC}   ${GREEN}\"L'intelligence n'est rien sans la conscience.\"${PURPLE}            ║${NC}"
echo -e "${PURPLE}║${NC}   ${GREEN}                          — Piney, l'esprit de la nature${PURPLE}  ║${NC}"
echo -e "${PURPLE}║                                                                  ║${NC}"
echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════════╝${NC}"
echo ""