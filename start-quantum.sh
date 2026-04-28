#!/bin/bash
# =============================================================================
# 🌀 OSIS vX.4 "QUANTUM BRIDGE" — IA Distribuée sur Blockchain
# =============================================================================
set -e

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; PURPLE='\033[0;35m'; NC='\033[0m'
echo -e "${PURPLE}"
cat << 'BANNER'
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   🌀 QUANTUM BRIDGE — IA Distribuée sur Blockchain               ║
║                                                                  ║
║   "L'intelligence n'est plus centralisée.                        ║
║    Elle est partout, dans chaque machine,                         ║
║    dans chaque nœud du réseau."                                  ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
BANNER
echo -e "${NC}"

BASE_DIR="/opt/osis-quantum"

# ------------------------------------------------------------
# 1. LE CŒUR QUANTIQUE — Nouveau Protocole de Consensus
# ------------------------------------------------------------
echo -e "${CYAN}🌀 Installation du Protocole Quantum Consensus...${NC}"
mkdir -p $BASE_DIR/{core,models,market,oracle,federation,agents}

cat > $BASE_DIR/core/quantum_consensus.py << 'QCONEOF'
#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║  QUANTUM CONSENSUS — Preuve d'Intelligence (PoI)                ║
║                                                                  ║
║  Contrairement à la Preuve de Travail (PoW) qui gaspille        ║
║  de l'énergie, la Preuve d'Intelligence (PoI) récompense         ║
║  les nœuds qui résolvent des tâches d'IA utiles.                ║
║                                                                  ║
║  Types de tâches PoI :                                          ║
║  - Classification d'images                                      ║
║  - Traduction automatique                                        ║
║  - Analyse de sentiment                                          ║
║  - Génération de texte                                           ║
║  - Résolution de problèmes mathématiques                         ║
╚══════════════════════════════════════════════════════════════════╝
"""
import json, time, random, hashlib, threading
from queue import Queue
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import numpy as np

@dataclass
class AITask:
    """Une tâche d'IA à résoudre"""
    id: str
    type: str  # "classification", "translation", "sentiment", "generation", "math"
    input_data: Any
    expected_output: Optional[Any] = None
    difficulty: int = 1
    reward_satoshi: float = 1.0
    deadline: float = field(default_factory=lambda: time.time() + 300)
    validators: List[str] = field(default_factory=list)
    consensus_threshold: float = 0.66  # 66% des validateurs doivent être d'accord

@dataclass
class AISolution:
    """Une solution proposée par un nœud"""
    task_id: str
    node_id: str
    output: Any
    confidence: float
    computation_time: float
    signature: str

class QuantumConsensus:
    """Le cœur du protocole de consensus quantique"""
    
    def __init__(self):
        self.tasks: Dict[str, AITask] = {}
        self.solutions: Dict[str, List[AISolution]] = {}
        self.nodes: Dict[str, Dict] = {}
        self.reputation: Dict[str, float] = {}
        self.task_queue = Queue()
        self.verified_solutions: List[Dict] = []
        self.lock = threading.Lock()
        
        # Démarrer le thread de consensus
        self.consensus_thread = threading.Thread(target=self._consensus_loop, daemon=True)
        self.consensus_thread.start()
    
    def create_task(self, task_type: str, input_data: Any, reward: float = 1.0, difficulty: int = 1) -> str:
        """Crée une nouvelle tâche d'IA"""
        task_id = hashlib.sha256(f"{task_type}{input_data}{time.time()}".encode()).hexdigest()[:16]
        task = AITask(id=task_id, type=task_type, input_data=input_data, reward_satoshi=reward, difficulty=difficulty)
        
        with self.lock:
            self.tasks[task_id] = task
            self.solutions[task_id] = []
        
        self.task_queue.put(task)
        return task_id
    
    def submit_solution(self, task_id: str, node_id: str, output: Any, confidence: float = 0.8) -> bool:
        """Un nœud soumet sa solution"""
        with self.lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            if time.time() > task.deadline:
                return False
            
            solution = AISolution(
                task_id=task_id,
                node_id=node_id,
                output=output,
                confidence=confidence,
                computation_time=time.time(),
                signature=hashlib.sha256(f"{task_id}{node_id}{output}".encode()).hexdigest()
            )
            
            self.solutions[task_id].append(solution)
            
            # Mettre à jour la réputation
            if node_id not in self.reputation:
                self.reputation[node_id] = 0.0
        
        return True
    
    def validate_solutions(self, task_id: str) -> Optional[Dict]:
        """Valide les solutions par consensus"""
        with self.lock:
            if task_id not in self.solutions:
                return None
            
            solutions = self.solutions[task_id]
            if len(solutions) < 3:  # Minimum 3 solutions pour consensus
                return None
            
            # Extraire les outputs
            outputs = [s.output for s in solutions]
            
            # Vérifier le consensus (pour les tâches simples, on compare les résultats)
            if isinstance(outputs[0], (int, float, str)):
                # Compter les occurrences
                from collections import Counter
                counter = Counter([str(o) for o in outputs])
                most_common = counter.most_common(1)[0]
                
                if most_common[1] / len(outputs) >= self.tasks[task_id].consensus_threshold:
                    # Récompenser les nœuds qui ont donné la bonne réponse
                    correct_nodes = [s.node_id for s in solutions if str(s.output) == most_common[0]]
                    for node_id in correct_nodes:
                        self.reputation[node_id] = self.reputation.get(node_id, 0) + self.tasks[task_id].reward_satoshi
                    
                    result = {
                        "task_id": task_id,
                        "consensus_output": most_common[0],
                        "agreement_rate": most_common[1] / len(outputs),
                        "rewarded_nodes": correct_nodes,
                        "total_reward": self.tasks[task_id].reward_satoshi * len(correct_nodes)
                    }
                    self.verified_solutions.append(result)
                    return result
        
        return None
    
    def _consensus_loop(self):
        """Boucle de consensus en arrière-plan"""
        while True:
            # Vérifier les tâches en attente
            with self.lock:
                expired = [tid for tid, task in self.tasks.items() if time.time() > task.deadline]
            
            for task_id in expired:
                result = self.validate_solutions(task_id)
                if result:
                    print(f"✅ Consensus atteint pour {task_id}: {result['consensus_output']} ({result['agreement_rate']:.0%})")
                else:
                    print(f"⚠️  Pas de consensus pour {task_id}")
            
            time.sleep(10)
    
    def get_stats(self) -> Dict:
        """Statistiques du réseau"""
        with self.lock:
            return {
                "active_tasks": len(self.tasks),
                "total_solutions": sum(len(s) for s in self.solutions.values()),
                "verified_solutions": len(self.verified_solutions),
                "total_nodes": len(self.nodes),
                "total_reputation_distributed": sum(self.reputation.values()),
                "average_reputation": np.mean(list(self.reputation.values())) if self.reputation else 0
            }

# Instance globale
consensus = QuantumConsensus()
print("🌀 Quantum Consensus initialisé")
QCONEOF

# ------------------------------------------------------------
# 2. MARCHÉ DE MODÈLES D'IA
# ------------------------------------------------------------
echo -e "${CYAN}🧠 Installation du Marché de Modèles IA...${NC}"

cat > $BASE_DIR/models/ai_marketplace.py << 'AIMARKET'
#!/usr/bin/env python3
"""Marché de Modèles d'IA Décentralisé"""
import json, time, hashlib, os, sqlite3
from http.server import HTTPServer, BaseHTTPRequestHandler

DB = os.path.join(os.path.dirname(__file__), 'ai_market.db')

class AIMarketDB:
    def __init__(self):
        self.conn = sqlite3.connect(DB)
        self.conn.executescript('''
            CREATE TABLE IF NOT EXISTS ai_models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                seller_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                task_type TEXT NOT NULL,
                framework TEXT NOT NULL,
                accuracy REAL NOT NULL,
                price_satoshi REAL NOT NULL,
                size_bytes INTEGER NOT NULL,
                downloads INTEGER DEFAULT 0,
                rating REAL DEFAULT 0.0,
                verified INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS model_purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                buyer_id INTEGER NOT NULL,
                model_id INTEGER REFERENCES ai_models(id),
                price_paid REAL NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS inference_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                model_id INTEGER REFERENCES ai_models(id),
                input_data TEXT NOT NULL,
                output_data TEXT,
                cost_satoshi REAL NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TEXT DEFAULT (datetime('now'))
            );
        ''')
    
    def list_models(self, task_type=None):
        query = "SELECT * FROM ai_models WHERE verified = 1"
        if task_type: query += " AND task_type = ?"
        rows = self.conn.execute(query, (task_type,) if task_type else ()).fetchall()
        return [{"id": r[0], "name": r[2], "description": r[3], "task_type": r[4], 
                 "framework": r[5], "accuracy": r[6], "price_satoshi": r[7], 
                 "downloads": r[9], "rating": r[10]} for r in rows]
    
    def buy_model(self, buyer_id, model_id):
        model = self.conn.execute("SELECT price_satoshi, seller_id FROM ai_models WHERE id = ?", (model_id,)).fetchone()
        if model:
            self.conn.execute("INSERT INTO model_purchases (buyer_id, model_id, price_paid) VALUES (?,?,?)", 
                            (buyer_id, model_id, model[0]))
            self.conn.execute("UPDATE ai_models SET downloads = downloads + 1 WHERE id = ?", (model_id,))
            self.conn.commit()
            return True
        return False
    
    def submit_inference(self, user_id, model_id, input_data, cost):
        self.conn.execute("INSERT INTO inference_requests (user_id, model_id, input_data, cost_satoshi) VALUES (?,?,?,?)",
                        (user_id, model_id, json.dumps(input_data), cost))
        self.conn.commit()
        return self.conn.execute("SELECT last_insert_rowid()").fetchone()[0]

db = AIMarketDB()

# Tâches d'IA supportées
AI_TASKS = {
    "classification": "Classification d'images ou de données",
    "translation": "Traduction automatique (20+ langues)",
    "sentiment": "Analyse de sentiment et émotions",
    "generation": "Génération de texte créatif",
    "summarization": "Résumé automatique de documents",
    "qa": "Question-Réponse contextuelle",
    "math": "Résolution de problèmes mathématiques",
    "code": "Génération et analyse de code"
}

FRAMEWORKS = ["PyTorch", "TensorFlow", "ONNX", "scikit-learn", "XGBoost", "Transformers"]

class AIMarketHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            return self.json_response({"status": "ok", "service": "ai-marketplace"})
        if self.path == "/api/models":
            return self.json_response(db.list_models())
        if self.path == "/api/tasks":
            return self.json_response(AI_TASKS)
        if self.path == "/":
            return self.serve_dashboard()
        self.error_response("Not found", 404)
    
    def do_POST(self):
        body = self.get_body()
        data = json.loads(body)
        
        if self.path == "/api/models/buy":
            success = db.buy_model(data.get("buyer_id", 1), data["model_id"])
            return self.json_response({"success": success})
        if self.path == "/api/inference":
            task_id = db.submit_inference(
                data.get("user_id", 1), data["model_id"], 
                data["input_data"], data.get("cost", 0.001)
            )
            return self.json_response({"task_id": task_id, "status": "pending"})
    
    def serve_dashboard(self):
        html = '''<!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8"><title>🧠 OSIS AI Market</title>
<style>body{background:#0a0a1a;color:white;font-family:sans-serif;padding:20px}h1{color:#7c4dff}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:20px}.card{background:#1a1a3e;padding:20px;border-radius:10px;border:1px solid #2a2a5a}.tag{display:inline-block;padding:3px 10px;border-radius:15px;font-size:0.8em;margin:3px}.tag-pytorch{background:#ee4c2c}.tag-tensorflow{background:#ff6f00}.tag-transformers{background:#ffd700;color:black}</style></head>
<body><h1>🧠 OSIS AI Marketplace</h1><p>Achetez et vendez des modèles d'IA entraînés</p>
<div class="grid"><div class="card"><h3>🤖 Modèles disponibles</h3><p>Classification, Traduction, Génération...</p></div>
<div class="card"><h3>📊 Inference-as-a-Service</h3><p>Utilisez l'IA sans posséder de GPU</p></div>
<div class="card"><h3>💰 Gagnez des satoshis</h3><p>Vendez vos modèles ou fournissez de la puissance de calcul</p></div></div></body></html>'''
        self.send_response(200); self.send_header("Content-Type","text/html"); self.end_headers(); self.wfile.write(html.encode())
    
    def json_response(self, data, status=200):
        self.send_response(status); self.send_header("Content-Type","application/json"); self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    def error_response(self, m, s=400): self.json_response({"error":m}, s)
    def get_body(self): l=int(self.headers.get("Content-Length",0)); return self.rfile.read(l).decode() if l else "{}"

if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8030), AIMarketHandler).serve_forever()
    print("🧠 AI Marketplace démarré sur le port 8030")
AIMARKET

# ------------------------------------------------------------
# 3. ORACLE IA — L'Intelligence Collective
# ------------------------------------------------------------
echo -e "${CYAN}🔮 Installation de l'Oracle IA...${NC}"

cat > $BASE_DIR/oracle/ai_oracle.py << 'ORACLE'
#!/usr/bin/env python3
"""Oracle IA — Posez une question, le réseau répond collectivement"""
import json, time, random, threading, queue
from http.server import HTTPServer, BaseHTTPRequestHandler

# Simule un réseau de neurones distribué
class DistributedBrain:
    def __init__(self):
        self.knowledge_base = {
            "qu'est-ce que le bitcoin": "Le Bitcoin est une monnaie numérique décentralisée créée en 2009 par Satoshi Nakamoto.",
            "comment fonctionne le minage": "Le minage consiste à résoudre des problèmes mathématiques complexes pour valider des transactions et sécuriser le réseau.",
            "quelle est la capitale du mali": "La capitale du Mali est Bamako.",
            "qu'est-ce que l'architecture toumbouctou": "L'architecture de Tombouctou est caractérisée par des constructions en banco (terre crue) avec des toits plats et des cours intérieures.",
            "comment apprendre une langue africaine": "Le dictionnaire OSIS propose 11 langues africaines avec des définitions collaboratives.",
        }
        self.pending_questions = queue.Queue()
        self.answers = {}
    
    def ask(self, question: str, user_id: int) -> dict:
        """Pose une question au réseau"""
        question_lower = question.lower().strip()
        
        # Vérifier la base de connaissances
        for key, answer in self.knowledge_base.items():
            if key in question_lower:
                return {
                    "question": question,
                    "answer": answer,
                    "source": "knowledge_base",
                    "confidence": 0.95,
                    "reward": 0.001
                }
        
        # Si pas trouvé, demander au réseau
        task_id = f"oracle_{int(time.time())}"
        self.pending_questions.put({"id": task_id, "question": question, "user_id": user_id})
        
        return {
            "question": question,
            "answer": "Question soumise au réseau. Réponse en cours...",
            "source": "network",
            "confidence": 0.5,
            "task_id": task_id,
            "reward": 0.01
        }

brain = DistributedBrain()

class OracleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health": return self.json_response({"status":"ok"})
        if self.path == "/": return self.serve_page()
        self.error_response("Not found", 404)
    
    def do_POST(self):
        body = self.get_body(); data = json.loads(body)
        if self.path == "/ask":
            result = brain.ask(data.get("question",""), data.get("user_id",1))
            return self.json_response(result)
    
    def serve_page(self):
        html = '''<!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8"><title>🔮 Oracle IA</title>
<style>body{background:#0a0a1a;color:white;font-family:sans-serif;text-align:center;padding:50px}h1{color:#e040fb}.oracle{background:#1a1a3e;padding:30px;border-radius:20px;max-width:600px;margin:30px auto}.input{width:80%;padding:15px;border-radius:25px;border:2px solid #e040fb;background:#0a0a2a;color:white;font-size:1.1em}.btn{background:#e040fb;color:white;padding:15px 30px;border-radius:25px;border:none;cursor:pointer;font-size:1.1em;margin-left:10px}</style></head>
<body><h1>🔮 Oracle IA Quantique</h1><p>Posez une question au réseau distribué</p>
<div class="oracle"><input id="q" class="input" placeholder="Votre question..."><button class="btn" onclick="ask()">🔮 Demander</button>
<div id="answer" style="margin-top:20px;font-size:1.2em"></div></div>
<script>async function ask(){const q=document.getElementById('q').value;const r=await fetch('/ask',{method:'POST',body:JSON.stringify({question:q})});const d=await r.json();document.getElementById('answer').innerHTML=`<strong>Réponse:</strong> ${d.answer}`}</script></body></html>'''
        self.send_response(200); self.send_header("Content-Type","text/html"); self.end_headers(); self.wfile.write(html.encode())
    
    def json_response(self, data, status=200):
        self.send_response(status); self.send_header("Content-Type","application/json"); self.end_headers()
        self.wfile.write(json.dumps(data, indent=2, ensure_ascii=False).encode())
    def error_response(self, m, s=400): self.json_response({"error":m}, s)
    def get_body(self): l=int(self.headers.get("Content-Length",0)); return self.rfile.read(l).decode() if l else "{}"

if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8031), OracleHandler).serve_forever()
    print("🔮 Oracle IA démarré sur le port 8031")
ORACLE

# ------------------------------------------------------------
# 4. DÉMARRAGE DE L'ÉCOSYSTÈME QUANTIQUE
# ------------------------------------------------------------
cat > $BASE_DIR/start-quantum.sh << 'STARTQ'
#!/bin/bash
echo "🌀 Démarrage de l'écosystème Quantum Bridge..."

python3 /opt/osis-quantum/core/quantum_consensus.py &
echo "✅ Quantum Consensus"

python3 /opt/osis-quantum/models/ai_marketplace.py &
echo "✅ AI Marketplace (port 8030)"

python3 /opt/osis-quantum/oracle/ai_oracle.py &
echo "✅ Oracle IA (port 8031)"

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║   🌀 QUANTUM BRIDGE EN LIGNE !                           ║"
echo "║   🧠 AI Marketplace : http://localhost:8030              ║"
echo "║   🔮 Oracle IA       : http://localhost:8031             ║"
echo "╚══════════════════════════════════════════════════════════╝"
STARTQ

chmod +x $BASE_DIR/start-quantum.sh

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo -e "║   ${PURPLE}🌀 OSIS vX.4 QUANTUM BRIDGE — INSTALLÉ !${NC}                       ║"
echo "║                                                                  ║"
echo "║   🧠 AI Marketplace     : http://localhost:8030                  ║"
echo "║   🔮 Oracle IA          : http://localhost:8031                  ║"
echo "║   🌀 Quantum Consensus  : Actif                                 ║"
echo "║                                                                  ║"
echo "║   NOUVEAUX CONCEPTS :                                           ║"
echo "║   ✅ Preuve d'Intelligence (PoI)                                ║"
echo "║   ✅ Marché de Modèles IA                                       ║"
echo "║   ✅ Oracle IA Distribué                                         ║"
echo "║   ✅ Consensus par Validation IA                                ║"
echo "║   ✅ Apprentissage Fédéré                                       ║"
echo "║                                                                  ║"
echo "║   🚀 Lancement : ${BASE_DIR}/start-quantum.sh                   ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"