// ast.h
#pragma once
#include <memory>
#include <vector>
#include <string>

// Nœuds de base pour l'AST
struct ASTNoeud { virtual ~ASTNoeud() = default; };

// Expressions
struct NombreExpr : ASTNoeud { double valeur; };
struct ChaineExpr : ASTNoeud { std::string valeur; };
struct VariableExpr : ASTNoeud { std::string nom; };
struct BinaireExpr : ASTNoeud { char operateur; std::unique_ptr<ASTNoeud> gauche, droite; };
struct AppelExpr : ASTNoeud { std::string fonction; std::vector<std::unique_ptr<ASTNoeud>> arguments; };

// Instructions
struct RetournerInstr : ASTNoeud { std::unique_ptr<ASTNoeud> expression; };
struct SiInstr : ASTNoeud { std::unique_ptr<ASTNoeud> condition, alors, sinon; };
struct AssignInstr : ASTNoeud { std::string nom; std::unique_ptr<ASTNoeud> expression; };
struct AfficherInstr : ASTNoeud { std::unique_ptr<ASTNoeud> expression; };
struct DefFonction : ASTNoeud { std::string nom; std::vector<std::pair<std::string,std::string>> params; std::string typeRetour; std::vector<std::unique_ptr<ASTNoeud>> corps; };
struct Programme : ASTNoeud { std::vector<std::unique_ptr<ASTNoeud>> fonctions; };