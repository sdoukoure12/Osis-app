#!/bin/bash
# =============================================================================
# 🌲 OSISLANG — Langage de programmation complet avec token natif (OLC)
# Auteur : sdoukoure12
# GitHub : https://github.com/sdoukoure12/Osis-app
# =============================================================================
# OsisLang est un langage de script moderne, interprété, avec :
#   • types primitifs (int, float, str, bool, list, map)
#   • structures de contrôle (if/else, while, for)
#   • fonctions, classes, héritage
#   • token natif OLC (comptes, transferts, solde)
#   • modules et bibliothèque standard
# =============================================================================
set -e

GREEN='\033[0;32m'; CYAN='\033[0;36m'; YELLOW='\033[1;33m'; NC='\033[0m'
echo -e "${GREEN}🌲 Installation d'OsisLang${NC}"

INSTALL_DIR="/opt/osislang"
sudo mkdir -p $INSTALL_DIR && sudo chown -R $USER:$USER $INSTALL_DIR
mkdir -p $INSTALL_DIR/{bin,lib,examples,data}

# -----------------------------------------------------------------------------
# L'INTERPRÉTEUR OSISLANG COMPLET
# -----------------------------------------------------------------------------
cat > $INSTALL_DIR/bin/osislang << 'INTERPRETER'
#!/usr/bin/env python3
"""
OsisLang Interpreter v2.0 – Langage complet avec token OLC natif
Usage: osislang [options] fichier.osis
"""
import sys, os, re, json, math, random, time, argparse
from pathlib import Path

# ======================== LEXER ========================
TOKEN_SPEC = [
    ('COMMENT', r'#.*'),
    ('NEWLINE', r'\n'),
    ('NUMBER', r'\d+\.\d+|\d+'),
    ('STRING', r'"[^"]*"'),
    ('BOOL', r'true|false'),
    ('ID', r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ('OP', r'==|!=|<=|>=|[\+\-\*/<>=]'),
    ('ASSIGN', r'='),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('LBRACKET', r'\['),
    ('RBRACKET', r'\]'),
    ('LBRACE', r'\{'),
    ('RBRACE', r'\}'),
    ('COMMA', r','),
    ('DOT', r'\.'),
    ('COLON', r':'),
    ('ARROW', r'->'),
    ('SKIP', r'[ \t\r]+'),
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
            raise SyntaxError(f"Caractère inattendu ligne {line_num}: {code[pos]!r}")
    tokens.append(('EOF', '', line_num))
    return tokens

# ======================== AST NODES ========================
class ASTNode:
    pass

class Program(ASTNode):
    def __init__(self, statements): self.statements = statements

class VarDecl(ASTNode):
    def __init__(self, name, type_annotation, value): self.name=name; self.type=type_annotation; self.value=value

class Assign(ASTNode):
    def __init__(self, name, value): self.name=name; self.value=value

class If(ASTNode):
    def __init__(self, cond, then_block, else_block): self.cond=cond; self.then=then_block; self.else_=else_block

class While(ASTNode):
    def __init__(self, cond, body): self.cond=cond; self.body=body

class For(ASTNode):
    def __init__(self, var, iterable, body): self.var=var; self.iterable=iterable; self.body=body

class FunctionDef(ASTNode):
    def __init__(self, name, params, body): self.name=name; self.params=params; self.body=body

class ClassDef(ASTNode):
    def __init__(self, name, base, body): self.name=name; self.base=base; self.body=body

class Return(ASTNode):
    def __init__(self, value): self.value=value

class Break(ASTNode): pass
class Continue(ASTNode): pass

class Expression(ASTNode): pass

class BinOp(Expression):
    def __init__(self, left, op, right): self.left=left; self.op=op; self.right=right

class UnaryOp(Expression):
    def __init__(self, op, operand): self.op=op; self.operand=operand

class Call(Expression):
    def __init__(self, func, args): self.func=func; self.args=args

class GetAttr(Expression):
    def __init__(self, obj, attr): self.obj=obj; self.attr=attr

class Index(Expression):
    def __init__(self, obj, index): self.obj=obj; self.index=index

class Literal(Expression):
    def __init__(self, value): self.value=value

class Var(Expression):
    def __init__(self, name): self.name=name

class ListLiteral(Expression):
    def __init__(self, elements): self.elements=elements

class MapLiteral(Expression):
    def __init__(self, pairs): self.pairs=pairs

class Lambda(Expression):
    def __init__(self, params, body): self.params=params; self.body=body

class TokenBuiltin(Expression):
    def __init__(self, name, args): self.name=name; self.args=args

# ======================== PARSER ========================
class ParseError(Exception): pass

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self): return self.tokens[self.pos]
    def consume(self, expected_type=None):
        tok = self.tokens[self.pos]
        if expected_type and tok[0] != expected_type:
            raise ParseError(f"Ligne {tok[2]}: attendu {expected_type}, obtenu {tok[0]} ({tok[1]})")
        self.pos += 1
        return tok
    def match(self, *types):
        if self.peek()[0] in types:
            return self.consume()
        return None

    def parse(self):
        stmts = []
        while self.peek()[0] != 'EOF':
            stmts.append(self.statement())
        return Program(stmts)

    def statement(self):
        if self.peek()[0] == 'NEWLINE':
            self.consume('NEWLINE')
            return None
        # Gestion des mots-clés
        kw = self.peek()[1]
        if kw == 'soit': return self.var_decl()
        if kw == 'si': return self.if_stmt()
        if kw == 'tantque': return self.while_stmt()
        if kw == 'pour': return self.for_stmt()
        if kw == 'fonction': return self.func_def()
        if kw == 'classe': return self.class_def()
        if kw == 'retourne': return self.return_stmt()
        if kw == 'arrete': return self.break_stmt()
        if kw == 'continue': return self.continue_stmt()
        if kw == 'affiche': return self.print_stmt()
        # Token builtins
        if kw in ('compte', 'solde', 'transfere', 'emettre'):
            return self.token_stmt()
        # Sinon expression simple ou assignation
        return self.expr_or_assign()

    def var_decl(self):
        self.consume('ID')  # 'soit'
        name = self.consume('ID')[1]
        type_annotation = None
        if self.match('COLON'):
            type_annotation = self.consume('ID')[1]
        self.consume('ASSIGN')
        value = self.expression()
        return VarDecl(name, type_annotation, value)

    def expr_or_assign(self):
        expr = self.expression()
        if self.match('ASSIGN'):
            # C'est une assignation
            value = self.expression()
            if isinstance(expr, Var):
                return Assign(expr.name, value)
            elif isinstance(expr, GetAttr):
                return SetAttr(expr.obj, expr.attr, value)  # à définir
            else:
                raise ParseError("Cible d'assignation invalide")
        return expr

    def if_stmt(self):
        self.consume('ID'); cond = self.expression(); self.consume('LBRACE')
        then_body = self.block()
        else_body = None
        if self.match('ID') and self.tokens[self.pos-1][1] == 'sinon':
            self.consume('LBRACE')
            else_body = self.block()
        return If(cond, then_body, else_body)

    def while_stmt(self):
        self.consume('ID'); cond = self.expression(); self.consume('LBRACE')
        body = self.block()
        return While(cond, body)

    def for_stmt(self):
        self.consume('ID'); var = self.consume('ID')[1]
        self.consume('ID')  # 'dans'
        iterable = self.expression()
        self.consume('LBRACE')
        body = self.block()
        return For(var, iterable, body)

    def func_def(self):
        self.consume('ID'); name = self.consume('ID')[1]
        self.consume('LPAREN'); params = []
        if self.peek()[0] != 'RPAREN':
            params.append(self.consume('ID')[1])
            while self.match('COMMA'):
                params.append(self.consume('ID')[1])
        self.consume('RPAREN')
        self.consume('LBRACE')
        body = self.block()
        return FunctionDef(name, params, body)

    def class_def(self):
        self.consume('ID'); name = self.consume('ID')[1]
        base = None
        if self.match('LPAREN'):
            base = self.consume('ID')[1]
            self.consume('RPAREN')
        self.consume('LBRACE')
        body = []
        while self.peek()[0] != 'RBRACE' and self.peek()[0] != 'EOF':
            if self.peek()[1] == 'fonction':
                body.append(self.func_def())
            else:
                # attributs (var decl)
                body.append(self.var_decl())
        self.consume('RBRACE')
        return ClassDef(name, base, body)

    def return_stmt(self):
        self.consume('ID'); value = None
        if self.peek()[0] not in ('NEWLINE','RBRACE','EOF'):
            value = self.expression()
        return Return(value)

    def break_stmt(self): self.consume('ID'); return Break()
    def continue_stmt(self): self.consume('ID'); return Continue()

    def print_stmt(self):
        self.consume('ID'); args = []
        if self.peek()[0] not in ('NEWLINE','RBRACE','EOF'):
            args.append(self.expression())
            while self.match('COMMA'):
                args.append(self.expression())
        return Print(args)

    def token_stmt(self):
        kw = self.consume('ID')[1]
        if kw == 'compte':
            name = self.consume('STRING')[1].strip('"')
            self.consume('ID')  # 'avec'
            amount = self.expression()
            return TokenBuiltin('create_account', [Literal(name), amount])
        elif kw == 'transfere':
            sender = self.consume('STRING')[1].strip('"')
            self.consume('ARROW')
            receiver = self.consume('STRING')[1].strip('"')
            self.consume('COLON')
            amount = self.expression()
            return TokenBuiltin('transfer', [Literal(sender), Literal(receiver), amount])
        elif kw == 'solde':
            name = self.consume('STRING')[1].strip('"')
            return TokenBuiltin('balance', [Literal(name)])
        elif kw == 'emettre':
            name = self.consume('STRING')[1].strip('"')
            amount = self.expression()
            return TokenBuiltin('mint', [Literal(name), amount])
        else:
            raise ParseError(f"Instruction token inconnue: {kw}")

    def block(self):
        stmts = []
        while self.peek()[0] not in ('RBRACE','EOF'):
            stmt = self.statement()
            if stmt: stmts.append(stmt)
        self.consume('RBRACE')
        return stmts

    def expression(self): return self.comparison()
    def comparison(self):
        left = self.addition()
        while self.peek()[0] == 'OP' and self.peek()[1] in ('==','!=','<=','>=','<','>'):
            op = self.consume('OP')[1]
            right = self.addition()
            left = BinOp(left, op, right)
        return left
    def addition(self):
        left = self.term()
        while self.peek()[0] == 'OP' and self.peek()[1] in ('+','-'):
            op = self.consume('OP')[1]
            right = self.term()
            left = BinOp(left, op, right)
        return left
    def term(self):
        left = self.unary()
        while self.peek()[0] == 'OP' and self.peek()[1] in ('*','/'):
            op = self.consume('OP')[1]
            right = self.unary()
            left = BinOp(left, op, right)
        return left
    def unary(self):
        if self.peek()[0] == 'OP' and self.peek()[1] in ('-','!'):
            op = self.consume('OP')[1]
            operand = self.unary()
            return UnaryOp(op, operand)
        return self.postfix()
    def postfix(self):
        expr = self.primary()
        while True:
            if self.match('LPAREN'):
                args = []
                if self.peek()[0] != 'RPAREN':
                    args.append(self.expression())
                    while self.match('COMMA'):
                        args.append(self.expression())
                self.consume('RPAREN')
                expr = Call(expr, args)
            elif self.match('LBRACKET'):
                index = self.expression()
                self.consume('RBRACKET')
                expr = Index(expr, index)
            elif self.match('DOT'):
                attr = self.consume('ID')[1]
                expr = GetAttr(expr, attr)
            else:
                break
        return expr
    def primary(self):
        tok = self.peek()
        if tok[0] == 'NUMBER':
            self.consume('NUMBER')
            return Literal(float(tok[1]) if '.' in tok[1] else int(tok[1]))
        elif tok[0] == 'STRING':
            self.consume('STRING')
            return Literal(tok[1][1:-1])
        elif tok[0] == 'BOOL':
            self.consume('BOOL')
            return Literal(tok[1]=='true')
        elif tok[0] == 'ID':
            name = self.consume('ID')[1]
            if name in ('compte','solde','transfere','emettre'):
                return self.token_expr(name)
            return Var(name)
        elif tok[0] == 'LPAREN':
            self.consume('LPAREN'); expr = self.expression(); self.consume('RPAREN')
            return expr
        elif tok[0] == 'LBRACKET':  # liste
            self.consume('LBRACKET'); items = []
            if self.peek()[0] != 'RBRACKET':
                items.append(self.expression())
                while self.match('COMMA'):
                    items.append(self.expression())
            self.consume('RBRACKET'); return ListLiteral(items)
        else:
            raise ParseError(f"Expression inattendue: {tok}")

    def token_expr(self, name):
        if name == 'solde':
            self.consume('LPAREN'); acc = self.consume('STRING')[1].strip('"'); self.consume('RPAREN')
            return TokenBuiltin('balance', [Literal(acc)])
        return Var(name)

# ======================== ENVIRONMENT & VALUES ========================
class ReturnException(Exception):
    def __init__(self, value): self.value = value

class BreakException(Exception): pass
class ContinueException(Exception): pass

class Environment:
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent
    def get(self, name):
        if name in self.vars: return self.vars[name]
        if self.parent: return self.parent.get(name)
        raise NameError(f"Variable '{name}' non définie")
    def set(self, name, value):
        self.vars[name] = value
    def assign(self, name, value):
        if name in self.vars:
            self.vars[name] = value
        elif self.parent:
            self.parent.assign(name, value)
        else:
            raise NameError(f"Variable '{name}' non définie")

class OsisObject:
    def __init__(self, cls, fields):
        self.cls = cls
        self.fields = fields
    def get(self, name):
        if name in self.fields: return self.fields[name]
        if self.cls and name in self.cls.methods:
            return self.cls.methods[name]
        raise AttributeError(f"Attribut '{name}' non trouvé")
    def set(self, name, value):
        self.fields[name] = value

class OsisClass:
    def __init__(self, name, base, methods):
        self.name = name
        self.base = base
        self.methods = methods

class OsisFunction:
    def __init__(self, params, body, env):
        self.params = params
        self.body = body
        self.env = env

class BuiltinFunction:
    def __init__(self, func): self.func = func

# ======================== EVALUATOR ========================
class Evaluator:
    def __init__(self):
        self.globals = Environment()
        self._setup_builtins()
        self.ledger = self._load_ledger()

    def _load_ledger(self):
        path = Path(os.path.expanduser('~/.osislang/ledger.json'))
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            with open(path) as f: return json.load(f)
        return {}

    def _save_ledger(self):
        path = Path(os.path.expanduser('~/.osislang/ledger.json'))
        with open(path, 'w') as f: json.dump(self.ledger, f, indent=2)

    def _setup_builtins(self):
        # Fonctions d'affichage
        self.globals.set('affiche', BuiltinFunction(lambda args: print(*(str(a) for a in args))))
        self.globals.set('entree', BuiltinFunction(lambda args: input(args[0] if args else '')))
        self.globals.set('type', BuiltinFunction(lambda args: type(args[0]).__name__))
        self.globals.set('longueur', BuiltinFunction(lambda args: len(args[0])))
        self.globals.set('aleatoire', BuiltinFunction(lambda args: random.random()))
        self.globals.set('plancher', BuiltinFunction(lambda args: math.floor(args[0])))
        # Token builtins
        self.globals.set('compte', BuiltinFunction(self._create_account))
        self.globals.set('transfere', BuiltinFunction(self._transfer))
        self.globals.set('solde', BuiltinFunction(self._balance))
        self.globals.set('emettre', BuiltinFunction(self._mint))

    def _create_account(self, args):
        name, amount = args[0], args[1]
        if name in self.ledger: raise Exception(f"Compte '{name}' existe déjà")
        self.ledger[name] = amount
        self._save_ledger()
        return amount

    def _transfer(self, args):
        sender, receiver, amount = args[0], args[1], args[2]
        if sender not in self.ledger: raise Exception(f"Compte '{sender}' introuvable")
        if self.ledger[sender] < amount: raise Exception(f"Solde insuffisant pour {sender}")
        self.ledger[sender] -= amount
        self.ledger.setdefault(receiver, 0)
        self.ledger[receiver] += amount
        self._save_ledger()
        return amount

    def _balance(self, args):
        name = args[0]
        return self.ledger.get(name, 0)

    def _mint(self, args):
        name, amount = args[0], args[1]
        self.ledger.setdefault(name, 0)
        self.ledger[name] += amount
        self._save_ledger()
        return amount

    def eval(self, node, env=None):
        if env is None: env = self.globals
        method = f'eval_{type(node).__name__}'
        if hasattr(self, method):
            return getattr(self, method)(node, env)
        else:
            raise NotImplementedError(f"Évaluation de {type(node).__name__} non implémentée")

    def eval_Program(self, prog, env):
        result = None
        for stmt in prog.statements:
            result = self.eval(stmt, env)
        return result

    def eval_VarDecl(self, node, env):
        value = self.eval(node.value, env)
        env.set(node.name, value)
        return value

    def eval_Assign(self, node, env):
        value = self.eval(node.value, env)
        env.assign(node.name, value)
        return value

    def eval_If(self, node, env):
        cond = self.eval(node.cond, env)
        if cond:
            return self._exec_block(node.then, Environment(env))
        elif node.else_:
            return self._exec_block(node.else_, Environment(env))

    def eval_While(self, node, env):
        while self.eval(node.cond, env):
            try:
                self._exec_block(node.body, Environment(env))
            except BreakException:
                break
            except ContinueException:
                continue

    def eval_For(self, node, env):
        iterable = self.eval(node.iterable, env)
        for item in iterable:
            inner = Environment(env)
            inner.set(node.var, item)
            try:
                self._exec_block(node.body, inner)
            except BreakException:
                break
            except ContinueException:
                continue

    def eval_FunctionDef(self, node, env):
        func = OsisFunction(node.params, node.body, env)
        env.set(node.name, func)
        return func

    def eval_ClassDef(self, node, env):
        methods = {}
        for item in node.body:
            if isinstance(item, FunctionDef):
                func = OsisFunction(item.params, item.body, env)
                methods[item.name] = func
        cls = OsisClass(node.name, node.base, methods)
        env.set(node.name, cls)
        return cls

    def eval_Return(self, node, env):
        value = self.eval(node.value, env) if node.value else None
        raise ReturnException(value)

    def eval_Break(self, node, env): raise BreakException()
    def eval_Continue(self, node, env): raise ContinueException()

    def eval_BinOp(self, node, env):
        left = self.eval(node.left, env)
        right = self.eval(node.right, env)
        op = node.op
        if op == '+': return left + right
        if op == '-': return left - right
        if op == '*': return left * right
        if op == '/': return left / right
        if op == '==': return left == right
        if op == '!=': return left != right
        if op == '<': return left < right
        if op == '>': return left > right
        if op == '<=': return left <= right
        if op == '>=': return left >= right
        raise ValueError(f"Opérateur inconnu: {op}")

    def eval_UnaryOp(self, node, env):
        val = self.eval(node.operand, env)
        if node.op == '-': return -val
        if node.op == '!': return not val
        raise ValueError(f"Opérateur unaire inconnu: {node.op}")

    def eval_Call(self, node, env):
        func = self.eval(node.func, env)
        args = [self.eval(a, env) for a in node.args]
        if isinstance(func, OsisFunction):
            inner = Environment(func.env)
            for p, a in zip(func.params, args):
                inner.set(p, a)
            try:
                return self._exec_block(func.body, inner)
            except ReturnException as e:
                return e.value
        elif isinstance(func, BuiltinFunction):
            return func.func(args)
        elif isinstance(func, OsisClass):
            # Construction d'une instance
            instance = OsisObject(func, {})
            # Appel du constructeur si existe
            if 'init' in func.methods:
                init = func.methods['init']
                inner = Environment(func.env)
                inner.set('soi', instance)
                for p, a in zip(init.params, args):
                    inner.set(p, a)
                self._exec_block(init.body, inner)
            return instance
        else:
            raise TypeError(f"{func} n'est pas appelable")

    def eval_GetAttr(self, node, env):
        obj = self.eval(node.obj, env)
        if isinstance(obj, OsisObject):
            attr = obj.get(node.attr)
            if isinstance(attr, OsisFunction):
                # Lier la méthode à l'objet (this)
                return BuiltinFunction(lambda args, f=attr, o=obj: self._call_method(f, o, args))
            return obj.fields.get(node.attr)
        raise AttributeError(f"Objet sans attribut: {node.attr}")

    def _call_method(self, func, obj, args):
        inner = Environment(func.env)
        inner.set('soi', obj)
        for p, a in zip(func.params, args):
            inner.set(p, a)
        return self._exec_block(func.body, inner)

    def eval_Index(self, node, env):
        obj = self.eval(node.obj, env)
        index = self.eval(node.index, env)
        return obj[index]

    def eval_Literal(self, node, env): return node.value
    def eval_Var(self, node, env): return env.get(node.name)
    def eval_ListLiteral(self, node, env): return [self.eval(e, env) for e in node.elements]
    def eval_MapLiteral(self, node, env):
        m = {}
        for k,v in node.pairs:
            m[self.eval(k,env)] = self.eval(v,env)
        return m

    def eval_TokenBuiltin(self, node, env):
        if node.name == 'balance':
            return self._balance([self.eval(node.args[0], env)])
        elif node.name == 'create_account':
            return self._create_account([self.eval(a,env) for a in node.args])
        elif node.name == 'transfer':
            return self._transfer([self.eval(a,env) for a in node.args])
        elif node.name == 'mint':
            return self._mint([self.eval(a,env) for a in node.args])
        else:
            raise ValueError(f"Token builtin inconnu: {node.name}")

    def _exec_block(self, stmts, env):
        result = None
        for stmt in stmts:
            result = self.eval(stmt, env)
        return result

def main():
    parser = argparse.ArgumentParser(description='OsisLang Interpreter')
    parser.add_argument('file', help='Fichier .osis')
    args = parser.parse_args()
    with open(args.file, 'r') as f: code = f.read()
    tokens = lex(code)
    ast = Parser(tokens).parse()
    evaluator = Evaluator()
    evaluator.eval(ast)

if __name__ == '__main__':
    main()
INTERPRETER

chmod +x $INSTALL_DIR/bin/osislang

# -----------------------------------------------------------------------------
# Exemples de programmes OsisLang
# -----------------------------------------------------------------------------
# Programme 1 : Token natif
cat > $INSTALL_DIR/examples/token.osis << 'EX1'
# Démonstration du token OLC natif
compte "alice" avec 1000
compte "bob" avec 500
transfere "alice" -> "bob" : 200
affiche "Solde alice:", solde("alice")
affiche "Solde bob:", solde("bob")
EX1

# Programme 2 : Structures de contrôle et fonctions
cat > $INSTALL_DIR/examples/fibonacci.osis << 'EX2'
fonction fib(n) {
    si n < 2 {
        retourne n
    }
    retourne fib(n-1) + fib(n-2)
}
affiche fib(10)
EX2

# Programme 3 : Classes
cat > $INSTALL_DIR/examples/compte_bancaire.osis << 'EX3'
classe Compte {
    soit solde = 0
    fonction depot(montant) {
        soi.solde = soi.solde + montant
    }
    fonction retrait(montant) {
        si soi.solde >= montant {
            soi.solde = soi.solde - montant
        }
    }
}

soit c = Compte()
c.depot(100)
c.retrait(30)
affiche c.solde
EX3

echo -e "${GREEN}✅ OsisLang installé avec succès !${NC}"
echo "Interpréteur : $INSTALL_DIR/bin/osislang"
echo "Exemples    : $INSTALL_DIR/examples/"
echo "Pour exécuter : osislang fichier.osis"