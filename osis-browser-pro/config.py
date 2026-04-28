#!/bin/bash
# =============================================================================
# 🌐 OSIS BROWSER PRO — GAINS MAXIMUM
# =============================================================================
# Des gains EXCEPTIONNELS pour chaque action de navigation
# =============================================================================
set -e

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; GOLD='\033[0;33m'; RED='\033[0;31m'; PURPLE='\033[0;35m'; NC='\033[0m'
echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║   🌐 OSIS BROWSER PRO — GAINS MAXIMUM                            ║"
echo "║                                                                  ║"
echo "║   « Naviguez comme un roi. Gagnez comme un roi. »                ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

BASE_DIR="/opt/osis-browser-pro"
sudo mkdir -p $BASE_DIR && sudo chown -R $USER:$USER $BASE_DIR
mkdir -p $BASE_DIR/{backend,frontend,extension,data,logs,static}

# ============================================================
# CONSTANTES DE GAINS MAXIMUM
# ============================================================
cat > $BASE_DIR/backend/rewards_config.py << 'CONFIG'
# 💎 OSIS BROWSER PRO — CONFIGURATION DES GAINS MAXIMUM

REWARDS = {
    # Navigation
    "tab_open": 500.0,              # 500 sat par onglet
    "search": 1000.0,               # 1 000 sat par recherche
    "minute_browsing": 100.0,       # 100 sat par minute
    "hour_browsing": 5000.0,        # 5 000 sat par heure (bonus)
    "page_view": 50.0,              # 50 sat par page consultée
    "scroll_1000px": 200.0,         # 200 sat par 1000px scrollés
    
    # Interaction
    "bookmark": 2000.0,             # 2 000 sat par favori
    "share": 5000.0,                # 5 000 sat par partage
    "download": 3000.0,             # 3 000 sat par téléchargement
    "form_submit": 1500.0,          # 1 500 sat par formulaire
    "comment": 2500.0,              # 2 500 sat par commentaire
    
    # Fidélité
    "daily_login": 10000.0,         # 10 000 sat par jour
    "weekly_streak": 50000.0,       # 50 000 sat par semaine
    "monthly_streak": 250000.0,     # 250 000 sat par mois
    "referral": 50000.0,            # 50 000 sat par parrainage
    "referral_bonus": 0.10,         # 10% des gains du filleul
    
    # Premium
    "premium_multiplier": 3.0,      # ×3 pour les utilisateurs premium
    "vip_multiplier": 10.0,         # ×10 pour les utilisateurs VIP
    
    # Bonus
    "first_tab_day": 5000.0,        # 5 000 sat premier onglet du jour
    "tenth_tab_day": 25000.0,       # 25 000 sat 10ème onglet
    "hundredth_search": 100000.0,   # 100 000 sat 100ème recherche
    "night_owl_bonus": 15000.0,     # 15 000 sat navigation nocturne
    "early_bird_bonus": 15000.0,    # 15 000 sat navigation matinale
}

# Gains estimés par jour selon le type d'utilisateur
ESTIMATED_DAILY = {
    "light": 50000,      # Navigation légère (1h/jour)
    "normal": 250000,    # Navigation normale (4h/jour)
    "heavy": 1000000,    # Navigation intensive (8h/jour)
    "power": 5000000,    # Power user (12h+/jour)
}

# Palier de retrait minimum
MIN_WITHDRAWAL = 100000  # 100 000 sat minimum pour retirer
CONFIG

# ============================================================
# MOTEUR DE RÉCOMPENSES HAUTE FRÉQUENCE
# ============================================================
cat > $BASE_DIR/backend/high_reward_engine.py << 'ENGINE'
#!/usr/bin/env python3
"""
💎 OSIS BROWSER PRO — Moteur de Récompenses Maximum
"""
import json, time, os, sqlite3, random, hashlib, threading, math
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Importer la configuration
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rewards_config import REWARDS, ESTIMATED_DAILY, MIN_WITHDRAWAL

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(BASE, 'data', 'browser_pro.db')
os.makedirs(os.path.dirname(DB), exist_ok=True)

class ProDB:
    def __init__(self):
        self.conn = sqlite3.connect(DB)
        self.conn.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT,
                total_earned REAL DEFAULT 0,
                today_earned REAL DEFAULT 0,
                level INTEGER DEFAULT 1,
                premium INTEGER DEFAULT 0,
                vip INTEGER DEFAULT 0,
                referral_code TEXT UNIQUE,
                referred_by INTEGER,
                tabs_today INTEGER DEFAULT 0,
                searches_today INTEGER DEFAULT 0,
                minutes_today INTEGER DEFAULT 0,
                streak_days INTEGER DEFAULT 0,
                last_login TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            );
            
            CREATE TABLE IF NOT EXISTS earnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                source TEXT NOT NULL,
                amount REAL NOT NULL,
                multiplier REAL DEFAULT 1.0,
                created_at TEXT DEFAULT (datetime('now'))
            );
            
            CREATE TABLE IF NOT EXISTS daily_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                total_earned REAL DEFAULT 0,
                tabs INTEGER DEFAULT 0,
                searches INTEGER DEFAULT 0,
                minutes INTEGER DEFAULT 0
            );
            
            CREATE TABLE IF NOT EXISTS withdrawals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                address TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TEXT DEFAULT (datetime('now'))
            );
        ''')
        self.conn.commit()
    
    def create_user(self, username, email="", referral_code=None):
        try:
            ref = hashlib.md5(f"{username}{time.time()}".encode()).hexdigest()[:8].upper()
            cursor = self.conn.execute(
                "INSERT INTO users (username, email, referral_code, referred_by) VALUES (?,?,?, (SELECT id FROM users WHERE referral_code = ?))",
                (username, email, ref, referral_code)
            )
            self.conn.commit()
            return cursor.lastrowid
        except: return None
    
    def add_earning(self, user_id, source, base_amount):
        """Ajoute un gain avec multiplicateur de niveau"""
        user = self.get_user(user_id)
        if not user: return 0
        
        # Calcul du multiplicateur
        multiplier = 1.0
        multiplier *= (1 + (user["level"] - 1) * 0.1)  # +10% par niveau
        if user["premium"]: multiplier *= REWARDS["premium_multiplier"]
        if user["vip"]: multiplier *= REWARDS["vip_multiplier"]
        
        final_amount = round(base_amount * multiplier, 8)
        
        self.conn.execute(
            "INSERT INTO earnings (user_id, source, amount, multiplier) VALUES (?,?,?,?)",
            (user_id, source, final_amount, multiplier)
        )
        self.conn.execute(
            "UPDATE users SET total_earned = total_earned + ?, today_earned = today_earned + ? WHERE id = ?",
            (final_amount, final_amount, user_id)
        )
        
        # Mise à jour des compteurs
        if source == "tab_open": self.conn.execute("UPDATE users SET tabs_today = tabs_today + 1 WHERE id = ?", (user_id,))
        elif source == "search": self.conn.execute("UPDATE users SET searches_today = searches_today + 1 WHERE id = ?", (user_id,))
        elif source == "minute_browsing": self.conn.execute("UPDATE users SET minutes_today = minutes_today + 1 WHERE id = ?", (user_id,))
        
        self.conn.commit()
        return final_amount
    
    def daily_login(self, user_id):
        """Bonus de connexion quotidienne"""
        user = self.get_user(user_id)
        if not user: return 0
        
        now = datetime.now()
        last = user["last_login"]
        
        if last:
            last_date = datetime.strptime(last, "%Y-%m-%d %H:%M:%S")
            days_diff = (now - last_date).days
            
            if days_diff == 1:
                self.conn.execute("UPDATE users SET streak_days = streak_days + 1 WHERE id = ?", (user_id,))
            elif days_diff > 1:
                self.conn.execute("UPDATE users SET streak_days = 1 WHERE id = ?", (user_id,))
        else:
            self.conn.execute("UPDATE users SET streak_days = 1 WHERE id = ?", (user_id,))
        
        # Calcul du bonus selon la streak
        streak = self.conn.execute("SELECT streak_days FROM users WHERE id = ?", (user_id,)).fetchone()[0]
        
        bonus = REWARDS["daily_login"]
        if streak >= 7: bonus += REWARDS["weekly_streak"]
        if streak >= 30: bonus += REWARDS["monthly_streak"]
        
        self.conn.execute("UPDATE users SET last_login = datetime('now'), today_earned = 0, tabs_today = 0, searches_today = 0, minutes_today = 0 WHERE id = ?", (user_id,))
        self.conn.commit()
        
        return self.add_earning(user_id, "daily_login", bonus)
    
    def check_special_bonuses(self, user_id):
        """Vérifie les bonus spéciaux"""
        user = self.get_user(user_id)
        if not user: return []
        
        bonuses = []
        
        # Premier onglet du jour
        if user["tabs_today"] == 1:
            amount = self.add_earning(user_id, "first_tab_day", REWARDS["first_tab_day"])
            bonuses.append(("Premier onglet du jour !", amount))
        
        # 10ème onglet
        if user["tabs_today"] == 10:
            amount = self.add_earning(user_id, "tenth_tab_day", REWARDS["tenth_tab_day"])
            bonuses.append(("10ème onglet !", amount))
        
        # 100ème recherche
        if user["searches_today"] == 100:
            amount = self.add_earning(user_id, "hundredth_search", REWARDS["hundredth_search"])
            bonuses.append(("100ème recherche !", amount))
        
        # Bonus nocturne (22h-6h)
        hour = datetime.now().hour
        if hour >= 22 or hour <= 6:
            amount = self.add_earning(user_id, "night_owl_bonus", REWARDS["night_owl_bonus"])
            bonuses.append(("🦉 Bonus nocturne !", amount))
        
        # Bonus matinal (6h-9h)
        if 6 <= hour <= 9:
            amount = self.add_earning(user_id, "early_bird_bonus", REWARDS["early_bird_bonus"])
            bonuses.append(("🌅 Bonus matinal !", amount))
        
        return bonuses
    
    def get_user(self, user_id):
        row = self.conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if row:
            cols = [c[0] for c in self.conn.execute("PRAGMA table_info(users)")]
            return dict(zip(cols, row))
        return None
    
    def get_leaderboard(self, limit=10):
        rows = self.conn.execute(
            "SELECT username, total_earned, level, premium, vip FROM users ORDER BY total_earned DESC LIMIT ?",
            (limit,)
        ).fetchall()
        return [{"username": r[0], "total_earned": r[1], "level": r[2], "premium": bool(r[3]), "vip": bool(r[4])} for r in rows]
    
    def withdraw(self, user_id, amount, address):
        user = self.get_user(user_id)
        if not user or user["total_earned"] < amount:
            return False, "Solde insuffisant"
        if amount < MIN_WITHDRAWAL:
            return False, f"Minimum {MIN_WITHDRAWAL} sat pour retirer"
        
        self.conn.execute("UPDATE users SET total_earned = total_earned - ? WHERE id = ?", (amount, user_id))
        self.conn.execute("INSERT INTO withdrawals (user_id, amount, address) VALUES (?,?,?)", (user_id, amount, address))
        self.conn.commit()
        return True, f"{amount} sat retirés vers {address[:10]}..."

db = ProDB()

# Utilisateur démo
if not db.get_user(1):
    db.create_user("demo", "demo@osis.io")
    db.conn.execute("UPDATE users SET level = 5, premium = 1 WHERE id = 1")
    db.conn.commit()

# =============================================
# API
# =============================================
class ProHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)
        
        if path == "/health":
            self.json({"status": "ok", "service": "osis-browser-pro", "version": "2.0"})
        
        elif path == "/api/rewards":
            self.json(REWARDS)
        
        elif path == "/api/estimated":
            self.json(ESTIMATED_DAILY)
        
        elif path == "/api/user":
            uid = int(params.get("user_id", [1])[0])
            user = db.get_user(uid)
            if user:
                user["estimated_daily"] = ESTIMATED_DAILY["normal"] * (1 + (user["level"]-1)*0.1) * (REWARDS["premium_multiplier"] if user["premium"] else 1)
            self.json(user or {"error": "Utilisateur non trouvé"})
        
        elif path == "/api/leaderboard":
            self.json(db.get_leaderboard(20))
        
        elif path == "/api/earn":
            uid = int(params.get("user_id", [1])[0])
            source = params.get("source", ["minute_browsing"])[0]
            
            # Vérifier si c'est une nouvelle journée
            user = db.get_user(uid)
            if user and user["last_login"]:
                last = datetime.strptime(user["last_login"], "%Y-%m-%d %H:%M:%S")
                if last.date() < datetime.now().date():
                    db.daily_login(uid)
            
            base = REWARDS.get(source, 100)
            amount = db.add_earning(uid, source, base)
            
            # Bonus spéciaux
            bonuses = db.check_special_bonuses(uid)
            
            user = db.get_user(uid)
            self.json({
                "earned": amount,
                "source": source,
                "total_earned": user["total_earned"],
                "today_earned": user["today_earned"],
                "level": user["level"],
                "streak": user["streak_days"],
                "bonuses": [{"name": b[0], "amount": b[1]} for b in bonuses] if bonuses else [],
                "estimated_daily": ESTIMATED_DAILY["normal"] * (1 + (user["level"]-1)*0.1)
            })
        
        elif path == "/api/daily_login":
            uid = int(params.get("user_id", [1])[0])
            amount = db.daily_login(uid)
            user = db.get_user(uid)
            self.json({
                "login_bonus": amount,
                "total_earned": user["total_earned"],
                "streak": user["streak_days"]
            })
        
        elif path == "/api/withdraw":
            uid = int(params.get("user_id", [1])[0])
            amount = float(params.get("amount", [0])[0])
            address = params.get("address", [""])[0]
            success, msg = db.withdraw(uid, amount, address)
            self.json({"success": success, "message": msg})
        
        elif path == "/":
            self.serve_dashboard()
        
        else:
            self.json({"error": "Not found"}, 404)
    
    def serve_dashboard(self):
        user = db.get_user(1)
        leaderboard = db.get_leaderboard(10)
        
        stars = "⭐" * min(5, user["level"] // 10)
        premium_badge = "💎 PREMIUM" if user["premium"] else ""
        vip_badge = "👑 VIP" if user["vip"] else ""
        
        lb_html = ""
        for i, u in enumerate(leaderboard):
            medals = ["🥇","🥈","🥉"]
            prefix = medals[i] if i < 3 else f"{i+1}."
            badges = ""
            if u["vip"]: badges += "👑"
            if u["premium"]: badges += "💎"
            lb_html += f'<div class="lb-item"><span>{prefix}</span> {badges} {u["username"]} <strong>{u["total_earned"]:,.0f} sat</strong> <small>Nv.{u["level"]}</small></div>'
        
        html = f'''<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>💎 OSIS Browser PRO</title>
<style>
    *{{margin:0;padding:0;box-sizing:border-box}}
    body{{background:#050510;color:white;font-family:sans-serif;min-height:100vh}}
    .header{{background:linear-gradient(135deg,#1a0030,#0a0030,#001a30);padding:30px;text-align:center;border-bottom:3px solid #ffd700}}
    .header h1{{font-size:3em;background:linear-gradient(90deg,#ffd700,#ffaa00,#ffd700);-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:shine 2s infinite}}
    @keyframes shine{{0%{{filter:brightness(1)}}50%{{filter:brightness(1.5)}}100%{{filter:brightness(1)}}}}
    .header .subtitle{{color:#ffd700;font-size:1.2em;margin-top:10px}}
    .badge{{display:inline-block;padding:5px 15px;border-radius:20px;margin:5px;font-weight:bold;font-size:0.9em}}
    .badge-premium{{background:linear-gradient(90deg,#ffd700,#ffaa00);color:black}}
    .badge-vip{{background:linear-gradient(90deg,#e040fb,#7c4dff);color:white}}
    .container{{max-width:1400px;margin:0 auto;padding:20px}}
    .stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:20px;margin:30px 0}}
    .stat{{background:rgba(26,0,62,0.9);padding:25px;border-radius:20px;text-align:center;border:2px solid #ffd700}}
    .stat .val{{font-size:2.5em;color:#ffd700;font-weight:bold}}
    .stat .lbl{{color:#aaa;margin-top:5px;font-size:0.9em}}
    .stat.highlight{{border-color:#e040fb;animation:glow 2s infinite}}
    @keyframes glow{{0%{{box-shadow:0 0 10px #e040fb}}50%{{box-shadow:0 0 30px #e040fb}}100%{{box-shadow:0 0 10px #e040fb}}}}
    .grid{{display:grid;grid-template-columns:2fr 1fr;gap:20px;margin:30px 0}}
    .earn-actions{{background:rgba(26,0,62,0.9);padding:25px;border-radius:20px;border:1px solid #4a0080}}
    .earn-actions h3{{color:#ffd700;margin-bottom:20px;text-align:center}}
    .action-btn{{display:block;width:100%;padding:18px;margin:12px 0;border:none;border-radius:25px;font-weight:bold;cursor:pointer;font-size:1em;text-align:left;color:white;background:#2a005a}}
    .action-btn:hover{{background:#4a0080;transform:scale(1.02)}}
    .action-btn .reward{{float:right;color:#ffd700;font-weight:bold}}
    .leaderboard{{background:rgba(26,0,62,0.9);padding:25px;border-radius:20px;border:2px solid #ffd700}}
    .leaderboard h3{{color:#ffd700;text-align:center;margin-bottom:20px;font-size:1.5em}}
    .lb-item{{padding:12px;margin:5px 0;background:rgba(0,0,0,0.3);border-radius:10px;display:flex;justify-content:space-between;align-items:center}}
    .lb-item strong{{color:#ffd700;font-size:1.1em}}
    .lb-item small{{color:#888}}
    .bonus-alert{{background:linear-gradient(90deg,#ffd700,#ffaa00);color:black;padding:15px;border-radius:15px;text-align:center;margin:15px 0;font-weight:bold;animation:slideIn 0.5s ease}}
    @keyframes slideIn{{from{{transform:translateY(-20px);opacity:0}}to{{transform:translateY(0);opacity:1}}}}
    .progress-bar{{background:#1a0030;height:10px;border-radius:10px;margin:10px 0;overflow:hidden}}
    .progress-fill{{background:linear-gradient(90deg,#ffd700,#ffaa00);height:100%;border-radius:10px}}
</style></head><body>
<div class="header">
    <h1>💎 OSIS Browser PRO</h1>
    <p class="subtitle">Naviguez. Gagnez. Devenez Riche.</p>
    {f'<span class="badge badge-premium">{premium_badge}</span>' if premium_badge else ''}
    {f'<span class="badge badge-vip">{vip_badge}</span>' if vip_badge else ''}
    <span class="badge" style="background:#2a005a">Niveau {user["level"]} {stars}</span>
    <span class="badge" style="background:#2a005a">🔥 {user["streak_days"]} jours</span>
</div>
<div class="container">
    <div class="stats">
        <div class="stat highlight"><div class="val">{user["total_earned"]:,.0f}</div><div class="lbl">💰 Total Gagné (sat)</div></div>
        <div class="stat"><div class="val">{user["today_earned"]:,.0f}</div><div class="lbl">📅 Aujourd'hui (sat)</div></div>
        <div class="stat"><div class="val">~{ESTIMATED_DAILY["normal"]:,.0f}</div><div class="lbl">📈 Estimé / Jour (sat)</div></div>
        <div class="stat"><div class="val">×{REWARDS["premium_multiplier"]:.0f}</div><div class="lbl">💎 Multiplicateur</div></div>
    </div>
    
    <div class="grid">
        <div class="earn-actions">
            <h3>⚡ Actions Rapides</h3>
            <button class="action-btn" onclick="earn('tab_open')">📑 Nouvel Onglet <span class="reward">+{REWARDS["tab_open"]:,.0f} sat</span></button>
            <button class="action-btn" onclick="earn('search')">🔍 Recherche <span class="reward">+{REWARDS["search"]:,.0f} sat</span></button>
            <button class="action-btn" onclick="earn('bookmark')">⭐ Favori <span class="reward">+{REWARDS["bookmark"]:,.0f} sat</span></button>
            <button class="action-btn" onclick="earn('share')">📤 Partager <span class="reward">+{REWARDS["share"]:,.0f} sat</span></button>
            <button class="action-btn" onclick="earn('download')">📥 Télécharger <span class="reward">+{REWARDS["download"]:,.0f} sat</span></button>
            <button class="action-btn" onclick="earn('comment')">💬 Commenter <span class="reward">+{REWARDS["comment"]:,.0f} sat</span></button>
        </div>
        <div class="leaderboard">
            <h3>🏆 Top Gagnants</h3>
            {lb_html}
        </div>
    </div>
    
    <div style="text-align:center;margin:30px 0">
        <p style="color:#888">💰 Minimum retrait : {MIN_WITHDRAWAL:,} sat</p>
        <button onclick="withdraw()" style="padding:15px 40px;background:#ffd700;color:black;border:none;border-radius:25px;font-size:1.2em;font-weight:bold;cursor:pointer">💸 Retirer mes gains</button>
    </div>
</div>

<script>
const API='http://localhost:8101/api';const UID=1;
async function earn(source){{try{{const r=await fetch(API+'/earn?user_id='+UID+'&source='+source);const d=await r.json();alert('💰 +'+d.earned.toFixed(0)+' sat !\\nTotal: '+d.total_earned.toFixed(0)+' sat\\nAujourd\\'hui: '+d.today_earned.toFixed(0)+' sat');if(d.bonuses.length)alert('🎁 Bonus: '+d.bonuses.map(b=>b.name+' +'+b.amount).join('\\n'));location.reload()}}catch(e){{}}}}
async function withdraw(){{const a=prompt('Montant (min {MIN_WITHDRAWAL} sat) ?','{MIN_WITHDRAWAL}');const addr=prompt('Adresse BTC ?','');if(a&&addr){{const r=await fetch(API+'/withdraw?user_id='+UID+'&amount='+a+'&address='+addr);const d=await r.json();alert(d.message);location.reload()}}}}
setInterval(()=>earn('minute_browsing'),60000);
</script></body></html>'''
        self.send_response(200); self.send_header("Content-Type","text/html"); self.end_headers()
        self.wfile.write(html.encode())
    
    def json(self, data, status=200):
        self.send_response(status); self.send_header("Content-Type","application/json"); self.send_header("Access-Control-Allow-Origin","*"); self.end_headers()
        self.wfile.write(json.dumps(data, indent=2, ensure_ascii=False, default=str).encode())

if __name__ == "__main__":
    port = int(os.getenv("BROWSER_PRO_PORT", 8101))
    print(f"💎 OSIS Browser PRO sur http://localhost:{port}")
    HTTPServer(("0.0.0.0", port), ProHandler).serve_forever()
ENGINE

# ------------------------------------------------------------
# SERVICE
# ------------------------------------------------------------
sudo tee /etc/systemd/system/osis-browser-pro.service > /dev/null << 'SVC'
[Unit]
Description=OSIS Browser PRO - High Rewards
After=network.target
[Service]
Type=simple
ExecStart=/usr/bin/python3 /opt/osis-browser-pro/backend/high_reward_engine.py
Restart=always
Environment=BROWSER_PRO_PORT=8101
[Install]
WantedBy=multi-user.target
SVC
sudo systemctl daemon-reload && sudo systemctl enable osis-browser-pro && sudo systemctl start osis-browser-pro

# Mise à jour de l'extension
mkdir -p $BASE_DIR/extension
cat > $BASE_DIR/extension/popup.html << 'POPUP'
<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
body{width:380px;background:#050510;color:white;font-family:sans-serif;padding:20px;margin:0}
h1{color:#ffd700;text-align:center;font-size:1.5em;margin:0}
.earn{text-align:center;font-size:3em;color:#ffd700;font-weight:bold;margin:15px 0}
.earn small{font-size:0.3em;color:#888;display:block}
.btn{display:block;width:100%;padding:12px;margin:8px 0;border:none;border-radius:25px;font-weight:bold;cursor:pointer;font-size:1em;text-align:center}
.btn-earn{background:#ffd700;color:black}
.btn-intent{background:#7c4dff;color:white}
.btn-garden{background:#00c853;color:black}
.stats{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:15px 0}
.st{background:#1a0030;padding:10px;border-radius:10px;text-align:center}
.st .v{color:#ffd700;font-weight:bold;font-size:1.2em}
.st .l{color:#888;font-size:0.7em;margin-top:3px}
</style></head><body>
<h1>💎 OSIS Browser PRO</h1>
<div class="earn" id="total">0<div><small>satoshis gagnés</small></div></div>
<div class="stats">
<div class="st"><div class="v" id="today">0</div><div class="l">📅 Aujourd'hui</div></div>
<div class="st"><div class="v" id="level">1</div><div class="l">⭐ Niveau</div></div>
<div class="st"><div class="v" id="streak">0</div><div class="l">🔥 Streak</div></div>
<div class="st"><div class="v" id="est">0</div><div class="l">📈 Estimé/jour</div></div>
</div>
<button class="btn btn-earn" onclick="earn('tab_open')">📑 Nouvel Onglet (+500 sat)</button>
<button class="btn btn-earn" onclick="earn('search')">🔍 Recherche (+1 000 sat)</button>
<button class="btn btn-earn" onclick="earn('bookmark')">⭐ Favori (+2 000 sat)</button>
<button class="btn btn-intent" onclick="window.open('http://localhost:8091')">🌌 Intentions (Haut Rendement)</button>
<button class="btn btn-garden" onclick="window.open('http://localhost:8070')">🌱 Jardin Financier</button>
<script>
const API='http://localhost:8101/api';const UID=1;
async function load(){{try{{const r=await fetch(API+'/user?user_id='+UID);const d=await r.json();
document.getElementById('total').innerHTML=d.total_earned?.toFixed(0)||'0';
document.getElementById('today').textContent=d.today_earned?.toFixed(0)||'0';
document.getElementById('level').textContent=d.level||1;
document.getElementById('streak').textContent=d.streak_days||0;
document.getElementById('est').textContent=d.estimated_daily?.toFixed(0)||'0';
}}catch(e){{}}}
async function earn(s){{try{{const r=await fetch(API+'/earn?user_id='+UID+'&source='+s);const d=await r.json();alert('💰 +'+d.earned.toFixed(0)+' sat !\\nTotal: '+d.total_earned.toFixed(0)+' sat');load()}}catch(e){{}}}}
load();setInterval(load,30000);
</script></body></html>
POPUP

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo -e "║   ${GOLD}💎 OSIS BROWSER PRO — GAINS MAXIMUM — EN LIGNE !${NC}                ║"
echo "║                                                                  ║"
echo -e "║   ${CYAN}🌐 Dashboard : http://localhost:8101${NC}                              ║"
echo "║                                                                  ║"
echo -e "║   ${GOLD}📈 GAINS PAR ACTION :${NC}                                             ║"
echo -e "║   ${GREEN}📑 Onglet : 500 sat${NC}                                               ║"
echo -e "║   ${GREEN}🔍 Recherche : 1 000 sat${NC}                                         ║"
echo -e "║   ${GREEN}⏱️  Minute : 100 sat${NC}                                             ║"
echo -e "║   ${GREEN}⭐ Favori : 2 000 sat${NC}                                            ║"
echo -e "║   ${GREEN}📤 Partage : 5 000 sat${NC}                                          ║"
echo -e "║   ${GREEN}🎁 Connexion : 10 000 sat${NC}                                       ║"
echo -e "║   ${GREEN}👥 Parrainage : 50 000 sat${NC}                                      ║"
echo "║                                                                  ║"
echo -e "║   ${PURPLE}💰 ESTIMÉS QUOTIDIENS :${NC}                                          ║"
echo -e "║   ${GOLD}🌱 Léger (1h) : ~50 000 sat/jour${NC}                                 ║"
echo -e "║   ${GOLD}🌿 Normal (4h) : ~250 000 sat/jour${NC}                               ║"
echo -e "║   ${GOLD}🌳 Intensif (8h) : ~1 000 000 sat/jour${NC}                           ║"
echo -e "║   ${GOLD}🏆 Power (12h+) : ~5 000 000 sat/jour${NC}                           ║"
echo "║                                                                  ║"
echo -e "║   ${RED}💎 AVEC PREMIUM (×3) ET VIP (×10) — MULTIPLIEZ VOS GAINS !${NC}       ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"