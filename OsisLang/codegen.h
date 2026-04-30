// codegen.h
#pragma once
#include "llvm/IR/LLVMContext.h"
#include "llvm/IR/Module.h"
#include "llvm/IR/IRBuilder.h"
#include "ast.h"

class GenerateurCode {
public:
    GenerateurCode();
    void generer(Programme& programme);
    void afficherIR();
    void compilerVersObjet(const std::string& nomFichier);

private:
    llvm::LLVMContext contexte;
    llvm::Module module;
    llvm::IRBuilder<> constructeur;
    std::map<std::string, llvm::Value*> valeursNommees;

    llvm::Function* genererFonction(DefFonction& fonc);
    llvm::Value* genererExpr(ASTNoeud* noeud);
    // ...
};