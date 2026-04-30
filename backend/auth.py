#!/usr/bin/env python3
"""
OSIS-PRO — Module d'authentification complet et sécurisé
Fonctionnalités :
- Hachage fort (PBKDF2 avec sel)
- Validation robuste des mots de passe
- Protection anti force-brute (rate limiting par IP et utilisateur)
- Tokens JWT avec access token (courte durée) et refresh token (longue durée)
- Double authentification (TOTP) – activable par l'utilisateur
- Validation d'email (envoi de code de vérification)
- OAuth2 (Google, GitHub) – intégration simplifiée
- Liste noire de tokens révoqués
"""

import os
import re
import time
import hashlib
import secrets
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, g

# ---------------------------------------------------------------------------
# Configuration (à externaliser dans des variables d'environnement)
# ---------------------------------------------------------------------------
SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_hex(32))
PASSWORD_SALT = os.environ.get('PASSWORD_SALT', secrets.token_hex(16))
ACCESS_TOKEN_EXPIRE_MINUTES = 60          # 1 heure
REFRESH_TOKEN_EXPIRE_DAYS = 7
MAX_LOGIN_ATTEMPTS = 5
BLOCK_DURATION_MINUTES = 15
TOTP_ISSUER = "OSIS-PRO"

# ---------------------------------------------------------------------------
# Stockage simulé (en production, utiliser Redis ou une table DB)
# ---------------------------------------------------------------------------
failed_logins = {}          # {ip ou username: (tentatives, timestamp)}
revoked_tokens = set()      # ensemble de tokens révoqués
totp_secrets = {}           # {user_id: secret_totp}
email_verification_codes = {}  # {user_id: {"code": code, "expires": timestamp}}

# ---------------------------------------------------------------------------
# Utilitaires de sécurité
# ---------------------------------------------------------------------------
def hash_password(password: str) -> str:
    """Hachage fort avec PBKDF2 + sel"""
    return hashlib.pbkdf2_hmac(
        'sha256',
        password.encode(),
        PASSWORD_SALT.encode(),
        100000
    ).hex()

def validate_password_strength(password: str) -> tuple:
    """Retourne (True, "") si le mot de passe est assez fort."""
    if len(password) < 8:
        return False, "Minimum 8 caractères"
    if not re.search(r'[A-Z]', password):
        return False, "Au moins une majuscule"
    if not re.search(r'[a-z]', password):
        return False, "Au moins une minuscule"
    if not re.search(r'[0-9]', password):
        return False, "Au moins un chiffre"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Au moins un caractère spécial"
    return True, ""

def is_rate_limited(identifier: str) -> bool:
    if identifier in failed_logins:
        attempts, ts = failed_logins[identifier]
        if attempts >= MAX_LOGIN_ATTEMPTS:
            if time.time() - ts < BLOCK_DURATION_MINUTES * 60:
                return True
            else:
                del failed_logins[identifier]
    return False

def record_failed_attempt(identifier: str):
    if identifier in failed_logins:
        attempts, _ = failed_logins[identifier]
        failed_logins[identifier] = (attempts + 1, time.time())
    else:
        failed_logins[identifier] = (1, time.time())

# ---------------------------------------------------------------------------
# Gestion des tokens JWT
# ---------------------------------------------------------------------------
def create_access_token(user_id: int) -> str:
    payload = {
        'user_id': user_id,
        'type': 'access',
        'exp': datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def create_refresh_token(user_id: int) -> str:
    payload = {
        'user_id': user_id,
        'type': 'refresh',
        'exp': datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token: str, token_type: str = 'access') -> dict:
    if token in revoked_tokens:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        if payload.get('type') != token_type:
            return None
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def revoke_token(token: str):
    revoked_tokens.add(token)

# ---------------------------------------------------------------------------
# TOTP (Double authentification)
# ---------------------------------------------------------------------------
import pyotp  # pip install pyotp

def generate_totp_secret() -> str:
    return pyotp.random_base32()

def get_totp_uri(secret: str, username: str) -> str:
    return pyotp.totp.TOTP(secret).provisioning_uri(
        name=username,
        issuer_name=TOTP_ISSUER
    )

def verify_totp(secret: str, code: str) -> bool:
    totp = pyotp.TOTP(secret)
    return totp.verify(code)

# ---------------------------------------------------------------------------
# Validation d'email (simulation d'envoi)
# ---------------------------------------------------------------------------
def send_verification_email(email: str, code: str):
    # En production, intégrer un service SMTP ou une API d'envoi
    print(f"📧 Code de vérification envoyé à {email} : {code}")

def generate_email_code() -> str:
    return str(secrets.randbelow(1000000)).zfill(6)

# ---------------------------------------------------------------------------
# Middleware d'authentification
# ---------------------------------------------------------------------------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Token manquant'}), 401
        payload = verify_token(token, 'access')
        if not payload:
            return jsonify({'error': 'Token invalide ou expiré'}), 401
        
        # Si 2FA activée, vérifier que le token a été émis après validation TOTP
        # (On pourrait stocker 'totp_verified': True dans le payload)
        g.user_id = payload['user_id']
        return f(*args, **kwargs)
    return decorated

# ---------------------------------------------------------------------------
# Routes d'authentification
# ---------------------------------------------------------------------------
def register_routes(app):
    from backend.main import get_db

    @app.route('/api/auth/register', methods=['POST'])
    def register():
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '')
        email = data.get('email', '').strip()

        if not username or len(username) < 3:
            return jsonify({'error': 'Nom d\'utilisateur trop court (min 3 caractères)'}), 400
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return jsonify({'error': 'Caractères invalides dans le nom d\'utilisateur'}), 400

        valid, msg = validate_password_strength(password)
        if not valid:
            return jsonify({'error': msg}), 400

        db = get_db()
        try:
            db.execute(
                "INSERT INTO users (username, password_hash, email, balance, email_verified) VALUES (?, ?, ?, 10000, 0)",
                (username, hash_password(password), email)
            )
            db.commit()
            user_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]

            # Envoi du code de vérification d'email
            code = generate_email_code()
            email_verification_codes[user_id] = {
                "code": code,
                "expires": time.time() + 3600  # 1 heure
            }
            send_verification_email(email, code)

            access_token = create_access_token(user_id)
            refresh_token = create_refresh_token(user_id)

            return jsonify({
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user_id': user_id,
                'message': 'Compte créé avec 10 000 OLC ! Vérifiez votre email.'
            }), 201
        except Exception as e:
            return jsonify({'error': 'Utilisateur déjà existant'}), 409

    @app.route('/api/auth/login', methods=['POST'])
    def login():
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '')
        totp_code = data.get('totp_code', '')  # Optionnel

        ip = request.remote_addr
        if is_rate_limited(ip) or is_rate_limited(username):
            return jsonify({'error': 'Trop de tentatives. Réessayez dans 15 minutes.'}), 429

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username = ? AND password_hash = ?",
            (username, hash_password(password))
        ).fetchone()

        if not user:
            record_failed_attempt(ip)
            record_failed_attempt(username)
            return jsonify({'error': 'Identifiants invalides'}), 401

        # Réinitialiser les tentatives
        failed_logins.pop(ip, None)
        failed_logins.pop(username, None)

        # Vérification 2FA si activée
        totp_enabled = user['totp_enabled']
        if totp_enabled:
            if not totp_code:
                return jsonify({'error': 'Code TOTP requis', 'totp_required': True}), 401
            secret = totp_secrets.get(user['id'])
            if not secret or not verify_totp(secret, totp_code):
                return jsonify({'error': 'Code TOTP invalide'}), 401

        access_token = create_access_token(user['id'])
        refresh_token = create_refresh_token(user['id'])

        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user_id': user['id'],
            'username': user['username'],
            'balance': user['balance'],
            'level': user['level'],
            'totp_required': bool(totp_enabled)
        })

    @app.route('/api/auth/refresh', methods=['POST'])
    def refresh():
        data = request.json
        refresh_token = data.get('refresh_token', '')
        payload = verify_token(refresh_token, 'refresh')
        if not payload:
            return jsonify({'error': 'Refresh token invalide ou expiré'}), 401
        
        access_token = create_access_token(payload['user_id'])
        return jsonify({'access_token': access_token})

    @app.route('/api/auth/logout', methods=['POST'])
    @login_required
    def logout():
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        revoke_token(token)
        return jsonify({'message': 'Déconnecté avec succès'})

    @app.route('/api/auth/verify-email', methods=['POST'])
    @login_required
    def verify_email():
        data = request.json
        code = data.get('code', '')
        user_id = g.user_id
        stored = email_verification_codes.get(user_id)
        if not stored:
            return jsonify({'error': 'Aucun code en attente'}), 400
        if time.time() > stored['expires']:
            del email_verification_codes[user_id]
            return jsonify({'error': 'Code expiré'}), 400
        if code != stored['code']:
            return jsonify({'error': 'Code invalide'}), 400
        
        db = get_db()
        db.execute("UPDATE users SET email_verified = 1 WHERE id = ?", (user_id,))
        db.commit()
        del email_verification_codes[user_id]
        return jsonify({'message': 'Email vérifié avec succès'})

    @app.route('/api/auth/totp/enable', methods=['POST'])
    @login_required
    def enable_totp():
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE id = ?", (g.user_id,)).fetchone()
        if user['totp_enabled']:
            return jsonify({'error': 'TOTP déjà activé'}), 400
        
        secret = generate_totp_secret()
        totp_secrets[g.user_id] = secret
        uri = get_totp_uri(secret, user['username'])
        return jsonify({'secret': secret, 'uri': uri})

    @app.route('/api/auth/totp/verify', methods=['POST'])
    @login_required
    def verify_totp_enable():
        data = request.json
        code = data.get('code', '')
        secret = totp_secrets.get(g.user_id)
        if not secret:
            return jsonify({'error': 'TOTP non initialisé'}), 400
        if verify_totp(secret, code):
            db = get_db()
            db.execute("UPDATE users SET totp_enabled = 1 WHERE id = ?", (g.user_id,))
            db.commit()
            return jsonify({'message': 'TOTP activé avec succès'})
        return jsonify({'error': 'Code TOTP invalide'}), 400

    @app.route('/api/auth/totp/disable', methods=['POST'])
    @login_required
    def disable_totp():
        data = request.json
        code = data.get('code', '')
        secret = totp_secrets.get(g.user_id)
        if secret and verify_totp(secret, code):
            db = get_db()
            db.execute("UPDATE users SET totp_enabled = 0 WHERE id = ?", (g.user_id,))
            db.commit()
            totp_secrets.pop(g.user_id, None)
            return jsonify({'message': 'TOTP désactivé avec succès'})
        return jsonify({'error': 'Code TOTP invalide'}), 400

    @app.route('/api/auth/oauth/google', methods=['POST'])
    def oauth_google():
        """Simulation d'authentification Google OAuth2"""
        data = request.json
        # En production, valider le token Google et récupérer les infos utilisateur
        google_id = data.get('google_id')
        email = data.get('email')
        name = data.get('name')
        
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE oauth_google_id = ?", (google_id,)).fetchone()
        if not user:
            # Créer un nouveau compte lié à Google
            db.execute(
                "INSERT INTO users (username, email, oauth_google_id, balance, email_verified) VALUES (?, ?, ?, 10000, 1)",
                (name, email, google_id)
            )
            db.commit()
            user = db.execute("SELECT * FROM users WHERE oauth_google_id = ?", (google_id,)).fetchone()
        
        access_token = create_access_token(user['id'])
        refresh_token = create_refresh_token(user['id'])
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user_id': user['id']
        })

    @app.route('/api/auth/oauth/github', methods=['POST'])
    def oauth_github():
        """Simulation d'authentification GitHub OAuth2"""
        data = request.json
        github_id = data.get('github_id')
        email = data.get('email')
        name = data.get('name')
        
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE oauth_github_id = ?", (github_id,)).fetchone()
        if not user:
            db.execute(
                "INSERT INTO users (username, email, oauth_github_id, balance, email_verified) VALUES (?, ?, ?, 10000, 1)",
                (name, email, github_id)
            )
            db.commit()
            user = db.execute("SELECT * FROM users WHERE oauth_github_id = ?", (github_id,)).fetchone()
        
        access_token = create_access_token(user['id'])
        refresh_token = create_refresh_token(user['id'])
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user_id': user['id']
        })