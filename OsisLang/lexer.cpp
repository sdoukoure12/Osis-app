// lexer.cpp (extrait)
std::vector<Token> Lexer::analyser() {
    std::vector<Token> tokens;
    while (position < source.size()) {
        ignorerEspaces();
        if (position >= source.size()) break;

        char c = sommet();
        if (isalpha(c) || c == '_') {
            tokens.push_back(lireIdentifiantOuMotCle());
        } else if (isdigit(c)) {
            tokens.push_back(lireNombre());
        } else if (c == '"') {
            tokens.push_back(lireChaine());
        } else {
            // Gestion des opérateurs et de la ponctuation
            switch (c) {
                case '+': tokens.push_back({TokenType::PLUS, "+", ligne, colonne}); avancer(); break;
                case '-':
                    if (source[position + 1] == '>') {
                        tokens.push_back({TokenType::FLECHE, "->", ligne, colonne});
                        avancer(); avancer();
                    } else {
                        tokens.push_back({TokenType::MOINS, "-", ligne, colonne});
                        avancer();
                    }
                    break;
                // ... autres opérateurs
                default:
                    throw std::runtime_error("Caractère inattendu : " + std::string(1, c));
            }
        }
    }
    tokens.push_back({TokenType::FIN_FICHIER, "", ligne, colonne});
    return tokens;
}