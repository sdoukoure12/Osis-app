// codegen.cpp (exemple de génération d'une expression binaire)
llvm::Value* GenerateurCode::genererExpr(ASTNoeud* noeud) {
    if (auto* num = dynamic_cast<NombreExpr*>(noeud)) {
        return llvm::ConstantInt::get(contexte, llvm::APInt(32, (int)num->valeur));
    }
    if (auto* bin = dynamic_cast<BinaireExpr*>(noeud)) {
        llvm::Value* gauche = genererExpr(bin->gauche.get());
        llvm::Value* droite = genererExpr(bin->droite.get());
        switch (bin->operateur) {
            case '+': return constructeur.CreateAdd(gauche, droite, "addtmp");
            case '-': return constructeur.CreateSub(gauche, droite, "subtmp");
            case '*': return constructeur.CreateMul(gauche, droite, "multmp");
            case '/': return constructeur.CreateSDiv(gauche, droite, "divtmp");
        }
    }
    // ...
    return nullptr;
}