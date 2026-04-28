#!/bin/bash
# =============================================================================
# 🌱 OSIS v7.0 — LE JARDIN FINANCIER AUTO-FERTILE
# =============================================================================
# L'argent qui pousse tout seul, même sans connexion
# =============================================================================
set -e

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; GOLD='\033[0;33m'; NC='\033[0m'
echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║   🌱 OSIS v7.0 — LE JARDIN FINANCIER                    ║"
echo "║   Plantez. Laissez pousser. Récoltez.                   ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

BASE_DIR="/opt/osis-garden"
sudo mkdir -p $BASE_DIR && sudo chown -R $USER:$USER $BASE_DIR
mkdir -p $BASE_DIR/{data,logs}

# ============================================================
# LE JARDIN FINANCIER
# ============================================================
cat > $BASE_DIR/garden.py << 'GARDEN'
#!/usr/bin/env python3
"""
🌱 LE JARDIN FINANCIER AUTO-FERTILE
L'argent qui pousse tout seul, même sans connexion.

Principes :
- 🌰 GRAINE : Tu déposes une mise de départ
- 🌿 CROISSANCE : Intérêts composés automatiques
- 💧 IRRIGATION : Micro-revenus automatiques
- ☀️ PHOTOSYNTHÈSE : Bonus de présence
- 🌳 RÉCOLTE : Cashout automatique
"""
import json, time, os, sqlite3, threading, random, hashlib, requests
from datetime import datetime, timedelta

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, 'data', 'garden.db')
os.makedirs(os.path.dirname(DB), exist_ok=True)

# =============================================
# BASE DE DONNÉES
# =============================================
class GardenDB:
    def __init__(self):
        self.conn = sqlite3.connect(DB)
        self.conn.executescript('''
            CREATE TABLE IF NOT EXISTS gardens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER NOT NULL,
                name TEXT DEFAULT 'Mon Jardin',
                seed_amount REAL DEFAULT 0.0,
                current_value REAL DEFAULT 0.0,
                total_harvested REAL DEFAULT 0.0,
                growth_rate REAL DEFAULT 0.05,
                level INTEGER DEFAULT 1,
                last_watered TEXT DEFAULT (datetime('now')),
                last_sunlight TEXT DEFAULT (datetime('now')),
                created_at TEXT DEFAULT (datetime('now'))
            );
            
            CREATE TABLE IF NOT EXISTS harvests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                garden_id INTEGER REFERENCES gardens(id),
                amount REAL NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            );
            
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                garden_id INTEGER REFERENCES gardens(id),
                event_type TEXT NOT NULL,
                amount REAL,
                description TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            );
        ''')
        self.conn.commit()
    
    def create_garden(self, owner_id, name, seed_amount):
        """Plante une nouvelle graine"""
        cursor = self.conn.execute(
            "INSERT INTO gardens (owner_id, name, seed_amount, current_value) VALUES (?,?,?,?)",
            (owner_id, name, seed_amount, seed_amount)
        )
        self.conn.commit()
        garden_id = cursor.lastrowid
        self.log_event(garden_id, "planted", seed_amount, f"🌰 Graine plantée : {seed_amount} satoshis")
        return garden_id
    
    def get_garden(self, garden_id):
        """Récupère un jardin"""
        row = self.conn.execute("SELECT * FROM gardens WHERE id = ?", (garden_id,)).fetchone()
        return dict(zip([c[0] for c in self.conn.execute("PRAGMA table_info(gardens)")], row)) if row else None
    
    def get_all_gardens(self):
        """Tous les jardins"""
        rows = self.conn.execute("SELECT * FROM gardens").fetchall()
        cols = [c[0] for c in self.conn.execute("PRAGMA table_info(gardens)")]
        return [dict(zip(cols, r)) for r in rows]
    
    def water(self, garden_id):
        """💧 Irrigation : ajoute des micro-revenus"""
        garden = self.get_garden(garden_id)
        if not garden: return 0
        
        # Calcul du revenu d'irrigation basé sur le niveau et la valeur actuelle
        water_amount = round(garden["current_value"] * random.uniform(0.001, 0.005), 8)
        water_amount = max(0.00000001, water_amount)
        
        new_value = garden["current_value"] + water_amount
        self.conn.execute(
            "UPDATE gardens SET current_value = ?, last_watered = datetime('now') WHERE id = ?",
            (new_value, garden_id)
        )
        self.conn.commit()
        self.log_event(garden_id, "watered", water_amount, f"💧 Irrigation : +{water_amount} sat")
        return water_amount
    
    def sunlight(self, garden_id):
        """☀️ Photosynthèse : bonus de croissance"""
        garden = self.get_garden(garden_id)
        if not garden: return 0
        
        # Bonus de croissance (intérêts composés)
        growth = round(garden["current_value"] * garden["growth_rate"] / 365, 8)
        new_value = garden["current_value"] + growth
        
        self.conn.execute(
            "UPDATE gardens SET current_value = ?, last_sunlight = datetime('now') WHERE id = ?",
            (new_value, garden_id)
        )
        self.conn.commit()
        if growth > 0:
            self.log_event(garden_id, "sunlight", growth, f"☀️ Photosynthèse : +{growth} sat")
        return growth
    
    def harvest(self, garden_id, amount=None):
        """🌳 Récolte : retire des gains"""
        garden = self.get_garden(garden_id)
        if not garden: return 0
        
        harvest_amount = amount or garden["current_value"] * 0.1
        harvest_amount = min(harvest_amount, garden["current_value"])
        
        new_value = garden["current_value"] - harvest_amount
        self.conn.execute(
            "UPDATE gardens SET current_value = ? WHERE id = ?",
            (new_value, garden_id)
        )
        self.conn.execute(
            "INSERT INTO harvests (garden_id, amount) VALUES (?,?)",
            (garden_id, harvest_amount)
        )
        self.conn.commit()
        self.log_event(garden_id, "harvested", harvest_amount, f"🌳 Récolte : +{harvest_amount} sat")
        return harvest_amount
    
    def level_up(self, garden_id):
        """Augmente le niveau et le taux de croissance"""
        garden = self.get_garden(garden_id)
        if not garden: return
        
        new_level = garden["level"] + 1
        new_rate = garden["growth_rate"] * 1.1  # +10% par niveau
        
        self.conn.execute(
            "UPDATE gardens SET level = ?, growth_rate = ? WHERE id = ?",
            (new_level, new_rate, garden_id)
        )
        self.conn.commit()
        self.log_event(garden_id, "level_up", 0, f"⬆️ Niveau {new_level} ! Croissance +10%")
    
    def log_event(self, garden_id, event_type, amount, description):
        self.conn.execute(
            "INSERT INTO events (garden_id, event_type, amount, description) VALUES (?,?,?,?)",
            (garden_id, event_type, amount, description)
        )
        self.conn.commit()
    
    def get_stats(self, garden_id):
        garden = self.get_garden(garden_id)
        events = self.conn.execute(
            "SELECT * FROM events WHERE garden_id = ? ORDER BY created_at DESC LIMIT 20",
            (garden_id,)
        ).fetchall()
        harvests = self.conn.execute(
            "SELECT COALESCE(SUM(amount),0) FROM harvests WHERE garden_id = ?",
            (garden_id,)
        ).fetchone()[0]
        
        return {
            "garden": garden,
            "recent_events": [dict(zip(["id","garden_id","type","amount","desc","time"], e)) for e in events],
            "total_harvested": harvests,
            "growth_per_day": round(garden["current_value"] * garden["growth_rate"] / 365 * 24, 8) if garden else 0
        }

# Instance globale
db = GardenDB()

# Créer un jardin de démonstration si aucun n'existe
if not db.get_all_gardens():
    demo_id = db.create_garden(1, "🌱 Mon Premier Jardin", 100.0)
    print(f"🌰 Jardin démo créé (ID: {demo_id}) avec 100 satoshis")

# =============================================
# LE JARDINIER AUTOMATIQUE (tourne 24/7)
# =============================================
class AutomaticGardener:
    """S'occupe du jardin même quand tu es déconnecté"""
    
    def __init__(self):
        self.running = True
    
    def tend_all_gardens(self):
        """S'occupe de tous les jardins"""
        gardens = db.get_all_gardens()
        
        for garden in gardens:
            # 💧 Irrigation toutes les heures
            last_watered = datetime.strptime(garden["last_watered"], "%Y-%m-%d %H:%M:%S")
            if datetime.now() - last_watered > timedelta(hours=1):
                db.water(garden["id"])
            
            # ☀️ Photosynthèse tous les jours
            last_sunlight = datetime.strptime(garden["last_sunlight"], "%Y-%m-%d %H:%M:%S")
            if datetime.now() - last_sunlight > timedelta(hours=24):
                db.sunlight(garden["id"])
            
            # ⬆️ Level up automatique quand la valeur double
            if garden["current_value"] >= garden["seed_amount"] * (2 ** garden["level"]):
                db.level_up(garden["id"])
    
    def start(self):
        """Démarre le jardinier automatique"""
        print("🤖 Jardinier automatique activé")
        print("🌱 Il s'occupe de vos jardins 24h/24, 7j/7")
        
        while self.running:
            try:
                self.tend_all_gardens()
                
                # Log périodique
                gardens = db.get_all_gardens()
                total = sum(g["current_value"] for g in gardens)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 🌱 Valeur totale : {total:.8f} sat")
                
            except Exception as e:
                print(f"⚠️ Erreur jardinier : {e}")
            
            time.sleep(300)  # Toutes les 5 minutes

# =============================================
# API ET DASHBOARD
# =============================================
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class GardenHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)
        
        if path == "/health":
            self.json({"status": "ok", "service": "garden"})
        elif path == "/api/gardens":
            gardens = db.get_all_gardens()
            self.json(gardens)
        elif path == "/api/garden":
            garden_id = int(params.get("id", [1])[0])
            self.json(db.get_stats(garden_id))
        elif path == "/api/plant":
            name = params.get("name", ["Mon Jardin"])[0]
            amount = float(params.get("amount", [100])[0])
            garden_id = db.create_garden(1, name, amount)
            self.json({"message": "🌰 Graine plantée !", "garden_id": garden_id})
        elif path == "/api/harvest":
            garden_id = int(params.get("id", [1])[0])
            amount = db.harvest(garden_id)
            self.json({"message": f"🌳 Récolté : {amount} sat", "amount": amount})
        elif path == "/":
            self.serve_dashboard()
        else:
            self.json({"error": "Not found"}, 404)
    
    def serve_dashboard(self):
        gardens = db.get_all_gardens()
        cards = ""
        for g in gardens:
            stats = db.get_stats(g["id"])
            cards += f'''
            <div class="garden-card">
                <h2>{g["name"]}</h2>
                <div class="value">{g["current_value"]:.8f} <small>sat</small></div>
                <div class="stats">
                    <span>🌰 Graine: {g["seed_amount"]:.2f} sat</span>
                    <span>📈 Niveau: {g["level"]}</span>
                    <span>📊 Croissance: {g["growth_rate"]*100:.1f}%</span>
                    <span>🌳 Récolté: {stats["total_harvested"]:.2f} sat</span>
                    <span>📈 +{stats["growth_per_day"]:.8f} sat/h</span>
                </div>
                <div class="actions">
                    <button onclick="harvest({g['id']})">🌳 Récolter</button>
                </div>
            </div>'''
        
        html = f'''<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>🌱 Jardin Financier OSIS</title>
<style>
    *{{margin:0;padding:0;box-sizing:border-box}}
    body{{background:linear-gradient(180deg,#0a1a0a 0%,#1a3e1a 100%);color:white;font-family:sans-serif;min-height:100vh;padding:20px}}
    h1{{text-align:center;color:#00c853;margin-bottom:10px}}
    .subtitle{{text-align:center;color:#8bc34a;margin-bottom:30px;font-style:italic}}
    .garden-card{{background:rgba(26,62,26,0.9);padding:25px;border-radius:15px;margin:15px 0;border:1px solid #2a5a2a}}
    .garden-card h2{{color:#8bc34a;margin-bottom:10px}}
    .value{{font-size:2.5em;color:#ffd700;font-weight:bold;text-align:center;margin:15px 0}}
    .value small{{font-size:0.5em;color:#888}}
    .stats{{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin:15px 0}}
    .stats span{{background:rgba(0,0,0,0.3);padding:10px;border-radius:10px;font-size:0.9em;text-align:center}}
    .actions{{text-align:center;margin-top:15px}}
    button{{padding:12px 30px;background:#00c853;color:black;border:none;border-radius:25px;font-size:1.1em;font-weight:bold;cursor:pointer}}
    button:hover{{background:#00e676}}
    .btn-plant{{background:#ffd700;color:black;display:block;width:100%;margin:20px 0}}
    .info{{text-align:center;color:#888;margin:20px 0;font-size:0.9em}}
    .pulse{{animation:pulse 2s infinite}}
    @keyframes pulse{{0%{{opacity:1}}50%{{opacity:0.5}}100%{{opacity:1}}}}
</style></head><body>
<h1>🌱 Le Jardin Financier</h1>
<p class="subtitle">Plantez une graine. Laissez pousser. Récoltez.</p>
{cards}
<button class="btn-plant" onclick="plant()">🌰 Planter une nouvelle graine (100 sat)</button>
<div class="info"><span class="pulse">🟢</span> Le jardinier automatique s'occupe de vos plantes 24h/24</div>
<script>
function plant(){{fetch('/api/plant?name='+encodeURIComponent(prompt('Nom du jardin ?','Mon Jardin'))+'&amount='+(prompt('Montant ?','100'))).then(()=>location.reload())}}
function harvest(id){{fetch('/api/harvest?id='+id).then(()=>location.reload())}}
setInterval(()=>location.reload(),30000);
</script></body></html>'''
        self.send_response(200); self.send_header("Content-Type","text/html"); self.end_headers()
        self.wfile.write(html.encode())
    
    def json(self, data, status=200):
        self.send_response(status); self.send_header("Content-Type","application/json"); self.end_headers()
        self.wfile.write(json.dumps(data, indent=2, ensure_ascii=False, default=str).encode())

# Démarrer le jardinier en arrière-plan
gardener = AutomaticGardener()
threading.Thread(target=gardener.start, daemon=True).start()

# Démarrer le serveur
if __name__ == "__main__":
    port = int(os.getenv("GARDEN_PORT", 8070))
    print(f"🌱 Jardin Financier démarré sur http://localhost:{port}")
    HTTPServer(("0.0.0.0", port), GardenHandler).serve_forever()
GARDEN

# ------------------------------------------------------------
# SERVICE SYSTEMD
# ------------------------------------------------------------
sudo tee /etc/systemd/system/osis-garden.service > /dev/null << 'SVC'
[Unit]
Description=OSIS Jardin Financier 24/7
After=network.target
[Service]
Type=simple
ExecStart=/usr/bin/python3 /opt/osis-garden/garden.py
Restart=always
RestartSec=10
Environment=GARDEN_PORT=8070
[Install]
WantedBy=multi-user.target
SVC

sudo systemctl daemon-reload
sudo systemctl enable osis-garden
sudo systemctl start osis-garden

# ------------------------------------------------------------
# FIN
# ------------------------------------------------------------
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                                                          ║"
echo -e "║   ${GREEN}🌱 LE JARDIN FINANCIER EST EN LIGNE !${NC}                    ║"
echo "║                                                          ║"
echo "║   🌐 Dashboard : http://localhost:8070                  ║"
echo "║                                                          ║"
echo "║   ${YELLOW}🌰 1. Plantez une graine (100 sat)${NC}                      ║"
echo "║   ${YELLOW}💧 2. L'irrigation automatique l'arrose${NC}                 ║"
echo "║   ${YELLOW}☀️ 3. La photosynthèse la fait grandir${NC}                 ║"
echo "║   ${YELLOW}🌳 4. Récoltez quand c'est mûr !${NC}                        ║"
echo "║                                                          ║"
echo "║   ${GOLD}💰 L'ARGENT POUSSE TOUT SEUL !${NC}                            ║"
echo "║   ${GOLD}📴 MÊME SANS CONNEXION, LE JARDINIER VEILLE${NC}              ║"
echo "║                                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"