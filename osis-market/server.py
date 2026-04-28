#!/bin/bash
set -e

GREEN='\033[0;32m'; CYAN='\033[0;36m'; YELLOW='\033[1;33m'; GOLD='\033[0;33m'; NC='\033[0m'
echo -e "${GREEN}🌲 OSIS — Nouveaux Marchés Stratégiques${NC}"

BASE_DIR="/opt/osis-markets"
sudo mkdir -p $BASE_DIR && sudo chown -R $USER:$USER $BASE_DIR
mkdir -p $BASE_DIR/{carbon-credits,agri-piney,certification,artisan-market,microtasks,identity}

# ============================================================
# 1. MARCHÉ DES CRÉDITS CARBONE TOKENISÉS ($50 Milliards)
# ============================================================
echo -e "${CYAN}🌍 Module Crédits Carbone Tokenisés...${NC}"

cat > $BASE_DIR/carbon-credits/server.py << 'CARBON'
#!/usr/bin/env python3
"""
OSIS Carbon Credits — Marché des Crédits Carbone Tokenisés
Potentiel : $50 Milliards
Comment ça marche :
- Les robots Piney mesurent la séquestration carbone des arbres
- Chaque tonne de CO2 séquestrée génère un token CARBON
- Les entreprises achètent ces tokens pour compenser leurs émissions
- Les agriculteurs/planteurs sont rémunérés directement
"""
import json, os, sqlite3, random, time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

DB = os.path.join(os.path.dirname(__file__), 'carbon.db')
os.makedirs(os.path.dirname(DB), exist_ok=True)

class CarbonDB:
    def __init__(self):
        self.c = sqlite3.connect(DB)
        self.c.executescript('''
            CREATE TABLE IF NOT EXISTS projects(id INTEGER PRIMARY KEY, name TEXT, location TEXT, trees_planted INTEGER, co2_sequestered REAL, tokens_issued REAL DEFAULT 0, price_per_ton REAL DEFAULT 25.0);
            CREATE TABLE IF NOT EXISTS credits(id INTEGER PRIMARY KEY, project_id INTEGER, owner_id INTEGER, tons REAL, token_id TEXT UNIQUE, price_paid REAL, created_at DATETIME DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS buyers(id INTEGER PRIMARY KEY, name TEXT, credits_purchased REAL, total_spent REAL);
        ''')
        if not self.c.execute("SELECT COUNT(*) FROM projects").fetchone()[0]:
            projects = [
                ("Forêt du Sahel", "Mali", 50000, 12500.0),
                ("Mangroves Sénégal", "Sénégal", 100000, 25000.0),
                ("Reforestation Kenya", "Kenya", 75000, 18750.0),
                ("Agroforesterie Côte d'Ivoire", "Côte d'Ivoire", 30000, 7500.0),
            ]
            for p in projects:
                self.c.execute("INSERT INTO projects(name,location,trees_planted,co2_sequestered,tokens_issued) VALUES(?,?,?,?,?)", (*p, p[3]/1000))
            self.c.commit()
    
    def buy_credits(self, buyer_name, tons):
        project = self.c.execute("SELECT * FROM projects WHERE co2_sequestered - tokens_issued >= ? ORDER BY price_per_ton ASC LIMIT 1", (tons,)).fetchone()
        if not project: return None
        total_price = tons * project[5]
        token_id = f"CARBON-{random.randint(10000,99999)}"
        self.c.execute("INSERT INTO credits(project_id,owner_id,tons,token_id,price_paid) VALUES(?,?,?,?,?)", (project[0], 1, tons, token_id, total_price))
        self.c.execute("UPDATE projects SET tokens_issued = tokens_issued + ? WHERE id = ?", (tons, project[0]))
        self.c.execute("INSERT OR IGNORE INTO buyers(name,credits_purchased,total_spent) VALUES(?,0,0)", (buyer_name,))
        self.c.execute("UPDATE buyers SET credits_purchased = credits_purchased + ?, total_spent = total_spent + ? WHERE name = ?", (tons, total_price, buyer_name))
        self.c.commit()
        return {"token_id": token_id, "tons": tons, "price": total_price, "project": project[1], "location": project[2]}

    def get_stats(self):
        total = self.c.execute("SELECT COALESCE(SUM(co2_sequestered),0) FROM projects").fetchone()[0]
        sold = self.c.execute("SELECT COALESCE(SUM(tokens_issued),0) FROM projects").fetchone()[0]
        revenue = self.c.execute("SELECT COALESCE(SUM(total_spent),0) FROM buyers").fetchone()[0]
        return {"total_tons": total, "sold_tons": sold, "revenue": revenue, "available": total - sold}

db = CarbonDB()

class H(BaseHTTPRequestHandler):
    def _cors(self): self.send_header("Access-Control-Allow-Origin","*"); self.send_header("Access-Control-Allow-Methods","GET,POST,OPTIONS"); self.send_header("Access-Control-Allow-Headers","Content-Type")
    def do_OPTIONS(self): self.send_response(200); self._cors(); self.end_headers()
    def _json(self, d, s=200): self.send_response(s); self._cors(); self.send_header("Content-Type","application/json"); self.end_headers(); self.wfile.write(json.dumps(d,default=str).encode())
    
    def do_GET(self):
        p = urlparse(self.path); q = parse_qs(p.query)
        if p.path == "/health": self._json({"status":"ok","market":"carbon-credits","potential":"$50B"})
        elif p.path == "/api/carbon/stats": self._json(db.get_stats())
        elif p.path == "/api/carbon/projects":
            rows = db.c.execute("SELECT * FROM projects").fetchall()
            self._json([{"id":r[0],"name":r[1],"location":r[2],"trees":r[3],"co2_tons":r[4],"sold":r[5],"price_per_ton":r[6]} for r in rows])
        elif p.path == "/api/carbon/buy":
            buyer = q.get("buyer",["Entreprise"])[0]; tons = float(q.get("tons",[100])[0])
            result = db.buy_credits(buyer, tons)
            if result: self._json({"success":True,"credit":result})
            else: self._json({"error":"Pas assez de crédits disponibles"},400)
        else:
            stats = db.get_stats()
            h = f'''<!DOCTYPE html><html><head><title>🌍 Crédits Carbone OSIS</title>
<style>body{{background:#0a1a0a;color:white;font-family:sans-serif;padding:30px;max-width:800px;margin:0 auto}}h1{{color:#00c853}}h2{{color:#ffd700}}.card{{background:#1a3e1a;padding:20px;border-radius:15px;margin:15px 0;border:1px solid #2a5a2a}}.stat{{font-size:2em;color:#00c853;font-weight:bold}}.btn{{background:#00c853;color:black;padding:12px 25px;border-radius:25px;border:none;font-weight:bold;cursor:pointer;margin:5px}}</style></head>
<body><h1>🌍 OSIS Carbon Credits</h1><p style="color:#aaa">Marché potentiel : <strong style="color:#ffd700">$50 Milliards</strong></p>
<div class="card"><h2>📊 Statistiques</h2><p>🌳 CO2 Séquestré : <span class="stat">{stats['total_tons']:.0f}</span> tonnes</p><p>💰 Vendus : {stats['sold_tons']:.0f} tonnes</p><p>💵 Revenus : {stats['revenue']:.0f} €</p><p>📦 Disponible : {stats['available']:.0f} tonnes</p></div>
<p style="color:#888;text-align:center">🤖 Les robots Piney mesurent la séquestration carbone en temps réel</p></body></html>'''
            self.send_response(200); self.send_header("Content-Type","text/html"); self.end_headers(); self.wfile.write(h.encode())

HTTPServer(("0.0.0.0", 8700), H).serve_forever()
CARBON

# ============================================================
# 2. MARKETPLACE ARTISANAT AFRICAIN ($8 Milliards)
# ============================================================
echo -e "${CYAN}🛍️ Module Marketplace Artisanat...${NC}"

cat > $BASE_DIR/artisan-market/server.py << 'ARTISAN'
#!/usr/bin/env python3
"""OSIS Artisan Market — Marketplace Artisanat Africain Global"""
import json, os, sqlite3
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

DB = os.path.join(os.path.dirname(__file__), 'artisan.db')
os.makedirs(os.path.dirname(DB), exist_ok=True)

class ArtisanDB:
    def __init__(self):
        self.c = sqlite3.connect(DB)
        self.c.executescript('''
            CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY, name TEXT, artisan TEXT, country TEXT, category TEXT, price_satoshi REAL, image_url TEXT, stock INTEGER, sales INTEGER DEFAULT 0);
            CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY, product_id INTEGER, buyer_id INTEGER, amount REAL, shipping_address TEXT, status TEXT DEFAULT 'pending');
        ''')
        if not self.c.execute("SELECT COUNT(*) FROM products").fetchone()[0]:
            products = [
                ("Tabouret Dogon", "Amadou Diallo", "Mali", "mobilier", 25000, 10),
                ("Tissu Bogolan", "Fatou Keita", "Mali", "textile", 15000, 25),
                ("Masque Baoulé", "Koffi Yao", "Côte d'Ivoire", "art", 50000, 3),
                ("Collier Touareg", "Amina Ag", "Niger", "bijoux", 35000, 15),
                ("Panier Wolof", "Marième Faye", "Sénégal", "vannerie", 8000, 50),
                ("Théière Berbère", "Hassan Ben", "Maroc", "artisanat", 45000, 8),
            ]
            for p in products:
                self.c.execute("INSERT INTO products(name,artisan,country,category,price_satoshi,stock) VALUES(?,?,?,?,?,?)", p)
            self.c.commit()
    
    def search(self, q="", category=""):
        if q: return self.c.execute("SELECT * FROM products WHERE name LIKE ? OR artisan LIKE ? OR country LIKE ?", (f"%{q}%", f"%{q}%", f"%{q}%")).fetchall()
        if category: return self.c.execute("SELECT * FROM products WHERE category=?", (category,)).fetchall()
        return self.c.execute("SELECT * FROM products").fetchall()

db = ArtisanDB()

class H(BaseHTTPRequestHandler):
    def _cors(self): self.send_header("Access-Control-Allow-Origin","*"); self.send_header("Access-Control-Allow-Methods","GET,POST,OPTIONS"); self.send_header("Access-Control-Allow-Headers","Content-Type")
    def do_OPTIONS(self): self.send_response(200); self._cors(); self.end_headers()
    def _json(self, d, s=200): self.send_response(s); self._cors(); self.send_header("Content-Type","application/json"); self.end_headers(); self.wfile.write(json.dumps(d,default=str).encode())
    
    def do_GET(self):
        p = urlparse(self.path); q = parse_qs(p.query)
        if p.path == "/health": self._json({"status":"ok","market":"artisan-africain","potential":"$8B"})
        elif p.path == "/api/products":
            rows = db.search(q.get("q",[""])[0], q.get("category",[""])[0])
            self._json([{"id":r[0],"name":r[1],"artisan":r[2],"country":r[3],"category":r[4],"price":r[5],"stock":r[7],"sales":r[8]} for r in rows])
        else:
            h = '<!DOCTYPE html><html><head><title>🛍️ Artisanat Africain</title><style>body{background:#1a0a0a;color:white;font-family:sans-serif;padding:20px}h1{color:#ff6b35}.card{background:#3e1a1a;padding:15px;border-radius:10px;margin:10px 0}.price{color:#ffd700;font-weight:bold}</style></head><body><h1>🛍️ OSIS Artisan Market</h1><p style="color:#aaa">Marché potentiel : <strong style="color:#ffd700">$8 Milliards</strong></p><input id="search" placeholder="Rechercher..." style="width:100%;padding:10px;border-radius:25px;border:none;margin:10px 0" onkeyup="search()"><div id="results"></div><script>async function search(){const q=document.getElementById("search").value;const r=await fetch("/api/products?q="+q);const d=await r.json();document.getElementById("results").innerHTML=d.map(p=>`<div class="card"><h3>${p.name}</h3><p>👤 ${p.artisan} | 📍 ${p.country}</p><p class="price">💰 ${p.price} sat | 📦 ${p.stock} en stock | 📈 ${p.sales} ventes</p></div>`).join("")}search()</script></body></html>'
            self.send_response(200); self.send_header("Content-Type","text/html"); self.end_headers(); self.wfile.write(h.encode())

HTTPServer(("0.0.0.0", 8701), H).serve_forever()
ARTISAN

# ============================================================
# 3. CERTIFICATION BLOCKCHAIN ($3 Milliards)
# ============================================================
echo -e "${CYAN}🎓 Module Certification Blockchain...${NC}"

cat > $BASE_DIR/certification/server.py << 'CERT'
#!/usr/bin/env python3
"""OSIS Certifications — Certificats Blockchain Vérifiables"""
import json, os, sqlite3, hashlib, time
from http.server import HTTPServer, BaseHTTPRequestHandler

DB = os.path.join(os.path.dirname(__file__), 'certs.db')
os.makedirs(os.path.dirname(DB), exist_ok=True)

class CertDB:
    def __init__(self):
        self.c = sqlite3.connect(DB)
        self.c.executescript('''
            CREATE TABLE IF NOT EXISTS certifications(id INTEGER PRIMARY KEY, holder_name TEXT, course TEXT, issuer TEXT, date TEXT, cert_hash TEXT UNIQUE, verified INTEGER DEFAULT 0);
            CREATE TABLE IF NOT EXISTS issuers(id INTEGER PRIMARY KEY, name TEXT, institution TEXT, verified INTEGER DEFAULT 0);
        ''')
        if not self.c.execute("SELECT COUNT(*) FROM certifications").fetchone()[0]:
            self.c.execute("INSERT INTO issuers(name,institution,verified) VALUES('Université de Bamako','Mali',1)")
            self.c.execute("INSERT INTO issuers(name,institution,verified) VALUES('Institut Polytechnique','Sénégal',1)")
            # Exemple
            h = hashlib.sha256(f"Fatou-Diallo-Blockchain-{time.time()}".encode()).hexdigest()[:16]
            self.c.execute("INSERT INTO certifications(holder_name,course,issuer,date,cert_hash,verified) VALUES('Fatou Diallo','Blockchain Avancé','Université de Bamako','2024-06-15',?,1)", (h,))
            self.c.commit()
    
    def verify(self, cert_hash):
        r = self.c.execute("SELECT * FROM certifications WHERE cert_hash=?", (cert_hash,)).fetchone()
        if r: return {"valid":True,"holder":r[1],"course":r[2],"issuer":r[3],"date":r[4]}
        return {"valid":False}

db = CertDB()

class H(BaseHTTPRequestHandler):
    def _cors(self): self.send_header("Access-Control-Allow-Origin","*"); self.send_header("Access-Control-Allow-Methods","GET,POST,OPTIONS"); self.send_header("Access-Control-Allow-Headers","Content-Type")
    def do_OPTIONS(self): self.send_response(200); self._cors(); self.end_headers()
    def _json(self, d, s=200): self.send_response(s); self._cors(); self.send_header("Content-Type","application/json"); self.end_headers(); self.wfile.write(json.dumps(d).encode())
    
    def do_GET(self):
        from urllib.parse import urlparse, parse_qs
        p = urlparse(self.path); q = parse_qs(p.query)
        if p.path == "/health": self._json({"status":"ok","market":"certification","potential":"$3B"})
        elif p.path == "/api/cert/verify":
            result = db.verify(q.get("hash",[""])[0])
            self._json(result)

HTTPServer(("0.0.0.0", 8702), H).serve_forever()
CERT

# ============================================================
# 4. IDENTITÉ NUMÉRIQUE DÉCENTRALISÉE ($30 Milliards)
# ============================================================
echo -e "${CYAN}🔐 Module Identité Numérique...${NC}"

cat > $BASE_DIR/identity/server.py << 'IDENTITY'
#!/usr/bin/env python3
"""OSIS ID — Identité Numérique Décentralisée"""
import json, os, sqlite3, hashlib, secrets, time
from http.server import HTTPServer, BaseHTTPRequestHandler

DB = os.path.join(os.path.dirname(__file__), 'identity.db')

class IdentityDB:
    def __init__(self):
        self.c = sqlite3.connect(DB)
        self.c.executescript('''
            CREATE TABLE IF NOT EXISTS identities(id INTEGER PRIMARY KEY, did TEXT UNIQUE, name TEXT, country TEXT, public_key TEXT, verified INTEGER DEFAULT 0, created_at DATETIME DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS credentials(id INTEGER PRIMARY KEY, identity_id INTEGER, type TEXT, issuer TEXT, credential_hash TEXT, issued_at DATETIME DEFAULT CURRENT_TIMESTAMP);
        ''')
        if not self.c.execute("SELECT COUNT(*) FROM identities").fetchone()[0]:
            did = f"did:osis:{secrets.token_hex(16)}"
            self.c.execute("INSERT INTO identities(did,name,country,public_key,verified) VALUES(?,?,?,?,1)", (did, "Amadou Diallo", "Mali", secrets.token_hex(32)))
            self.c.commit()
    
    def create_identity(self, name, country):
        did = f"did:osis:{secrets.token_hex(16)}"
        pubkey = secrets.token_hex(32)
        self.c.execute("INSERT INTO identities(did,name,country,public_key) VALUES(?,?,?,?)", (did, name, country, pubkey))
        self.c.commit()
        return {"did": did, "name": name, "country": country}

db = IdentityDB()

class H(BaseHTTPRequestHandler):
    def _cors(self): self.send_header("Access-Control-Allow-Origin","*"); self.send_header("Access-Control-Allow-Methods","GET,POST,OPTIONS"); self.send_header("Access-Control-Allow-Headers","Content-Type")
    def do_OPTIONS(self): self.send_response(200); self._cors(); self.end_headers()
    def _json(self, d, s=200): self.send_response(s); self._cors(); self.send_header("Content-Type","application/json"); self.end_headers(); self.wfile.write(json.dumps(d).encode())
    def do_GET(self):
        if "/health" in self.path: self._json({"status":"ok","market":"digital-identity","potential":"$30B"})

HTTPServer(("0.0.0.0", 8703), H).serve_forever()
IDENTITY

# ============================================================
# FIN
# ============================================================
for svc in carbon-credits artisan-market certification identity; do
    python3 $BASE_DIR/$svc/server.py &
    echo "✅ $svc démarré"
done

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  🌲 OSIS — Nouveaux Marchés Stratégiques                    ║"
echo "║                                                              ║"
echo "║  🌍 Crédits Carbone  : http://localhost:8700  ($50B)        ║"
echo "║  🛍️ Artisan Market  : http://localhost:8701  ($8B)         ║"
echo "║  🎓 Certifications  : http://localhost:8702  ($3B)         ║"
echo "║  🔐 Identité Num.   : http://localhost:8703  ($30B)        ║"
echo "║                                                              ║"
echo "║  💰 Potentiel Total : $91 Milliards                        ║"
echo "╚══════════════════════════════════════════════════════════════╝"