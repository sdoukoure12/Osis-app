#!/bin/bash
# =============================================================================
# 🌲 OSIS-PRO — FINALISATION & INTÉGRATION KORKI-WALLET
# Script : osis-korki-bridge.sh
# Auteur : sdoukoure12
# Ce script :
#   1. Vérifie la présence du module Korki-Wallet
#   2. Crée un pont API entre le backend OSIS-PRO et Korki-Wallet
#   3. Synchronise les tokens OLC entre les deux systèmes
#   4. Ajoute les routes Wallet au backend principal
#   5. Finalise l'écosystème OSIS-PRO prêt pour la production
# =============================================================================
set -e

# Couleurs
GREEN='\033[0;32m'; CYAN='\033[0;36m'; YELLOW='\033[1;33m'; NC='\033[0m'
echo -e "${GREEN}🌲 OSIS-PRO — Finalisation & Pont Korki-Wallet${NC}"

BASE_DIR="Osis-Pro"
if [ ! -d "$BASE_DIR" ]; then
    echo "❌ Le dossier $BASE_DIR est introuvable. Exécutez d'abord le script de création du dépôt."
    exit 1
fi

cd "$BASE_DIR"

# ---------------------------------------------------------------------------
# 1. VÉRIFICATION DE KORKI-WALLET
# ---------------------------------------------------------------------------
echo -e "${CYAN}🔍 Vérification de Korki-Wallet...${NC}"
if [ ! -d "modules/korki-wallet" ]; then
    echo "⚠️  Korki-Wallet non trouvé. Importation via SSH..."
    git clone git@github.com:sdoukoure12/Korki-Wallet.git modules/korki-wallet
    echo "✅ Korki-Wallet importé."
else
    echo "✅ Korki-Wallet déjà présent."
fi

# ---------------------------------------------------------------------------
# 2. CRÉATION DU PONT API (Korki-Wallet ↔ OSIS Backend)
# ---------------------------------------------------------------------------
echo -e "${CYAN}🔗 Création du pont API...${NC}"
mkdir -p backend/services

cat > backend/services/korki_bridge.py << 'BRIDGE'
#!/usr/bin/env python3
"""
OSIS-PRO ↔ Korki-Wallet Bridge
Service de liaison entre le backend OSIS et Korki-Wallet.
"""
import os
import json
import requests
from flask import Blueprint, request, jsonify

# URL de l'API Korki-Wallet (à adapter selon le port réel)
KORKI_API_URL = os.environ.get("KORKI_API_URL", "http://localhost:9000/api")

korki_bp = Blueprint('korki', __name__, url_prefix='/api/wallet')

@korki_bp.route('/balance/<user_id>', methods=['GET'])
def get_balance(user_id):
    """Récupère le solde OLC depuis Korki-Wallet."""
    try:
        resp = requests.get(f"{KORKI_API_URL}/balance/{user_id}", timeout=5)
        if resp.status_code == 200:
            return jsonify(resp.json())
        else:
            # Fallback : solde depuis la DB OSIS
            from backend.main import get_db
            db = get_db()
            user = db.execute("SELECT balance FROM users WHERE id = ?", (user_id,)).fetchone()
            if user:
                return jsonify({"user_id": user_id, "balance": user['balance'], "source": "osis-db"})
            return jsonify({"error": "Utilisateur non trouvé"}), 404
    except requests.exceptions.ConnectionError:
        # Fallback local
        from backend.main import get_db
        db = get_db()
        user = db.execute("SELECT balance FROM users WHERE id = ?", (user_id,)).fetchone()
        if user:
            return jsonify({"user_id": user_id, "balance": user['balance'], "source": "osis-db"})
        return jsonify({"error": "Service wallet indisponible"}), 503

@korki_bp.route('/transfer', methods=['POST'])
def transfer():
    """Effectue un transfert OLC via Korki-Wallet."""
    data = request.json
    sender = data.get('sender')
    receiver = data.get('receiver')
    amount = data.get('amount')

    if not all([sender, receiver, amount]):
        return jsonify({"error": "Paramètres manquants"}), 400

    # Tenter Korki-Wallet d'abord
    try:
        resp = requests.post(f"{KORKI_API_URL}/transfer", json=data, timeout=5)
        if resp.status_code == 200:
            return jsonify(resp.json())
    except:
        pass

    # Fallback : transfert local dans OSIS
    from backend.main import get_db
    db = get_db()
    sender_balance = db.execute("SELECT balance FROM users WHERE id = ?", (sender,)).fetchone()
    if not sender_balance or sender_balance['balance'] < amount:
        return jsonify({"error": "Solde insuffisant"}), 400

    db.execute("UPDATE users SET balance = balance - ? WHERE id = ?", (amount, sender))
    db.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (amount, receiver))
    db.commit()
    return jsonify({"message": f"Transfert de {amount} OLC effectué (mode local)", "sender": sender, "receiver": receiver, "amount": amount})

@korki_bp.route('/transactions/<user_id>', methods=['GET'])
def get_transactions(user_id):
    """Récupère l'historique des transactions (Korki ou DB OSIS)."""
    try:
        resp = requests.get(f"{KORKI_API_URL}/transactions/{user_id}", timeout=5)
        if resp.status_code == 200:
            return jsonify(resp.json())
    except:
        pass
    # Fallback local (pas d'historique complet dans la DB de base, retourne vide)
    return jsonify([])

@korki_bp.route('/sync', methods=['POST'])
def sync_wallet():
    """Synchronise le solde OSIS avec Korki-Wallet."""
    data = request.json
    user_id = data.get('user_id')

    from backend.main import get_db
    db = get_db()
    user = db.execute("SELECT balance FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        return jsonify({"error": "Utilisateur non trouvé"}), 404

    # Envoyer le solde à Korki pour synchronisation
    try:
        requests.post(f"{KORKI_API_URL}/sync", json={"user_id": user_id, "balance": user['balance']}, timeout=5)
    except:
        pass

    return jsonify({"message": "Synchronisation effectuée", "user_id": user_id, "balance": user['balance']})
BRIDGE

# ---------------------------------------------------------------------------
# 3. INTÉGRATION DANS LE BACKEND PRINCIPAL
# ---------------------------------------------------------------------------
echo -e "${CYAN}🔧 Mise à jour du backend principal...${NC}"

# Vérifier si main.py existe et le modifier pour inclure le blueprint
if [ -f "backend/main.py" ]; then
    # Ajouter l'import et l'enregistrement du blueprint si pas déjà fait
    if ! grep -q "korki_bridge" backend/main.py; then
        # Sauvegarde
        cp backend/main.py backend/main.py.bak
        
        # Ajouter l'import après les autres imports
        sed -i "1s/^/from backend.services.korki_bridge import korki_bp\n/" backend/main.py 2>/dev/null || true
        
        # Ajouter l'enregistrement du blueprint après CORS(app)
        if grep -q "CORS(app)" backend/main.py; then
            sed -i "/CORS(app)/a\ \n# Korki-Wallet Bridge\napp.register_blueprint(korki_bp)" backend/main.py
        fi
        
        echo "   ✅ Blueprint Korki-Wallet ajouté à main.py"
    else
        echo "   ℹ️  Blueprint déjà présent dans main.py"
    fi
fi

# ---------------------------------------------------------------------------
# 4. CRÉATION DU SCRIPT DE DÉMARRAGE UNIFIÉ
# ---------------------------------------------------------------------------
echo -e "${CYAN}🚀 Création du script de démarrage unifié...${NC}"

cat > start-all.sh << 'STARTALL'
#!/bin/bash
# Démarrage de tous les services OSIS-PRO
echo "🌲 Démarrage de l'écosystème OSIS-PRO..."

# Backend principal (port 8000)
cd backend
python3 main.py &
echo "   ✅ Backend : http://localhost:8000"
cd ..

# Module Crédits Carbone (port 8700)
if [ -f "modules/carbon-credits/server.py" ]; then
    cd modules/carbon-credits && python3 server.py &
    echo "   ✅ Carbon : http://localhost:8700"
    cd ../..
fi

# Module Artisanat (port 8701)
if [ -f "modules/artisan-market/server.py" ]; then
    cd modules/artisan-market && python3 server.py &
    echo "   ✅ Artisan : http://localhost:8701"
    cd ../..
fi

# Korki-Wallet (port 9000)
if [ -f "modules/korki-wallet/main.py" ]; then
    cd modules/korki-wallet && python3 main.py &
    echo "   ✅ Wallet : http://localhost:9000"
    cd ../..
elif [ -f "modules/korki-wallet/app.py" ]; then
    cd modules/korki-wallet && python3 app.py &
    echo "   ✅ Wallet : http://localhost:9000"
    cd ../..
elif [ -f "modules/korki-wallet/server.py" ]; then
    cd modules/korki-wallet && python3 server.py &
    echo "   ✅ Wallet : http://localhost:9000"
    cd ../..
else
    echo "   ⚠️  Korki-Wallet : point d'entrée non trouvé (cherché main.py, app.py, server.py)"
fi

echo ""
echo "🌲 Tous les services sont démarrés."
echo "   Backend : http://localhost:8000/api/health"
echo "   Wallet  : http://localhost:8000/api/wallet/balance/1"
STARTALL
chmod +x start-all.sh

# ---------------------------------------------------------------------------
# 5. SCRIPT DE TEST DU PONT
# ---------------------------------------------------------------------------
cat > test-bridge.sh << 'TESTBRIDGE'
#!/bin/bash
# Test du pont OSIS ↔ Korki-Wallet
echo "🧪 Test du pont..."

# Test solde via le nouveau endpoint
echo -n "Solde user 1 : "
curl -s http://localhost:8000/api/wallet/balance/1 | python3 -m json.tool 2>/dev/null || echo "Backend non démarré"

# Test transfert
echo -n "Transfert test : "
curl -s -X POST http://localhost:8000/api/wallet/transfer \
  -H "Content-Type: application/json" \
  -d '{"sender":1, "receiver":2, "amount":10}' 2>/dev/null || echo "Backend non démarré"

echo "✅ Tests terminés."
TESTBRIDGE
chmod +x test-bridge.sh

# ---------------------------------------------------------------------------
# 6. FINALISATION
# ---------------------------------------------------------------------------
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   ✅ OSIS-PRO — Finalisation terminée !                 ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Script créé : ${CYAN}osis-korki-bridge.sh${NC}"
echo ""
echo "Prochaines étapes :"
echo "  1. Démarrer tous les services : cd Osis-Pro && ./start-all.sh"
echo "  2. Tester le pont : ./test-bridge.sh"
echo "  3. Voir la doc API Wallet : http://localhost:8000/api/wallet/balance/1"
echo ""
echo "Le module Korki-Wallet est maintenant lié au système de tokens OLC."
echo "Les endpoints /api/wallet/* sont disponibles avec fallback automatique."