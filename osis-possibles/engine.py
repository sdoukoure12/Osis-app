#!/bin/bash
# =============================================================================
# 🌌 OSIS vX.0 — LE MARCHÉ DES POSSIBLES
# =============================================================================
# Concept : Échanger des futurs alternatifs qui gagnent de la valeur avec le temps
# Auteur  : Projet OSIS
# =============================================================================
set -e

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; PURPLE='\033[0;35m'; GOLD='\033[0;33m'; NC='\033[0m'
echo -e "${PURPLE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║   🌌 OSIS vX.0 — LE MARCHÉ DES POSSIBLES                    ║"
echo "║   « Et si... ? » — La valeur de l'inattendu                  ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

BASE_DIR="/opt/osis-possibles"
sudo mkdir -p $BASE_DIR && sudo chown -R $USER:$USER $BASE_DIR
mkdir -p $BASE_DIR/{data,logs,static}

# ============================================================
# LE MOTEUR DES POSSIBLES
# ============================================================
cat > $BASE_DIR/engine.py << 'ENGINE'
#!/usr/bin/env python3
"""
🌌 LE MARCHÉ DES POSSIBLES — The Possible Market

Un lieu où l'on échange des « Possibilités » (POSS),
des actifs numériques qui représentent des futurs alternatifs.

Chaque POSS :
- 🧠 Contient un scénario (« Et si... ? »)
- 💰 A une mise de départ en satoshis
- ⏳ Gagne de la valeur avec le temps (Gravité Temporelle)
- 🌱 Génère des « Échos » (sous-possibilités)
- 🔗 Peut entrer en « Résonance » avec d'autres POSS
"""
import json, time, os, sqlite3, random, hashlib, threading, math
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE, 'data', 'possibles.db')
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# =============================================
# BASE DE DONNÉES
# =============================================
class PossibleDB:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.executescript('''
            CREATE TABLE IF NOT EXISTS possibles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                creator_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                scenario TEXT NOT NULL,
                category TEXT NOT NULL,
                initial_stake REAL NOT NULL,
                current_value REAL NOT NULL,
                maturity_date TEXT,
                status TEXT DEFAULT 'active',
                resonance_count INTEGER DEFAULT 0,
                echo_count INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now'))
            );
            
            CREATE TABLE IF NOT EXISTS investments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                possible_id INTEGER REFERENCES possibles(id),
                investor_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            );
            
            CREATE TABLE IF NOT EXISTS echoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parent_id INTEGER REFERENCES possibles(id),
                title TEXT NOT NULL,
                value REAL NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            );
            
            CREATE TABLE IF NOT EXISTS resonances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                possible_id_1 INTEGER REFERENCES possibles(id),
                possible_id_2 INTEGER REFERENCES possibles(id),
                strength REAL DEFAULT 0.0,
                created_at TEXT DEFAULT (datetime('now'))
            );
            
            CREATE TABLE IF NOT EXISTS validations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                possible_id INTEGER REFERENCES possibles(id),
                validator_id INTEGER NOT NULL,
                vote TEXT NOT NULL,
                reward REAL DEFAULT 0.0,
                created_at TEXT DEFAULT (datetime('now'))
            );
        ''')
        self.conn.commit()
    
    def create_possible(self, creator_id, title, scenario, category, initial_stake, maturity_days=90):
        """Crée une nouvelle Possibilité"""
        current_value = initial_stake * 1.1  # +10% au lancement
        maturity_date = (datetime.now() + timedelta(days=maturity_days)).strftime("%Y-%m-%d %H:%M:%S")
        
        cursor = self.conn.execute(
            "INSERT INTO possibles (creator_id, title, scenario, category, initial_stake, current_value, maturity_date) VALUES (?,?,?,?,?,?,?)",
            (creator_id, title, scenario, category, initial_stake, current_value, maturity_date)
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def get_possible(self, possible_id):
        """Récupère une Possibilité"""
        row = self.conn.execute("SELECT * FROM possibles WHERE id = ?", (possible_id,)).fetchone()
        if not row: return None
        cols = [c[0] for c in self.conn.execute("PRAGMA table_info(possibles)")]
        return dict(zip(cols, row))
    
    def get_all_possibles(self, status="active"):
        """Toutes les Possibilités actives"""
        rows = self.conn.execute(
            "SELECT * FROM possibles WHERE status = ? ORDER BY current_value DESC", (status,)
        ).fetchall()
        cols = [c[0] for c in self.conn.execute("PRAGMA table_info(possibles)")]
        return [dict(zip(cols, r)) for r in rows]
    
    def apply_temporal_gravity(self):
        """Applique la Gravité Temporelle : plus le temps passe, plus la valeur augmente"""
        possibles = self.get_all_possibles()
        
        for p in possibles:
            # Calcul du temps écoulé depuis la création
            created = datetime.strptime(p["created_at"], "%Y-%m-%d %H:%M:%S")
            elapsed_days = (datetime.now() - created).days
            
            # Gravité Temporelle : +0.1% par jour
            growth = round(p["current_value"] * (0.001 * elapsed_days), 8)
            
            # Bonus de proximité de maturité
            if p["maturity_date"]:
                maturity = datetime.strptime(p["maturity_date"], "%Y-%m-%d %H:%M:%S")
                days_to_maturity = (maturity - datetime.now()).days
                if days_to_maturity > 0:
                    maturity_bonus = round(p["current_value"] * (0.01 / max(1, days_to_maturity)), 8)
                    growth += maturity_bonus
            
            new_value = p["current_value"] + growth
            self.conn.execute(
                "UPDATE possibles SET current_value = ? WHERE id = ?",
                (new_value, p["id"])
            )
    
    def generate_echoes(self, possible_id):
        """Génère des Échos : sous-possibilités automatiques"""
        possible = self.get_possible(possible_id)
        if not possible: return
        
        # Un écho tous les 30 jours
        echo_count = self.conn.execute(
            "SELECT COUNT(*) FROM echoes WHERE parent_id = ?", (possible_id,)
        ).fetchone()[0]
        
        created = datetime.strptime(possible["created_at"], "%Y-%m-%d %H:%M:%S")
        elapsed_days = (datetime.now() - created).days
        expected_echoes = elapsed_days // 30
        
        for _ in range(expected_echoes - echo_count):
            echo_value = round(possible["current_value"] * random.uniform(0.01, 0.05), 8)
            echo_title = f"Écho de : {possible['title']} (#{echo_count + 1})"
            
            self.conn.execute(
                "INSERT INTO echoes (parent_id, title, value) VALUES (?,?,?)",
                (possible_id, echo_title, echo_value)
            )
            self.conn.execute(
                "UPDATE possibles SET echo_count = echo_count + 1 WHERE id = ?",
                (possible_id,)
            )
        self.conn.commit()
    
    def create_resonance(self, possible_id_1, possible_id_2):
        """Crée une Résonance entre deux Possibilités"""
        existing = self.conn.execute(
            "SELECT * FROM resonances WHERE (possible_id_1 = ? AND possible_id_2 = ?) OR (possible_id_1 = ? AND possible_id_2 = ?)",
            (possible_id_1, possible_id_2, possible_id_2, possible_id_1)
        ).fetchone()
        
        if existing: return
        
        # Force de résonance basée sur la similarité des catégories
        p1 = self.get_possible(possible_id_1)
        p2 = self.get_possible(possible_id_2)
        
        strength = 1.0 if p1["category"] == p2["category"] else 0.3
        
        self.conn.execute(
            "INSERT INTO resonances (possible_id_1, possible_id_2, strength) VALUES (?,?,?)",
            (possible_id_1, possible_id_2, strength)
        )
        
        # Bonus de résonance : +5% de valeur aux deux
        bonus_p1 = round(p1["current_value"] * 0.05 * strength, 8)
        bonus_p2 = round(p2["current_value"] * 0.05 * strength, 8)
        
        self.conn.execute(
            "UPDATE possibles SET current_value = current_value + ?, resonance_count = resonance_count + 1 WHERE id = ?",
            (bonus_p1, possible_id_1)
        )
        self.conn.execute(
            "UPDATE possibles SET current_value = current_value + ?, resonance_count = resonance_count + 1 WHERE id = ?",
            (bonus_p2, possible_id_2)
        )
        self.conn.commit()
    
    def invest(self, possible_id, investor_id, amount):
        """Investit dans une Possibilité"""
        possible = self.get_possible(possible_id)
        if not possible: return False
        
        new_value = possible["current_value"] + amount * 1.05  # +5% immédiat
        self.conn.execute("UPDATE possibles SET current_value = ? WHERE id = ?", (new_value, possible_id))
        self.conn.execute("INSERT INTO investments (possible_id, investor_id, amount) VALUES (?,?,?)", (possible_id, investor_id, amount))
        self.conn.commit()
        return True
    
    def get_stats(self):
        """Statistiques du marché"""
        possibles = self.get_all_possibles()
        total_value = sum(p["current_value"] for p in possibles)
        total_echoes = sum(p["echo_count"] for p in possibles)
        total_resonances = self.conn.execute("SELECT COUNT(*) FROM resonances").fetchone()[0]
        
        return {
            "total_possibles": len(possibles),
            "total_value": total_value,
            "total_echoes": total_echoes,
            "total_resonances": total_resonances,
            "top_possibles": sorted(possibles, key=lambda x: x["current_value"], reverse=True)[:5]
        }

# Instance globale
db = PossibleDB()

# Créer des Possibilités de démonstration
if not db.get_all_possibles():
    db.create_possible(1, "Un pont entre les mondes", "Et si on construisait un pont qui relie tous les villages isolés ?", "infrastructure", 1000, 365)
    db.create_possible(1, "L'école du futur", "Et si chaque enfant africain avait accès à une éducation de qualité via le numérique ?", "education", 500, 180)
    db.create_possible(1, "La forêt qui parle", "Et si les arbres pouvaient communiquer leurs besoins via des capteurs ?", "environnement", 300, 90)
    db.create_possible(1, "Le marché sans frontières", "Et si les artisans pouvaient vendre directement au monde entier ?", "economie", 800, 270)
    db.create_possible(1, "L'eau pour tous", "Et si chaque village avait accès à l'eau potable ?", "humanitaire", 2000, 180)
    print("🌌 5 Possibilités initiales créées")

# =============================================
# LE MOTEUR TEMPOREL (tourne 24/7)
# =============================================
class TemporalEngine:
    """Applique la Gravité Temporelle et génère les Échos"""
    
    def __init__(self):
        self.running = True
    
    def cycle(self):
        """Un cycle temporel"""
        db.apply_temporal_gravity()
        
        for p in db.get_all_possibles():
            db.generate_echoes(p["id"])
    
    def start(self):
        print("⏳ Moteur Temporel activé")
        while self.running:
            self.cycle()
            stats = db.get_stats()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 🌌 Valeur totale: {stats['total_value']:.2f} sat | {stats['total_possibles']} possibles | {stats['total_echoes']} échos")
            time.sleep(300)

# =============================================
# API ET DASHBOARD
# =============================================
class PossibleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)
        
        if path == "/health":
            self.json({"status": "ok", "service": "possible-market", "concept": "Le Marché des Possibles"})
        elif path == "/api/possibles":
            self.json(db.get_all_possibles())
        elif path == "/api/possible":
            pid = int(params.get("id", [1])[0])
            self.json(db.get_possible(pid))
        elif path == "/api/stats":
            self.json(db.get_stats())
        elif path == "/api/create":
            title = params.get("title", ["Nouvelle Possibilité"])[0]
            scenario = params.get("scenario", ["Et si... ?"])[0]
            category = params.get("category", ["innovation"])[0]
            stake = float(params.get("stake", [100])[0])
            maturity = int(params.get("maturity", [90])[0])
            pid = db.create_possible(1, title, scenario, category, stake, maturity)
            self.json({"message": "🌌 Possibilité créée !", "id": pid})
        elif path == "/api/invest":
            pid = int(params.get("id", [1])[0])
            amount = float(params.get("amount", [100])[0])
            db.invest(pid, 1, amount)
            self.json({"message": f"💰 Investi {amount} sat dans la possibilité #{pid}"})
        elif path == "/":
            self.serve_dashboard()
        else:
            self.json({"error": "Not found"}, 404)
    
    def serve_dashboard(self):
        possibles = db.get_all_possibles()
        stats = db.get_stats()
        
        cards = ""
        for p in possibles[:10]:
            created = datetime.strptime(p["created_at"], "%Y-%m-%d %H:%M:%S")
            elapsed = (datetime.now() - created).days
            cards += f'''
            <div class="possible-card">
                <div class="category">{p["category"]}</div>
                <h3>🧠 {p["title"]}</h3>
                <p class="scenario">« {p["scenario"]} »</p>
                <div class="value">⚡ {p["current_value"]:.2f} <small>sat</small></div>
                <div class="info">
                    <span>⏳ {elapsed} jours</span>
                    <span>🔗 {p["resonance_count"]} résonances</span>
                    <span>🌱 {p["echo_count"]} échos</span>
                </div>
                <div class="actions">
                    <button onclick="invest({p['id']})">💰 Investir</button>
                    <button onclick="resonate({p['id']})">🔗 Résonner</button>
                </div>
            </div>'''
        
        html = f'''<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>🌌 Le Marché des Possibles</title>
<style>
    *{{margin:0;padding:0;box-sizing:border-box}}
    body{{background:linear-gradient(135deg,#0a0a2e 0%,#1a0a3e 50%,#0a1a2e 100%);color:white;font-family:sans-serif;min-height:100vh;padding:20px}}
    h1{{text-align:center;background:linear-gradient(90deg,#e040fb,#7c4dff,#448aff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-size:2.5em;margin-bottom:10px}}
    .subtitle{{text-align:center;color:#aaa;margin-bottom:30px;font-style:italic}}
    .stats-bar{{display:flex;justify-content:center;gap:30px;flex-wrap:wrap;margin-bottom:30px}}
    .stat{{background:rgba(26,26,62,0.9);padding:20px;border-radius:15px;text-align:center;min-width:150px}}
    .stat .value{{font-size:1.5em;color:#ffd700;font-weight:bold}}
    .stat .label{{color:#888;font-size:0.8em;margin-top:5px}}
    .possible-card{{background:rgba(26,26,62,0.9);padding:25px;border-radius:15px;margin:15px 0;border:1px solid #2a2a5a;position:relative;overflow:hidden}}
    .possible-card::before{{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,#e040fb,#7c4dff,#448aff)}}
    .category{{display:inline-block;padding:3px 10px;border-radius:15px;font-size:0.7em;background:#e040fb;color:white;margin-bottom:10px;text-transform:uppercase}}
    .possible-card h3{{color:#e040fb;margin-bottom:10px}}
    .scenario{{color:#aaa;font-style:italic;margin-bottom:15px;font-size:0.95em}}
    .value{{font-size:2em;color:#ffd700;font-weight:bold;text-align:center;margin:15px 0}}
    .value small{{font-size:0.5em;color:#888}}
    .info{{display:flex;justify-content:space-around;margin:15px 0;color:#888;font-size:0.85em}}
    .actions{{text-align:center;margin-top:15px;display:flex;gap:10px;justify-content:center}}
    button{{padding:10px 20px;border:none;border-radius:25px;font-weight:bold;cursor:pointer;font-size:0.9em}}
    .btn-invest{{background:#ffd700;color:black}}
    .btn-resonate{{background:#7c4dff;color:white}}
    .btn-create{{background:#00c853;color:black;display:block;width:100%;padding:15px;font-size:1.1em;margin:20px 0}}
    .pulse{{animation:pulse 3s infinite}}
    @keyframes pulse{{0%{{opacity:1}}50%{{opacity:0.5}}100%{{opacity:1}}}}
</style></head><body>
<h1>🌌 Le Marché des Possibles</h1>
<p class="subtitle">« Et si... ? » — Investissez dans les futurs alternatifs</p>

<div class="stats-bar">
    <div class="stat"><div class="value">{stats["total_possibles"]}</div><div class="label">🌌 Possibles</div></div>
    <div class="stat"><div class="value">{stats["total_value"]:.0f}</div><div class="label">⚡ Valeur Totale (sat)</div></div>
    <div class="stat"><div class="value">{stats["total_echoes"]}</div><div class="label">🌱 Échos</div></div>
    <div class="stat"><div class="value">{stats["total_resonances"]}</div><div class="label">🔗 Résonances</div></div>
</div>

{cards}

<button class="btn-create" onclick="createPossible()">🌌 Créer une nouvelle Possibilité</button>
<div style="text-align:center;color:#888;margin-top:20px"><span class="pulse">⏳</span> Le Moteur Temporel applique la Gravité en continu</div>

<script>
function createPossible(){{const t=prompt('Titre de la possibilité ?','');const s=prompt('Scénario (Et si... ?)','');const c=prompt('Catégorie (innovation, education, environnement, economie, humanitaire)','innovation');const a=prompt('Mise initiale (satoshis) ?','100');if(t&&s){{fetch('/api/create?title='+encodeURIComponent(t)+'&scenario='+encodeURIComponent(s)+'&category='+c+'&stake='+a).then(()=>location.reload())}}}}
function invest(id){{const a=prompt('Montant à investir (satoshis) ?','100');if(a){{fetch('/api/invest?id='+id+'&amount='+a).then(()=>location.reload())}}}}
function resonate(id){{const pid=prompt('ID de la possibilité avec laquelle résonner ?','');if(pid){{fetch('/api/resonate?id1='+id+'&id2='+pid).then(()=>location.reload())}}}}
setInterval(()=>location.reload(),60000);
</script></body></html>'''
        self.send_response(200); self.send_header("Content-Type","text/html"); self.end_headers()
        self.wfile.write(html.encode())
    
    def json(self, data, status=200):
        self.send_response(status); self.send_header("Content-Type","application/json"); self.end_headers()
        self.wfile.write(json.dumps(data, indent=2, ensure_ascii=False, default=str).encode())

# Démarrer le moteur temporel
temporal = TemporalEngine()
threading.Thread(target=temporal.start, daemon=True).start()

if __name__ == "__main__":
    port = int(os.getenv("POSSIBLE_PORT", 8085))
    print(f"🌌 Le Marché des Possibles démarré sur http://localhost:{port}")
    HTTPServer(("0.0.0.0", port), PossibleHandler).serve_forever()
ENGINE

# ------------------------------------------------------------
# SERVICE SYSTEMD
# ------------------------------------------------------------
sudo tee /etc/systemd/system/osis-possibles.service > /dev/null << 'SVC'
[Unit]
Description=OSIS Marché des Possibles 24/7
After=network.target
[Service]
Type=simple
ExecStart=/usr/bin/python3 /opt/osis-possibles/engine.py
Restart=always
RestartSec=10
Environment=POSSIBLE_PORT=8085
[Install]
WantedBy=multi-user.target
SVC

sudo systemctl daemon-reload
sudo systemctl enable osis-possibles
sudo systemctl start osis-possibles
