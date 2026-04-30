#!/usr/bin/env python3
"""
osislint — Linter officiel pour OsisLang
Usage : osislint [options] fichier.osis
"""
import sys, re, argparse, json
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

# ============================================================
# RÈGLES DE LINTING
# ============================================================
@dataclass
class LintRule:
    code: str
    severity: str  # 'error', 'warning', 'info'
    message: str
    check: callable

RULES = []

def rule(code, severity, message):
    def decorator(func):
        RULES.append(LintRule(code, severity, message, func))
        return func
    return decorator

# ----------------------------------------------------------
# Règles de style
# ----------------------------------------------------------
@rule('E001', 'error', 'Ligne trop longue (max 100 caractères)')
def check_line_length(line, lineno, context):
    if len(line.rstrip()) > 100:
        return True
    return False

@rule('W001', 'warning', 'Espaces en fin de ligne')
def check_trailing_whitespace(line, lineno, context):
    if line.rstrip() != line.rstrip('\n\r ') and line.strip():
        return True
    return False

@rule('W002', 'warning', 'Utiliser des espaces, pas des tabulations')
def check_tabs(line, lineno, context):
    if '\t' in line:
        return True
    return False

# ----------------------------------------------------------
# Règles de nommage
# ----------------------------------------------------------
@rule('N001', 'warning', 'Les variables doivent être en minuscule_underscore')
def check_snake_case(line, lineno, context):
    for match in re.finditer(r'\bsoit\s+([A-Z][a-zA-Z_]*)', line):
        return True
    return False

@rule('N002', 'warning', 'Les classes doivent être en CamelCase')
def check_class_case(line, lineno, context):
    for match in re.finditer(r'\bclasse\s+([a-z][a-zA-Z_]*)', line):
        return True
    return False

# ----------------------------------------------------------
# Règles de token OLC
# ----------------------------------------------------------
@rule('T001', 'error', 'Compte déjà existant, utiliser solde() pour vérifier')
def check_duplicate_account(line, lineno, context):
    if 'compte' in line:
        name = re.search(r'compte\s+"([^"]*)"', line)
        if name and name.group(1) in context.get('accounts', set()):
            return True
        elif name:
            context.setdefault('accounts', set()).add(name.group(1))
    return False

@rule('T002', 'warning', 'Transfert sans vérification de solde préalable')
def check_transfer_without_balance(line, lineno, context):
    if 'transfere' in line and 'solde' not in context.get('last_balance_check', ''):
        return True
    if 'solde' in line:
        context['last_balance_check'] = line
    return False

# ----------------------------------------------------------
# Règles de complexité
# ----------------------------------------------------------
@rule('C001', 'warning', 'Fonction trop longue (> 30 lignes)')
def check_function_length(line, lineno, context):
    if 'fonction' in line:
        context['current_function_start'] = lineno
        context['current_function_lines'] = 0
    if 'current_function_start' in context:
        context['current_function_lines'] += 1
    if '}' in line and 'current_function_start' in context:
        if context['current_function_lines'] > 30:
            return True
        del context['current_function_start']
        del context['current_function_lines']
    return False

@rule('C002', 'warning', 'Profondeur d\'imbrication > 4')
def check_nesting_depth(line, lineno, context):
    depth = context.get('depth', 0)
    opens = line.count('{')
    closes = line.count('}')
    if opens - closes > 0:
        depth += opens - closes
        context['depth'] = depth
    if depth > 4:
        return True
    return False

# ============================================================
# MOTEUR DE LINTING
# ============================================================
@dataclass
class LintMessage:
    file: str
    line: int
    col: int
    code: str
    severity: str
    message: str

class Linter:
    def __init__(self, rules=None):
        self.rules = rules or RULES
        self.messages = []
    
    def lint_file(self, filepath: str) -> List[LintMessage]:
        self.messages = []
        context = {'accounts': set(), 'last_balance_check': '', 'depth': 0}
        
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for lineno, line in enumerate(lines, 1):
            for rule in self.rules:
                try:
                    if rule.check(line, lineno, context):
                        self.messages.append(
                            LintMessage(filepath, lineno, 0, rule.code, rule.severity, rule.message)
                        )
                except Exception:
                    pass  # Une règle ne doit jamais planter
        
        return self.messages
    
    def format_output(self, messages: List[LintMessage], format='text') -> str:
        if format == 'json':
            return json.dumps([{'file': m.file, 'line': m.line, 'code': m.code, 'severity': m.severity, 'message': m.message} for m in messages], indent=2)
        
        # Format texte
        severity_colors = {'error': '\033[31m', 'warning': '\033[33m', 'info': '\033[36m'}
        reset = '\033[0m'
        output = []
        for m in messages:
            color = severity_colors.get(m.severity, '')
            output.append(f"{m.file}:{m.line}:{m.col}: {color}{m.code} [{m.severity}]{reset} {m.message}")
        return '\n'.join(output) if output else "✅ Aucun problème détecté."

def main():
    parser = argparse.ArgumentParser(description='osislint — Linter officiel OsisLang')
    parser.add_argument('file', nargs='+', help='Fichier(s) .osis à analyser')
    parser.add_argument('--format', choices=['text', 'json'], default='text', help='Format de sortie')
    parser.add_argument('--fix', action='store_true', help='Corriger automatiquement (à venir)')
    parser.add_argument('--version', action='version', version='osislint v1.0.0')
    args = parser.parse_args()
    
    linter = Linter()
    all_messages = []
    
    for filepath in args.file:
        messages = linter.lint_file(filepath)
        all_messages.extend(messages)
    
    if all_messages:
        print(linter.format_output(all_messages, args.format))
        has_errors = any(m.severity == 'error' for m in all_messages)
        sys.exit(1 if has_errors else 0)
    else:
        print(linter.format_output([], args.format))

if __name__ == '__main__':
    main()