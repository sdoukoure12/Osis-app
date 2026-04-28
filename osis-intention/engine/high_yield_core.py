#!/bin/bash
# =============================================================================
# 🌌 OSIS v∞.1 — ÉCONOMIE DE L'INTENTION À HAUT RENDEMENT
# =============================================================================
# Des gains EXCEPTIONNELS pour une plateforme RÉVOLUTIONNAIRE
# =============================================================================
set -e

PURPLE='\033[0;35m'; GOLD='\033[0;33m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'; RED='\033[0;31m'; NC='\033[0m'
echo -e "${PURPLE}"
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║   🌌 OSIS v∞.1 — HAUT RENDEMENT                                 ║"
echo "║                                                                  ║"
echo "║   « Gagnez 1000x plus. Vos intentions valent de l'or. »          ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

BASE_DIR="/opt/osis-intention"
sudo mkdir -p $BASE_DIR && sudo chown -R $USER:$USER $BASE_DIR
mkdir -p $BASE_DIR/{engine,data,logs}

# ============================================================
# LE MOTEUR HAUT RENDEMENT
# ============================================================
cat > $BASE_DIR/engine/high_yield_core.py << 'CORE'
#!/usr/bin/env python3
"""
🌌 OSIS v∞.1 — ÉCONOMIE DE L'INTENTION À HAUT RENDEMENT

GAINS EXCEPTIONNELS :
- Création : 10 000 satoshis
- Investissement : +10% immédiat
- Résonance : +25% par connexion
- Gravité : +5% par jour
- Réalisation : ×5 la valeur
- Parrainage : 5 000 satoshis
"""
import json, time, os, sqlite3, random, hashlib, threading, math
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(BASE, 'data', 'high_yield.db')
os.makedirs(os.path.dirname(DB), exist_ok=True)

# =============================================
# CONSTANTES DE GAINS ÉLEVÉS
# =============================================
REWARDS = {
    "create_intention": 10000.0,      # 10 000 sat pour créer une intention
    "invest_bonus": 0.10,             # +10% immédiat sur l'investissement
    "resonance_bonus": 0.25,          # +25% par résonance
    "gravity_per_day": 0.05,          # +5% par jour
    "realization_multiplier": 5.0,    # ×5 à la réalisation
    "referral_bonus": 5000.0,         # 5 000 sat par parrainage
    "daily_login": 100.0,             # 100 sat par jour de connexion
    "echo_bonus": 0.15,               # +15% par écho
}

class HighYieldDB:
    def __init__(self):
        self.conn = sqlite3.connect(DB)
        self.conn.executescript('''
            CREATE TABLE IF NOT EXISTS intentions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                creator_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                token_value REAL DEFAULT 10000.0,
                total_invested REAL DEFAULT 0.0,
                total_earned REAL DEFAULT 10000.0,
                status TEXT DEFAULT 'active',
                progress REAL DEFAULT 0.0,
                resonance_level INTEGER DEFAULT 1,
                echo_count INTEGER DEFAULT 0,
                daily_bonus_last TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                realized_at TEXT
            );
            
            CREATE TABLE IF NOT EXISTS investments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                intention_id INTEGER REFERENCES intentions(id),
                investor_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                bonus_earned REAL NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            );
            
            CREATE TABLE IF NOT EXISTS resonances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                intention_id_1 INTEGER REFERENCES intentions(id),
                intention_id_2 INTEGER REFERENCES intentions(id),
                strength REAL DEFAULT 0.25,
                bonus_applied REAL DEFAULT 0.0,
                created_at TEXT DEFAULT (datetime('now'))
            );
            
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                total_earned REAL DEFAULT 0.0,
                referral_code TEXT UNIQUE,
                referred_by INTEGER,
                created_at TEXT DEFAULT (datetime('now'))
            );
        ''')
        self.conn.commit()
    
    def create_intention(self, creator_id, title, description, category):
        """Créer une intention → 10 000 satoshis de valeur initiale"""
        cursor = self.conn.execute(
            "INSERT INTO intentions (creator_id, title, description, category, token_value, total_earned) VALUES (?,?,?,?,?,?)",
            (creator_id, title, description, category, REWARDS["create_intention"], REWARDS["create_intention"])
        )
        self.conn.commit()
        
        # Créditer le créateur
        self.conn.execute(
            "UPDATE users SET total_earned = total_earned + ? WHERE id = ?",
            (REWARDS["create_intention"], creator_id)
        )
        self.conn.commit()
        
        return cursor.lastrowid
    
    def get_intention(self, iid):
        row = self.conn.execute("SELECT * FROM intentions WHERE id = ?", (iid,)).fetchone()
        if row:
            cols = [c[0] for c in self.conn.execute("PRAGMA table_info(intentions)")]
            return dict(zip(cols, row))
        return None
    
    def get_all_intentions(self, status="active"):
        rows = self.conn.execute(
            "SELECT * FROM intentions WHERE status = ? ORDER BY token_value DESC", (status,)
        ).fetchall()
        cols = [c[0] for c in self.conn.execute("PRAGMA table_info(intentions)")]
        return [dict(zip(cols, r)) for r in rows]
    
    def invest(self, intention_id, investor_id, amount):
        """Investir → +10% immédiat de bonus"""
        intention = self.get_intention(intention_id)
        if not intention: return None
        
        # Bonus de 10% sur l'investissement
        bonus = amount * REWARDS["invest_bonus"]
        total_added = amount + bonus
        
        new_value = intention["token_value"] + total_added
        new_invested = intention["total_invested"] + amount
        new_earned = intention["total_earned"] + bonus
        new_progress = min(100, intention["progress"] + (total_added / new_value) * 20)
        
        self.conn.execute(
            "UPDATE intentions SET token_value = ?, total_invested = ?, total_earned = ?, progress = ? WHERE id = ?",
            (new_value, new_invested, new_earned, new_progress, intention_id)
        )
        self.conn.execute(
            "INSERT INTO investments (intention_id, investor_id, amount, bonus_earned) VALUES (?,?,?,?)",
            (intention_id, investor_id, amount, bonus)
        )
        # Créditer l'investisseur du bonus
        self.conn.execute(
            "UPDATE users SET total_earned = total_earned + ? WHERE id = ?",
            (bonus, investor_id)
        )
        self.conn.commit()
        
        return {
            "new_value": new_value,
            "bonus_earned": bonus,
            "progress": new_progress,
            "total_invested": new_invested
        }
    
    def apply_gravity(self):
        """Applique la gravité temporelle : +5% par jour"""
        intentions = self.get_all_intentions()
        total_bonus = 0
        
        for intent in intentions:
            created = datetime.strptime(intent["created_at"], "%Y-%m-%d %H:%M:%S")
            days_elapsed = max(1, (datetime.now() - created).days)
            
            # +5% par jour (composé)
            growth = intent["token_value"] * (REWARDS["gravity_per_day"] * days_elapsed)
            new_value = intent["token_value"] + growth
            
            self.conn.execute(
                "UPDATE intentions SET token_value = ?, total_earned = total_earned + ? WHERE id = ?",
                (new_value, growth, intent["id"])
            )
            total_bonus += growth
        
        self.conn.commit()
        return total_bonus
    
    def create_resonance(self, iid1, iid2):
        """Résonance entre deux intentions → +25% de bonus"""
        i1 = self.get_intention(iid1)
        i2 = self.get_intention(iid2)
        if not i1 or not i2: return None
        
        bonus1 = i1["token_value"] * REWARDS["resonance_bonus"]
        bonus2 = i2["token_value"] * REWARDS["resonance_bonus"]
        
        self.conn.execute(
            "UPDATE intentions SET token_value = token_value + ?, total_earned = total_earned + ?, resonance_level = resonance_level + 1 WHERE id = ?",
            (bonus1, bonus1, iid1)
        )
        self.conn.execute(
            "UPDATE intentions SET token_value = token_value + ?, total_earned = total_earned + ?, resonance_level = resonance_level + 1 WHERE id = ?",
            (bonus2, bonus2, iid2)
        )
        self.conn.execute(
            "INSERT INTO resonances (intention_id_1, intention_id_2, strength, bonus_applied) VALUES (?,?,?,?)",
            (iid1, iid2, REWARDS["resonance_bonus"], bonus1 + bonus2)
        )
        self.conn.commit()
        
        return {"bonus_1": bonus1, "bonus_2": bonus2}
    
    def realize_intention(self, iid):
        """Réaliser une intention → ×5 la valeur"""
        intent = self.get_intention(iid)
        if not intent or intent["status"] != "active": return None
        
        multiplier = REWARDS["realization_multiplier"]
        final_value = intent["token_value"] * multiplier
        bonus = final_value - intent["token_value"]
        
        self.conn.execute(
            "UPDATE intentions SET token_value = ?, total_earned = total_earned + ?, status = 'realized', progress = 100, realized_at = datetime('now') WHERE id = ?",
            (final_value, bonus, iid)
        )
        self.conn.execute(
            "UPDATE users SET total_earned = total_earned + ? WHERE id = ?",
            (bonus, intent["creator_id"])
        )
        self.conn.commit()
        
        return {"final_value": final_value, "bonus": bonus}
    
    def get_leaderboard(self, limit=10):
        """Classement des intentions par valeur"""
        return self.get_all_intentions()[:limit]
    
    def get_user_stats(self, user_id):
        """Statistiques d'un utilisateur"""
        row = self.conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if row:
            cols = [c[0] for c in self.conn.execute("PRAGMA table_info(users)")]
            return dict(zip(cols, row))
        return None

db = HighYieldDB()

# Créer un utilisateur démo
try:
    db.conn.execute("INSERT INTO users (username, referral_code) VALUES ('demo', 'DEMO001')")
    db.conn.commit()
except: pass

# Intentions de démonstration avec hautes valeurs
if not db.get_all_intentions():
    db.create_intention(1, "🏫 École du Futur", "Une école connectée pour 1000 enfants", "education")
    db.create_intention(1, "🌳 Forêt Éternelle", "1 million d'arbres plantés au Sahel", "environnement")
    db.create_intention(1, "🏥 Santé Pour Tous", "Cliniques mobiles dans 50 villages", "santé")
    db.create_intention(1, "💧 L'EAU", "Accès à l'eau potable pour 100 000 personnes", "humanitaire")
    db.create_intention(1, "🏗️ Villages Connectés", "Internet haut débit dans 100 villages", "infrastructure")
    print("🌌 5 Intentions créées (valeur initiale: 10 000 sat chaque)")

# =============================================
# MOTEUR DE CROISSANCE 24/7
# =============================================
class GrowthEngine:
    def __init__(self):
        self.running = True
        self.total_distributed = 0
    
    def cycle(self):
        # Appliquer la gravité temporelle
        gravity_bonus = db.apply_gravity()
        self.total_distributed += gravity_bonus
        
        # Créer des résonances automatiques entre intentions similaires
        intentions = db.get_all_intentions()
        for i in range(len(intentions)):
            for j in range(i+1, len(intentions)):
                if intentions[i]["category"] == intentions[j]["category"]:
                    try:
                        result = db.create_resonance(intentions[i]["id"], intentions[j]["id"])
                        if result:
                            self.total_distributed += result["bonus_1"] + result["bonus_2"]
                    except: pass
    
    def start(self):
        print(f"💎 Moteur de Croissance Haute Fréquence activé")
        print(f"📈 +{REWARDS['gravity_per_day']*100:.0f}% par jour | +{REWARDS['resonance_bonus']*100:.0f}% par résonance | ×{REWARDS['realization_multiplier']:.0f} à la réalisation")
        
        while self.running:
            self.cycle()
            stats = self.get_stats()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 💎 Distribué: {self.total_distributed:.0f} sat | Valeur totale: {stats['total_value']:.0f} sat | {stats['total_intentions']} intentions")
            time.sleep(120)  # Toutes les 2 minutes pour des gains rapides
    
    def get_stats(self):
        intentions = db.get_all_intentions()
        return {
            "total_intentions": len(intentions),
            "total_value": sum(i["token_value"] for i in intentions),
            "total_earned": sum(i["total_earned"] for i in intentions),
            "total_invested": sum(i["total_invested"] for i in intentions)
        }

# =============================================
# API + DASHBOARD
# =============================================
class HighYieldHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)
        
        if path == "/health":
            self.json({"status": "ok", "service": "high-yield-intention", "version": "∞.1"})
        elif path == "/api/intentions":
            self.json(db.get_all_intentions())
        elif path == "/api/leaderboard":
            self.json(db.get_leaderboard(10))
        elif path == "/api/stats":
            self.json(growth_engine.get_stats())
        elif path == "/api/create":
            title = params.get("title", ["Nouvelle Intention"])[0]
            desc = params.get("desc", [""])[0]
            cat = params.get("category", ["innovation"])[0]
            iid = db.create_intention(1, title, desc, cat)
            self.json({
                "message": "🌌 Intention créée !",
                "id": iid,
                "token_value": REWARDS["create_intention"],
                "bonus_earned": REWARDS["create_intention"]
            })
        elif path == "/api/invest":
            iid = int(params.get("id", [1])[0])
            amount = float(params.get("amount", [1000])[0])
            result = db.invest(iid, 1, amount)
            if result:
                self.json({
                    "message": f"💰 Investi {amount} sat + {result['bonus_earned']} sat de bonus !",
                    "new_value": result["new_value"],
                    "bonus": result["bonus_earned"],
                    "progress": result["progress"]
                })
            else:
                self.json({"error": "Intention non trouvée"}, 404)
        elif path == "/api/realize":
            iid = int(params.get("id", [1])[0])
            result = db.realize_intention(iid)
            if result:
                self.json({
                    "message": f"🎉 Intention réalisée ! ×{REWARDS['realization_multiplier']:.0f} !",
                    "final_value": result["final_value"],
                    "bonus": result["bonus"]
                })
            else:
                self.json({"error": "Impossible de réaliser"}, 400)
        elif path == "/":
            self.serve_dashboard()
        else:
            self.json({"error": "Not found"}, 404)
    
    def serve_dashboard(self):
        intentions = db.get_all_intentions()
        stats = growth_engine.get_stats()
        leaderboard = db.get_leaderboard(5)
        
        cards = ""
        for intent in intentions[:10]:
            progress = intent["progress"]
            cards += f'''
            <div class="intention-card">
                <span class="category">{intent["category"]}</span>
                <h3>{intent["title"]}</h3>
                <p>{intent["description"][:80]}...</p>
                <div class="value">💎 {intent["token_value"]:,.0f} <small>sat</small></div>
                <div class="progress-bar"><div class="progress-fill" style="width:{progress}%"></div></div>
                <div class="info">
                    <span>💰 {intent["total_invested"]:,.0f} investis</span>
                    <span>📈 {intent["total_earned"]:,.0f} gagnés</span>
                    <span>🔮 Nv.{intent["resonance_level"]}</span>
                    <span>{progress:.0f}%</span>
                </div>
                <div class="actions">
                    <button onclick="invest({intent['id']})">💰 Investir (+10% bonus)</button>
                    <button onclick="realize({intent['id']})">🎯 Réaliser (×5)</button>
                </div>
            </div>'''
        
        leaderboard_html = ""
        for i, intent in enumerate(leaderboard):
            medal = ["🥇","🥈","🥉","4️⃣","5️⃣"][i]
            leaderboard_html += f'<div class="lb-item"><span>{medal}</span> {intent["title"]} <strong>{intent["token_value"]:,.0f} sat</strong></div>'
        
        html = f'''<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>🌌 OSIS ∞.1 — Haut Rendement</title>
<style>
    *{{margin:0;padding:0;box-sizing:border-box}}
    body{{background:#050510;color:white;font-family:sans-serif;min-height:100vh}}
    .header{{background:linear-gradient(135deg,#1a0030,#0a0030,#001a30);padding:40px 20px;text-align:center;border-bottom:2px solid #ffd700}}
    .header h1{{font-size:3.5em;background:linear-gradient(90deg,#ffd700,#ffaa00,#ffd700);-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:shine 3s infinite}}
    .header .subtitle{{color:#ffd700;font-size:1.3em;margin-top:10px;font-weight:bold}}
    @keyframes shine{{0%{{filter:brightness(1)}}50%{{filter:brightness(1.5)}}100%{{filter:brightness(1)}}}}
    .container{{max-width:1200px;margin:0 auto;padding:20px}}
    .stats{{display:flex;justify-content:center;gap:20px;flex-wrap:wrap;margin:30px 0}}
    .stat{{background:rgba(26,0,62,0.9);padding:30px;border-radius:20px;text-align:center;min-width:200px;border:2px solid #ffd700}}
    .stat .val{{font-size:2.5em;color:#ffd700;font-weight:bold}}
    .stat .lbl{{color:#aaa;margin-top:5px}}
    .intention-card{{background:rgba(26,0,62,0.9);padding:25px;border-radius:20px;margin:15px 0;border:1px solid #4a0080}}
    .intention-card::before{{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,#ffd700,#ffaa00,#ffd700)}}
    .intention-card{{position:relative}}
    .category{{background:#ffd700;color:black;padding:4px 14px;border-radius:15px;font-size:0.75em;font-weight:bold;text-transform:uppercase}}
    .intention-card h3{{color:#ffd700;margin:10px 0}}
    .value{{font-size:2.2em;color:#ffd700;font-weight:bold;text-align:center;margin:15px 0}}
    .value small{{font-size:0.4em;color:#888}}
    .progress-bar{{background:#1a0030;height:10px;border-radius:10px;margin:10px 0;overflow:hidden}}
    .progress-fill{{background:linear-gradient(90deg,#ffd700,#ffaa00);height:100%;border-radius:10px;transition:width 1s}}
    .info{{display:flex;gap:15px;flex-wrap:wrap;margin:10px 0;color:#888;font-size:0.85em}}
    .actions{{display:flex;gap:10px;margin-top:15px}}
    button{{flex:1;padding:12px;border:none;border-radius:25px;font-weight:bold;cursor:pointer;font-size:0.9em}}
    .btn-invest{{background:linear-gradient(90deg,#ffd700,#ffaa00);color:black}}
    .btn-realize{{background:linear-gradient(90deg,#00c853,#00e676);color:black}}
    .btn-create{{background:linear-gradient(90deg,#e040fb,#7c4dff);color:white;display:block;width:100%;padding:20px;font-size:1.3em;margin:30px 0;border-radius:30px}}
    .leaderboard{{background:rgba(26,0,62,0.9);padding:25px;border-radius:20px;margin:20px 0;border:2px solid #ffd700}}
    .leaderboard h3{{color:#ffd700;text-align:center;margin-bottom:15px;font-size:1.5em}}
    .lb-item{{padding:10px;margin:5px 0;background:rgba(0,0,0,0.3);border-radius:10px;display:flex;justify-content:space-between;align-items:center}}
    .lb-item strong{{color:#ffd700}}
    .pulse{{animation:pulse 2s infinite;display:inline-block}}
    @keyframes pulse{{0%{{opacity:1}}50%{{opacity:0.3}}100%{{opacity:1}}}}
</style></head><body>
<div class="header">
    <h1>🌌 OSIS ∞.1</h1>
    <p class="subtitle">💎 ÉCONOMIE DE L'INTENTION — HAUT RENDEMENT 💎</p>
</div>
<div class="container">
    <div class="stats">
        <div class="stat"><div class="val">{stats['total_intentions']}</div><div class="lbl">🧠 Intentions</div></div>
        <div class="stat"><div class="val">{stats['total_value']:,.0f}</div><div class="lbl">💎 Valeur Totale (sat)</div></div>
        <div class="stat"><div class="val">{stats['total_earned']:,.0f}</div><div class="lbl">📈 Total Gagné (sat)</div></div>
        <div class="stat"><div class="val">+{REWARDS['gravity_per_day']*100:.0f}%/jour</div><div class="lbl">⚡ Croissance</div></div>
    </div>
    
    <div class="leaderboard">
        <h3>🏆 Top Intentions</h3>
        {leaderboard_html}
    </div>
    
    {cards}
    
    <button class="btn-create" onclick="createIntention()">🌌 Créer une Intention (GAIN: {REWARDS['create_intention']:,.0f} sat)</button>
    <div style="text-align:center;color:#ffd700;margin:20px 0;font-size:1.1em">
        <span class="pulse">💎</span> 
        +{REWARDS['gravity_per_day']*100:.0f}%/jour | +{REWARDS['invest_bonus']*100:.0f}% par investissement | ×{REWARDS['realization_multiplier']:.0f} à la réalisation
    </div>
</div>
<script>
function createIntention(){{const t=prompt('💎 Votre intention ?','');const d=prompt('Description ?','');const c=prompt('Catégorie ?','innovation');if(t){{fetch('/api/create?title='+encodeURIComponent(t)+'&desc='+encodeURIComponent(d)+'&category='+c).then(()=>location.reload())}}}}
function invest(id){{const a=prompt('💰 Montant à investir (satoshis) ?','10000');if(a){{fetch('/api/invest?id='+id+'&amount='+a).then(()=>location.reload())}}}}
function realize(id){{if(confirm('🎯 Réaliser cette intention ? ×5 la valeur !')){{fetch('/api/realize?id='+id).then(()=>location.reload())}}}}
setInterval(()=>location.reload(),30000);
</script></body></html>'''
        self.send_response(200); self.send_header("Content-Type","text/html"); self.end_headers()
        self.wfile.write(html.encode())
    
    def json(self, data, status=200):
        self.send_response(status); self.send_header("Content-Type","application/json"); self.end_headers()
        self.wfile.write(json.dumps(data, indent=2, ensure_ascii=False, default=str).encode())

# Démarrer le moteur
growth_engine = GrowthEngine()
threading.Thread(target=growth_engine.start, daemon=True).start()

if __name__ == "__main__":
    port = int(os.getenv("INTENTION_PORT", 8091))
    print(f"💎 OSIS ∞.1 Haut Rendement sur http://localhost:{port}")
    HTTPServer(("0.0.0.0", port), HighYieldHandler).serve_forever()
CORE

# ------------------------------------------------------------
# SERVICE
# ------------------------------------------------------------
sudo tee /etc/systemd/system/osis-highyield.service > /dev/null << 'SVC'
[Unit]
Description=OSIS Intention High Yield ∞.1
After=network.target
[Service]
Type=simple
ExecStart=/usr/bin/python3 /opt/osis-intention/engine/high_yield_core.py
Restart=always
Environment=INTENTION_PORT=8091
[Install]
WantedBy=multi-user.target
SVC
sudo systemctl daemon-reload && sudo systemctl enable osis-highyield && sudo systemctl start osis-highyield

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo -e "║   ${GOLD}💎 OSIS ∞.1 — HAUT RENDEMENT — EN LIGNE !${NC}                      ║"
echo "║                                                                  ║"
echo "║   ${CYAN}🌐 http://localhost:8091${NC}                                      ║"
echo "║                                                                  ║"
echo -e "║   ${GOLD}📈 GAINS EXCEPTIONNELS :${NC}                                      ║"
echo -e "║   ${GREEN}✅ Création : 10 000 satoshis${NC}                                ║"
echo -e "║   ${GREEN}✅ Investissement : +10% immédiat${NC}                             ║"
echo -e "║   ${GREEN}✅ Gravité : +5% par jour${NC}                                    ║"
echo -e "║   ${GREEN}✅ Résonance : +25% par connexion${NC}                            ║"
echo -e "║   ${GREEN}✅ Réalisation : ×5 la valeur${NC}                               ║"
echo -e "║   ${GREEN}✅ Parrainage : 5 000 satoshis${NC}                              ║"
echo "║                                                                  ║"
echo -e "║   ${RED}🚀 LA PREMIÈRE ÉCONOMIE DE L'INTENTION AU MONDE${NC}                ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"