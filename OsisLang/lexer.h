// lexer.h
#pragma once
#include <string>
#include <vector>
#include <unordered_map>

enum class TokenType {
    // Mots-clés
    FONCTION, SI, SINON, TANTQUE, POUR, RETOURNER, AFFICHER,
    // Types primitifs
    TYPE_INT, TYPE_STR, TYPE_BOOL, TYPE_FLOAT,
    // Littéraux
    IDENTIFIER, NOMBRE, CHAINE,
    // Opérateurs
    PLUS, MOINS, MUL, DIV, ASSIGN, EGAL, DIFFERENT, INF, SUP, INF_EGAL, SUP_EGAL,
    // Ponctuation
    PARENTHESE_OUVR, PARENTHESE_FERM, ACCOLADE_OUVR, ACCOLADE_FERM, DEUX_POINTS, VIRGULE, FLECHE,
    // Fin de fichier
    FIN_FICHIER
};

struct Token {
    TokenType type;
    std::string valeur;
    int ligne;
    int colonne;
};

class Lexer {
public:
    explicit Lexer(const std::string& source);
    std::vector<Token> analyser();

private:
    std::string source;
    size_t position = 0;
    int ligne = 1;
    int colonne = 1;

    char sommet();
    char avancer();
    void ignorerEspaces();
    Token lireIdentifiantOuMotCle();
    Token lireNombre();
    Token lireChaine();
};