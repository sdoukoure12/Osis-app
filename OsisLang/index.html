#!/bin/bash
# =============================================================================
# 🌲 OSISLANG — Langage de programmation avec token natif
# Auteur : sdoukoure12
# GitHub : https://github.com/sdoukoure12/Osis-app
# =============================================================================
set -e

GREEN='\033[0;32m'; CYAN='\033[0;36m'; YELLOW='\033[1;33m'; NC='\033[0m'
echo -e "${GREEN}🌲 Installation d'OsisLang${NC}"

INSTALL_DIR="/opt/osislang"
sudo mkdir -p $INSTALL_DIR && sudo chown -R $USER:$USER $INSTALL_DIR
mkdir -p $INSTALL_DIR/{bin,examples,data}

# -----------------------------------------------------------------------------
# 1. L'interpréteur OsisLang (Python)
# -----------------------------------------------------------------------------
cat > $INSTALL_DIR/bin/osislang.py << 'INTERPRETER'
#!/usr/bin/env python3
"""OsisLang Interpreter v1.0 — Token natif intégré"""
import json, os, sys, re
from pathlib import Path

# ---------------------------------------------------------------------------
# Lexer
# ---------------------------------------------------------------------------
TOKEN_SPEC = [
    ('COMMENT',  r'#.*'),
    ('ARROW',    r'->'),
    ('TRANSFER', r':'),
    ('NUMBER',   r'\d+(\.\d+)?'),
    ('STRING',   r'"[^"]*"'),
    ('ID',       r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ('OP',       r'[+\-*/<>=!]+'),
    ('LPAREN',   r'\('),
    ('RPAREN',   r'\)'),
    ('LBRACKET', r'\['),
    ('RBRACKET', r'\]'),
    ('COMMA',    r','),
    ('NEWLINE',  r'\n'),
    ('SKIP',     r'[ \t]+'),
    ('MISMATCH', r'.'),
]

def lex(code):
    tokens = []
    line_num = 1
    pos = 0
    while pos < len(code):
        match = None
        for tok_type, pattern in TOKEN_SPEC:
            regex = re.compile(pattern)
            match = regex.match(code, pos)
            if match:
                text = match.group(0)
                if tok_type == 'NEWLINE':
                    line_num += 1
                elif tok_type not in ('SKIP', 'COMMENT'):
                    tokens.append((tok_type, text, line_num))
                pos = match.end()
                break
        if not match:
            raise SyntaxError(f"Caractère inattendu: {code[pos]!r} ligne {line_num}")
    tokens.append(('EOF', '', line_num))
    return tokens

# ---------------------------------------------------------------------------
# Parser / AST
# ---------------------------------------------------------------------------
class ASTNode:
    pass

class Program(ASTNode):
    def __init__(self, statements):
        self.statements = statements

class CreateAccount(ASTNode):
    def __init__(self, name, initial_balance):
        self.name = name
        self.initial_balance = initial_balance

class Transfer(ASTNode):
    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount

class Print(ASTNode):
    def __init__(self, expression):
        self.expression = expression

class BalanceCall(ASTNode):
    def __init__(self, account):
        self.account = account

class BinOp(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class Number(ASTNode):
    def __init__(self, value):
        self.value = value

class String(ASTNode):
    def __init__(self, value):
        self.value = value

class Var(ASTNode):
    def __init__(self, name):
        self.name = name

# Parser functions
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos][0]

    def consume(self, expected_type=None):
        tok = self.tokens[self.pos]
        if expected_type and tok[0] != expected_type:
            raise SyntaxError(f"Attendu {expected_type}, trouvé {tok[0]} à la ligne {tok[2]}")
        self.pos += 1
        return tok

    def parse(self):
        stmts = []
        while self.peek() != 'EOF':
            stmts.append(self.statement())
        return Program(stmts)

    def statement(self):
        tok_type = self.peek()
        if tok_type == 'ID' and self.tokens[self.pos][1] == 'compte':
            return self.parse_create_account()
        elif tok_type == 'ID' and self.tokens[self.pos+1][0] == 'ARROW':
            return self.parse_transfer()
        elif tok_type == 'ID' and self.tokens[self.pos][1] == 'afficher':
            return self.parse_print()
        else:
            raise SyntaxError(f"Instruction inconnue: {self.tokens[self.pos][1]!r}")

    def parse_create_account(self):
        self.consume('ID')  # 'compte'
        name = self.consume('STRING')[1].strip('"')
        self.consume('ID')  # 'avec'
        amount = float(self.consume('NUMBER')[1])
        self.consume('ID')  # 'OLC'
        return CreateAccount(name, amount)

    def parse_transfer(self):
        sender = self.consume('ID')[1]
        self.consume('ARROW')
        receiver = self.consume('ID')[1]
        self.consume('TRANSFER')
        amount = float(self.consume('NUMBER')[1])
        self.consume('ID')  # 'OLC'
        return Transfer(sender, receiver, amount)

    def parse_print(self):
        self.consume('ID')  # 'afficher'
        expr = self.expression()
        return Print(expr)

    def expression(self):
        left = self.primary()
        while self.peek() == 'OP':
            op = self.consume('OP')[1]
            right = self.primary()
            left = BinOp(left, op, right)
        return left

    def primary(self):
        tok_type = self.peek()
        if tok_type == 'ID':
            name = self.consume('ID')[1]
            if name == 'solde':
                self.consume('LPAREN')
                account = self.consume('STRING')[1].strip('"')
                self.consume('RPAREN')
                return BalanceCall(account)
            else:
                return Var(name)
        elif tok_type == 'NUMBER':
            return Number(float(self.consume('NUMBER')[1]))
        elif tok_type == 'STRING':
            return String(self.consume('STRING')[1].strip('"'))
        else:
            raise SyntaxError(f"Expression inattendue: {self.tokens[self.pos]}")

# ---------------------------------------------------------------------------
# Evaluator (avec gestion des tokens)
# ---------------------------------------------------------------------------
class State:
    def __init__(self, storage_path):
        self.storage = Path(storage_path)
        self.storage.parent.mkdir(parents=True, exist_ok=True)
        self.ledger = {}
        self.load()

    def load(self):
        if self.storage.exists():
            with open(self.storage) as f:
                self.ledger = json.load(f)

    def save(self):
        with open(self.storage, 'w') as f:
            json.dump(self.ledger, f, indent=2)

    def balance(self, account):
        return self.ledger.get(account, 0.0)

    def set_balance(self, account, amount):
        self.ledger[account] = amount
        self.save()

class Evaluator:
    def __init__(self, state):
        self.state = state

    def eval(self, node):
        method = f'eval_{type(node).__name__}'
        return getattr(self, method)(node)

    def eval_Program(self, prog):
        for stmt in prog.statements:
            self.eval(stmt)

    def eval_CreateAccount(self, node):
        self.state.set_balance(node.name, node.initial_balance)
        print(f"✅ Compte '{node.name}' créé avec {node.initial_balance} OLC")

    def eval_Transfer(self, node):
        sender_bal = self.state.balance(node.sender)
        if sender_bal < node.amount:
            print(f"❌ Solde insuffisant pour {node.sender} ({sender_bal} OLC)")
            return
        self.state.set_balance(node.sender, sender_bal - node.amount)
        receiver_bal = self.state.balance(node.receiver)
        self.state.set_balance(node.receiver, receiver_bal + node.amount)
        print(f"💸 {node.sender} -> {node.receiver} : {node.amount} OLC")

    def eval_Print(self, node):
        value = self.eval(node.expression)
        print(value)

    def eval_BalanceCall(self, node):
        return self.state.balance(node.account)

    def eval_BinOp(self, node):
        left = self.eval(node.left)
        right = self.eval(node.right)
        if node.op == '+': return left + right
        if node.op == '-': return left - right
        if node.op == '*': return left * right
        if node.op == '/': return left / right
        raise ValueError(f"Opérateur inconnu: {node.op}")

    def eval_Number(self, node): return node.value
    def eval_String(self, node): return node.value
    def eval_Var(self, node): return self.state.balance(node.name)  # Les variables = comptes par défaut

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    import argparse
    parser = argparse.ArgumentParser(description='OsisLang Interpreter')
    parser.add_argument('file', help='Fichier .osis à exécuter')
    parser.add_argument('--ledger', default='data/ledger.json', help='Fichier de registre des comptes')
    args = parser.parse_args()

    with open(args.file, 'r') as f:
        code = f.read()

    tokens = lex(code)
    ast = Parser(tokens).parse()
    state = State(args.ledger)
    evaluator = Evaluator(state)
    evaluator.eval(ast)
    state.save()

if __name__ == '__main__':
    main()
INTERPRETER

# -----------------------------------------------------------------------------
# 2. Rendre exécutable
# -----------------------------------------------------------------------------
chmod +x $INSTALL_DIR/bin/osislang.py
sudo ln -sf $INSTALL_DIR/bin/osislang.py /usr/local/bin/osislang

# -----------------------------------------------------------------------------
# 3. Exemples de programmes OsisLang
# -----------------------------------------------------------------------------
# Exemple 1 : création de comptes et transfert
cat > $INSTALL_DIR/examples/transfert.osis << 'EX1'
# transfert.osis - Démonstration de transfert
compte "alice" avec 1000 OLC
compte "bob" avec 500 OLC
alice -> bob : 200 OLC
afficher solde("alice")
afficher solde("bob")
EX1

# Exemple 2 : plusieurs transferts et calculs
cat > $INSTALL_DIR/examples/bourse.osis << 'EX2'
# bourse.osis - Simulation de mini-bourse
compte "investisseur" avec 10000 OLC
compte "startup" avec 0 OLC

investisseur -> startup : 5000 OLC
afficher solde("startup")

# Retour sur investissement (simulé)
investisseur -> startup : solde("investisseur") * 0.1 OLC
afficher solde("investisseur")
EX2

# -----------------------------------------------------------------------------
# 4. Serveur API pour exécuter du OsisLang à distance
# -----------------------------------------------------------------------------
cat > $INSTALL_DIR/bin/osislang_server.py << 'APISERVER'
#!/usr/bin/env python3
"""Serveur API pour exécuter du code OsisLang"""
import json, subprocess, tempfile, os
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

LEDGER = os.path.join(os.path.dirname(__file__), '..', 'data', 'ledger.json')

class OsisAPI(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200); self._cors(); self.end_headers()

    def do_POST(self):
        if self.path == '/execute':
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            data = json.loads(body)
            code = data.get('code', '')

            # Écrire le code dans un fichier temporaire
            with tempfile.NamedTemporaryFile(mode='w', suffix='.osis', delete=False) as f:
                f.write(code)
                tmpfile = f.name

            try:
                result = subprocess.run(
                    ['python3', os.path.join(os.path.dirname(__file__), 'osislang.py'), tmpfile, '--ledger', LEDGER],
                    capture_output=True, text=True, timeout=10
                )
                output = result.stdout + result.stderr
                os.unlink(tmpfile)
                self._json_response({'success': True, 'output': output})
            except Exception as e:
                self._json_response({'success': False, 'error': str(e)})
        else:
            self._json_response({'error': 'Not found'}, 404)

    def do_GET(self):
        if self.path == '/health':
            self._json_response({'status': 'ok', 'service': 'osislang-api'})
        elif self.path == '/ledger':
            if Path(LEDGER).exists():
                with open(LEDGER) as f:
                    self._json_response(json.load(f))
            else:
                self._json_response({})
        else:
            self._json_response({'error': 'Not found'}, 404)

    def _json_response(self, data, status=200):
        self.send_response(status)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

if __name__ == '__main__':
    port = int(os.getenv('OSISLANG_PORT', 8400))
    print(f"🧠 OsisLang API sur http://localhost:{port}")
    HTTPServer(("0.0.0.0", port), OsisAPI).serve_forever()
APISERVER

chmod +x $INSTALL_DIR/bin/osislang_server.py

# -----------------------------------------------------------------------------
# 5. Lancement du serveur API + test
# -----------------------------------------------------------------------------
# Démarrage du serveur en arrière-plan
python3 $INSTALL_DIR/bin/osislang_server.py &
sleep 1

# Test rapide avec curl
echo -e "${CYAN}Test d'exécution d'un programme OsisLang via API...${NC}"
curl -s -X POST http://localhost:8400/execute \
  -H "Content-Type: application/json" \
  -d '{"code": "compte \"test\" avec 100 OLC\nafficher solde(\"test\")"}'

echo ""
echo -e "${GREEN}✅ OsisLang installé avec succès !${NC}"
echo "📂 Interpréteur : /usr/local/bin/osislang"
echo "📝 Exemples : $INSTALL_DIR/examples/"
echo "🌐 API : http://localhost:8400"
echo ""
echo "Pour exécuter un fichier .osis : osislang fichier.osis"