#!/bin/bash

set -e

echo "🧹 Nettoyage des anciennes installations Node.js..."
sudo apt remove --purge nodejs npm -y 2>/dev/null || true
sudo apt autoremove -y

echo "📦 Ajout du dépôt NodeSource pour Node.js 20 LTS..."
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -

echo "⚙️ Installation de Node.js (inclut npm)..."
sudo apt install -y nodejs

echo "✅ Versions :"
node --version
npm --version

echo "📁 Création du projet SeekMiner..."
mkdir -p ~/SeekMiner/config ~/SeekMiner/public ~/SeekMiner/scripts
cd ~/SeekMiner

npm init -y
npm install express axios

# ---------- Fichier de configuration API ----------
cat > config/api.json << 'EOF'
{
  "braiins": {
    "token": "yrrX89hgXrCeWOEF",
    "username": "Mint-pr@sd999"
  },
  "viabtc": {
    "accessKey": "6bf3666dd537e10093d3533c891836db",
    "secretKey": "ssd39910101.001",
    "username": "Dashboard-Pr@sd999"
  }
}
EOF

# ---------- Serveur principal (server.js) ----------
cat > server.js << 'EOF'
const express = require('express');
const axios = require('axios');
const fs = require('fs');

const app = express();
const PORT = 3000;

// Chargement des clés API
const apiConfig = JSON.parse(fs.readFileSync('./config/api.json'));

app.use(express.static('public'));

// Endpoint Braiins
app.get('/api/braiins/overview', async (req, res) => {
    try {
        const response = await axios.get('https://pool.braiins.com/user/overview', {
            headers: { 'Authorization': `Bearer ${apiConfig.braiins.token}` }
        });
        res.json(response.data);
    } catch (err) {
        console.error('Braiins error:', err.message);
        res.status(500).json({ error: 'Braiins API error' });
    }
});

// Endpoint ViaBTC (authentification Basic)
const viaAuth = Buffer.from(`${apiConfig.viabtc.accessKey}:${apiConfig.viabtc.secretKey}`).toString('base64');

app.get('/api/viabtc/overview', async (req, res) => {
    try {
        const response = await axios.get(
            `https://api.viabtc.com/v1/miner/${apiConfig.viabtc.username}/overview`,
            { headers: { 'Authorization': `Basic ${viaAuth}` } }
        );
        res.json(response.data);
    } catch (err) {
        console.error('ViaBTC error:', err.message);
        res.status(500).json({ error: 'ViaBTC API error' });
    }
});

app.listen(PORT, () => {
    console.log(`✅ SeekMiner actif sur http://localhost:${PORT}`);
    console.log(`📊 Dashboard : http://localhost:${PORT}/dashboard.html`);
});
EOF

# ---------- Dashboard HTML (dashboard.html) ----------
cat > public/dashboard.html << 'EOF'
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SeekMiner – Multi‑Pool Dashboard</title>
    <style>
        * { box-sizing: border-box; }
        body {
            background: #0f172a;
            color: #f8fafc;
            font-family: monospace;
            padding: 1.5rem;
        }
        .tabs {
            display: flex;
            gap: 0.5rem;
            margin-bottom: 1.5rem;
            border-bottom: 1px solid #334155;
            padding-bottom: 0.5rem;
        }
        .tab {
            background: #1e293b;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            cursor: pointer;
        }
        .tab.active {
            background: #3b82f6;
        }
        .stats {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
            margin-bottom: 2rem;
        }
        .card {
            background: #1e293b;
            padding: 1rem;
            border-radius: 12px;
            flex: 1;
            min-width: 180px;
            border-left: 3px solid #facc15;
        }
        .value {
            font-size: 1.5rem;
            font-weight: bold;
            color: #facc15;
        }
        table {
            width: 100%;
            background: #1e293b;
            border-radius: 12px;
            border-collapse: collapse;
        }
        th, td {
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid #334155;
        }
        .active { color: #4ade80; }
        .inactive { color: #f87171; }
        .error { color: #f87171; padding: 2rem; text-align: center; }
        .refresh-note { margin-top: 1rem; font-size: 0.8rem; color: #64748b; text-align: right; }
    </style>
</head>
<body>
    <h1>⚡ SeekMiner – Multi‑Pool Dashboard</h1>
    <div class="tabs">
        <div class="tab active" data-pool="braiins">⛏️ Braiins</div>
        <div class="tab" data-pool="viabtc">🟠 ViaBTC</div>
    </div>
    <div id="dashboard">Chargement...</div>
    <div class="refresh-note">🔄 Rafraîchissement automatique toutes les 30s</div>

    <script>
        let currentPool = 'braiins';

        async function fetchBraiins() {
            const response = await fetch('/api/braiins/overview');
            if (!response.ok) throw new Error('Braiins API error');
            const data = await response.json();
            return { overview: data, workers: [] }; // Braiins workers non implémentés ici
        }

        async function fetchViaBTC() {
            const response = await fetch('/api/viabtc/overview');
            if (!response.ok) throw new Error('ViaBTC API error');
            const data = await response.json();
            return { overview: data, workers: [] };
        }

        async function loadDashboard() {
            const container = document.getElementById('dashboard');
            container.innerHTML = '<div class="card">⏳ Chargement...</div>';
            try {
                let data;
                if (currentPool === 'braiins') data = await fetchBraiins();
                else data = await fetchViaBTC();

                const ov = data.overview;
                const confirmed = ov.confirmed_reward ?? '—';
                const unconfirmed = ov.unconfirmed_reward ?? '—';
                const threshold = ov.send_threshold ?? (currentPool === 'braiins' ? '0.0005 BTC' : '—');

                container.innerHTML = `
                    <div class="stats">
                        <div class="card"><h3>💰 Récompense confirmée</h3><div class="value">${confirmed} BTC</div></div>
                        <div class="card"><h3>⏳ Récompense non confirmée</h3><div class="value">${unconfirmed} BTC</div></div>
                        <div class="card"><h3>🎯 Seuil paiement</h3><div class="value">${threshold}</div></div>
                    </div>
                    <p><em>Workers : affichage à venir (API spécifique)</em></p>
                `;
            } catch (err) {
                container.innerHTML = `<div class="error">❌ Erreur : ${err.message}</div>`;
            }
        }

        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', () => {
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                currentPool = tab.dataset.pool;
                loadDashboard();
            });
        });

        loadDashboard();
        setInterval(loadDashboard, 30000);
    </script>
</body>
</html>
EOF

echo ""
echo "🎉 Installation terminée avec succès !"
echo "👉 Pour lancer SeekMiner :"
echo "    cd ~/SeekMiner && node server.js"
echo "🌐 Ouvrir le navigateur : http://localhost:3000/dashboard.html"
