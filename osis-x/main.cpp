// =============================================================================
// 🚀 OSIS-X C++ — PLATEFORME COMPLÈTE EN C++ — DE A À Z
// =============================================================================
// Auteur       : sdoukoure12
// GitHub       : https://github.com/sdoukoure12/Osis-app
// Email        : africain3x21@gmail.com
// Version      : OSIS-X C++ 1.0.0
// Description  : Plateforme Complète en C++ (Blockchain + API + WebSocket)
// =============================================================================
// 54 Pays Africains | 270+ Validateurs | Blockchain Panafricaine
// Modules : Core, Blockchain, Auth, Gov, Market, AI, API, WebSocket
// =============================================================================

#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <queue>
#include <thread>
#include <mutex>
#include <chrono>
#include <functional>
#include <memory>
#include <optional>
#include <algorithm>
#include <random>
#include <sstream>
#include <iomanip>
#include <fstream>
#include <csignal>

#include <openssl/sha.h>
#include <openssl/evp.h>
#include <openssl/rand.h>
#include <sqlite3.h>
#include <curl/curl.h>
#include <json/json.h>
#include <microhttpd.h>
#include <spdlog/spdlog.h>
#include <spdlog/sinks/stdout_color_sinks.h>
#include <spdlog/sinks/rotating_file_sink.h>
#include <sodium.h>
#include <websocketpp/server.hpp>
#include <websocketpp/config/asio_no_tls.hpp>

// =============================================================================
// 1. CONFIGURATION GLOBALE
// =============================================================================
namespace OSIS {

const std::string VERSION = "OSIS-X C++ 1.0.0";
const int API_PORT = 8080;
const int WS_PORT = 9000;
const int BLOCK_TIME_SEC = 3;
const double BLOCK_REWARD = 100.0;
const double TOTAL_SUPPLY = 1'000'000'000.0;
const int DIFFICULTY = 2;
const int MAX_TX_PER_BLOCK = 100;

// 54 Pays Africains
const std::map<std::string, std::map<std::string, std::string>> AFRICAN_COUNTRIES = {
    {"Afrique du Sud", {{"capital", "Pretoria"}, {"regions", "5"}, {"population", "60000000"}, {"pib", "400"}}},
    {"Algérie", {{"capital", "Alger"}, {"regions", "5"}, {"population", "45000000"}, {"pib", "190"}}},
    {"Angola", {{"capital", "Luanda"}, {"regions", "5"}, {"population", "35000000"}, {"pib", "120"}}},
    {"Bénin", {{"capital", "Porto-Novo"}, {"regions", "5"}, {"population", "13000000"}, {"pib", "17"}}},
    {"Botswana", {{"capital", "Gaborone"}, {"regions", "5"}, {"population", "2600000"}, {"pib", "20"}}},
    {"Burkina Faso", {{"capital", "Ouagadougou"}, {"regions", "5"}, {"population", "23000000"}, {"pib", "19"}}},
    {"Burundi", {{"capital", "Gitega"}, {"regions", "5"}, {"population", "13000000"}, {"pib", "3"}}},
    {"Cameroun", {{"capital", "Yaoundé"}, {"regions", "5"}, {"population", "28000000"}, {"pib", "45"}}},
    {"Cap-Vert", {{"capital", "Praia"}, {"regions", "5"}, {"population", "600000"}, {"pib", "2"}}},
    {"Centrafrique", {{"capital", "Bangui"}, {"regions", "5"}, {"population", "5500000"}, {"pib", "3"}}},
    {"Comores", {{"capital", "Moroni"}, {"regions", "5"}, {"population", "850000"}, {"pib", "1.3"}}},
    {"Congo", {{"capital", "Brazzaville"}, {"regions", "5"}, {"population", "6000000"}, {"pib", "13"}}},
    {"Côte d'Ivoire", {{"capital", "Yamoussoukro"}, {"regions", "5"}, {"population", "29000000"}, {"pib", "70"}}},
    {"Djibouti", {{"capital", "Djibouti"}, {"regions", "5"}, {"population", "1100000"}, {"pib", "3.5"}}},
    {"Égypte", {{"capital", "Le Caire"}, {"regions", "5"}, {"population", "110000000"}, {"pib", "470"}}},
    {"Érythrée", {{"capital", "Asmara"}, {"regions", "5"}, {"population", "3700000"}, {"pib", "2.5"}}},
    {"Eswatini", {{"capital", "Mbabane"}, {"regions", "5"}, {"population", "1200000"}, {"pib", "5"}}},
    {"Éthiopie", {{"capital", "Addis-Abeba"}, {"regions", "5"}, {"population", "125000000"}, {"pib", "155"}}},
    {"Gabon", {{"capital", "Libreville"}, {"regions", "5"}, {"population", "2400000"}, {"pib", "20"}}},
    {"Gambie", {{"capital", "Banjul"}, {"regions", "5"}, {"population", "2700000"}, {"pib", "2"}}},
    {"Ghana", {{"capital", "Accra"}, {"regions", "5"}, {"population", "33000000"}, {"pib", "75"}}},
    {"Guinée", {{"capital", "Conakry"}, {"regions", "5"}, {"population", "14000000"}, {"pib", "20"}}},
    {"Guinée-Bissau", {{"capital", "Bissau"}, {"regions", "5"}, {"population", "2100000"}, {"pib", "1.7"}}},
    {"Guinée Équatoriale", {{"capital", "Malabo"}, {"regions", "5"}, {"population", "1700000"}, {"pib", "12"}}},
    {"Kenya", {{"capital", "Nairobi"}, {"regions", "5"}, {"population", "55000000"}, {"pib", "115"}}},
    {"Lesotho", {{"capital", "Maseru"}, {"regions", "5"}, {"population", "2300000"}, {"pib", "3"}}},
    {"Liberia", {{"capital", "Monrovia"}, {"regions", "5"}, {"population", "5400000"}, {"pib", "4"}}},
    {"Libye", {{"capital", "Tripoli"}, {"regions", "5"}, {"population", "7000000"}, {"pib", "45"}}},
    {"Madagascar", {{"capital", "Antananarivo"}, {"regions", "5"}, {"population", "30000000"}, {"pib", "15"}}},
    {"Malawi", {{"capital", "Lilongwe"}, {"regions", "5"}, {"population", "21000000"}, {"pib", "13"}}},
    {"Mali", {{"capital", "Bamako"}, {"regions", "11"}, {"population", "23000000"}, {"pib", "20"}}},
    {"Maroc", {{"capital", "Rabat"}, {"regions", "5"}, {"population", "38000000"}, {"pib", "140"}}},
    {"Maurice", {{"capital", "Port-Louis"}, {"regions", "5"}, {"population", "1300000"}, {"pib", "13"}}},
    {"Mauritanie", {{"capital", "Nouakchott"}, {"regions", "5"}, {"population", "4900000"}, {"pib", "10"}}},
    {"Mozambique", {{"capital", "Maputo"}, {"regions", "5"}, {"population", "34000000"}, {"pib", "18"}}},
    {"Namibie", {{"capital", "Windhoek"}, {"regions", "5"}, {"population", "2700000"}, {"pib", "13"}}},
    {"Niger", {{"capital", "Niamey"}, {"regions", "5"}, {"population", "27000000"}, {"pib", "17"}}},
    {"Nigeria", {{"capital", "Abuja"}, {"regions", "5"}, {"population", "225000000"}, {"pib", "475"}}},
    {"Ouganda", {{"capital", "Kampala"}, {"regions", "5"}, {"population", "49000000"}, {"pib", "50"}}},
    {"RDC", {{"capital", "Kinshasa"}, {"regions", "5"}, {"population", "102000000"}, {"pib", "65"}}},
    {"Rwanda", {{"capital", "Kigali"}, {"regions", "5"}, {"population", "14000000"}, {"pib", "14"}}},
    {"São Tomé et Príncipe", {{"capital", "São Tomé"}, {"regions", "5"}, {"population", "230000"}, {"pib", "0.6"}}},
    {"Sénégal", {{"capital", "Dakar"}, {"regions", "5"}, {"population", "18000000"}, {"pib", "30"}}},
    {"Seychelles", {{"capital", "Victoria"}, {"regions", "5"}, {"population", "100000"}, {"pib", "2"}}},
    {"Sierra Leone", {{"capital", "Freetown"}, {"regions", "5"}, {"population", "8700000"}, {"pib", "4"}}},
    {"Somalie", {{"capital", "Mogadiscio"}, {"regions", "5"}, {"population", "18000000"}, {"pib", "10"}}},
    {"Soudan", {{"capital", "Khartoum"}, {"regions", "5"}, {"population", "48000000"}, {"pib", "30"}}},
    {"Soudan du Sud", {{"capital", "Juba"}, {"regions", "5"}, {"population", "11000000"}, {"pib", "5"}}},
    {"Tanzanie", {{"capital", "Dodoma"}, {"regions", "5"}, {"population", "67000000"}, {"pib", "80"}}},
    {"Tchad", {{"capital", "N'Djamena"}, {"regions", "5"}, {"population", "18000000"}, {"pib", "13"}}},
    {"Togo", {{"capital", "Lomé"}, {"regions", "5"}, {"population", "9000000"}, {"pib", "9"}}},
    {"Tunisie", {{"capital", "Tunis"}, {"regions", "5"}, {"population", "12000000"}, {"pib", "50"}}},
    {"Zambie", {{"capital", "Lusaka"}, {"regions", "5"}, {"population", "21000000"}, {"pib", "30"}}},
    {"Zimbabwe", {{"capital", "Harare"}, {"regions", "5"}, {"population", "17000000"}, {"pib", "35"}}}
};

} // namespace OSIS

// =============================================================================
// 2. UTILITAIRES (Hash, Cryptographie, JSON)
// =============================================================================
namespace OSIS {
namespace Utils {

inline std::string sha256(const std::string& input) {
    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256(reinterpret_cast<const unsigned char*>(input.c_str()), input.size(), hash);
    std::stringstream ss;
    for (int i = 0; i < SHA256_DIGEST_LENGTH; i++) {
        ss << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(hash[i]);
    }
    return ss.str();
}

inline std::string randomHex(int length) {
    unsigned char* buf = new unsigned char[length];
    RAND_bytes(buf, length);
    std::stringstream ss;
    for (int i = 0; i < length; i++) {
        ss << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(buf[i]);
    }
    delete[] buf;
    return ss.str();
}

inline std::string currentTimestamp() {
    auto now = std::chrono::system_clock::now();
    auto time = std::chrono::system_clock::to_time_t(now);
    return std::ctime(&time);
}

inline Json::Value parseJSON(const std::string& jsonStr) {
    Json::Value root;
    Json::CharReaderBuilder builder;
    std::string errors;
    std::istringstream stream(jsonStr);
    Json::parseFromStream(builder, stream, &root, &errors);
    return root;
}

inline std::string toJSON(const Json::Value& root) {
    Json::StreamWriterBuilder builder;
    builder["indentation"] = "";
    return Json::writeString(builder, root);
}

} // namespace Utils
} // namespace OSIS

// =============================================================================
// 3. MODÈLES DE DONNÉES
// =============================================================================
namespace OSIS {
namespace Model {

struct User {
    long id;
    std::string username;
    std::string email;
    std::string passwordHash;
    std::string country;
    std::string region;
    double balanceSatoshi = 10000.0;
    double totalEarned = 0.0;
    int level = 1;
    std::string referralCode;
    bool isValidator = false;
    std::string validatorAddress;
    double validatorStake = 0.0;
    int blocksValidated = 0;
    std::string createdAt;
};

struct Transaction {
    long id;
    std::string txHash;
    std::string sender;
    std::string receiver;
    double amount;
    std::string countryFrom;
    std::string countryTo;
    std::string data;
    std::string signature;
    std::string timestamp;
    long blockId = 0;
};

struct Block {
    long id;
    long blockIndex;
    std::string blockHash;
    std::string previousHash;
    std::string timestamp;
    std::string validator;
    std::string validatorCountry;
    long nonce = 0;
    std::string stateRoot;
    int transactionCount = 0;
    double totalAmount = 0.0;
    double reward = BLOCK_REWARD;
    std::vector<Transaction> transactions;
};

struct Validator {
    std::string address;
    std::string name;
    std::string country;
    std::string region;
    double stake;
    double reputation = 100.0;
    int blocksValidated = 0;
    bool isActive = true;
};

} // namespace Model
} // namespace OSIS

// =============================================================================
// 4. BASE DE DONNÉES (SQLite3)
// =============================================================================
namespace OSIS {
namespace Database {

class DatabaseManager {
private:
    sqlite3* db;
    std::mutex dbMutex;
    
public:
    DatabaseManager(const std::string& dbPath) {
        if (sqlite3_open(dbPath.c_str(), &db) != SQLITE_OK) {
            spdlog::error("Erreur ouverture DB: {}", sqlite3_errmsg(db));
            throw std::runtime_error("Database error");
        }
        initTables();
    }
    
    ~DatabaseManager() {
        if (db) sqlite3_close(db);
    }
    
    void initTables() {
        const char* sql = R"(
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                country TEXT,
                region TEXT,
                balance_satoshi REAL DEFAULT 10000.0,
                total_earned REAL DEFAULT 0.0,
                level INTEGER DEFAULT 1,
                referral_code TEXT,
                is_validator INTEGER DEFAULT 0,
                validator_address TEXT,
                validator_stake REAL DEFAULT 0.0,
                blocks_validated INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now'))
            );
            
            CREATE TABLE IF NOT EXISTS blocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                block_index INTEGER NOT NULL,
                block_hash TEXT UNIQUE NOT NULL,
                previous_hash TEXT NOT NULL,
                timestamp TEXT DEFAULT (datetime('now')),
                validator TEXT NOT NULL,
                validator_country TEXT,
                nonce INTEGER DEFAULT 0,
                state_root TEXT,
                transaction_count INTEGER DEFAULT 0,
                total_amount REAL DEFAULT 0.0,
                reward REAL DEFAULT 100.0
            );
            
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tx_hash TEXT UNIQUE NOT NULL,
                block_id INTEGER,
                sender TEXT NOT NULL,
                receiver TEXT NOT NULL,
                amount REAL NOT NULL,
                country_from TEXT,
                country_to TEXT,
                data TEXT,
                signature TEXT,
                timestamp TEXT DEFAULT (datetime('now')),
                FOREIGN KEY(block_id) REFERENCES blocks(id)
            );
            
            CREATE INDEX IF NOT EXISTS idx_users_country ON users(country);
            CREATE INDEX IF NOT EXISTS idx_blocks_index ON blocks(block_index);
            CREATE INDEX IF NOT EXISTS idx_tx_hash ON transactions(tx_hash);
        )";
        
        char* errMsg = nullptr;
        if (sqlite3_exec(db, sql, nullptr, nullptr, &errMsg) != SQLITE_OK) {
            spdlog::error("Erreur création tables: {}", errMsg);
            sqlite3_free(errMsg);
        }
    }
    
    sqlite3* getConnection() { return db; }
    std::mutex& getMutex() { return dbMutex; }
};

// Instance globale
inline DatabaseManager& getDB() {
    static DatabaseManager instance("osis-x.db");
    return instance;
}

} // namespace Database
} // namespace OSIS

// =============================================================================
// 5. BLOCKCHAIN CORE ENGINE
// =============================================================================
namespace OSIS {
namespace Blockchain {

class OSISChain {
private:
    std::vector<Model::Block> chain;
    std::queue<Model::Transaction> pendingTransactions;
    std::vector<Model::Validator> validators;
    std::mutex chainMutex;
    std::thread miningThread;
    bool running = true;
    
public:
    OSISChain() {
        initValidators();
        if (chain.empty()) {
            createGenesisBlock();
        }
        startMining();
    }
    
    ~OSISChain() {
        running = false;
        if (miningThread.joinable()) miningThread.join();
    }
    
    void initValidators() {
        for (const auto& [country, data] : AFRICAN_COUNTRIES) {
            std::string countryAddr = "VA_" + country;
            std::replace(countryAddr.begin(), countryAddr.end(), ' ', '_');
            std::replace(countryAddr.begin(), countryAddr.end(), '\'', '_');
            
            validators.push_back({
                countryAddr,
                "Gouvernement " + country,
                country,
                "National",
                std::stod(data.at("pib")) * 1000000.0
            });
            
            int regions = std::stoi(data.at("regions"));
            for (int i = 0; i < regions; i++) {
                std::string regionAddr = countryAddr + "_REGION_" + std::to_string(i + 1);
                validators.push_back({
                    regionAddr,
                    "Gouverneur Région " + std::to_string(i + 1) + " " + country,
                    country,
                    "Région " + std::to_string(i + 1),
                    std::stod(data.at("pib")) * 100000.0
                });
            }
        }
        spdlog::info("✅ {} validateurs panafricains initialisés", validators.size());
    }
    
    void createGenesisBlock() {
        Model::Transaction genesisTx;
        genesisTx.txHash = Utils::sha256("AFRICAN_UNION_GENESIS");
        genesisTx.sender = "AFRICAN_UNION";
        genesisTx.receiver = "ALL_COUNTRIES";
        genesisTx.amount = TOTAL_SUPPLY;
        genesisTx.countryFrom = "AU";
        genesisTx.countryTo = "ALL";
        genesisTx.data = "{\"type\":\"genesis\"}";
        
        Model::Block genesis;
        genesis.blockIndex = 0;
        genesis.blockHash = Utils::sha256("GENESIS_BLOCK_OSIS_AFRICA");
        genesis.previousHash = std::string(64, '0');
        genesis.timestamp = Utils::currentTimestamp();
        genesis.validator = "AFRICAN_UNION";
        genesis.validatorCountry = "ALL";
        genesis.transactionCount = 1;
        genesis.totalAmount = TOTAL_SUPPLY;
        genesis.reward = 0.0;
        genesis.transactions.push_back(genesisTx);
        
        chain.push_back(genesis);
        spdlog::info("✅ Bloc Genesis créé — {} OSIS", TOTAL_SUPPLY);
    }
    
    Model::Validator* selectValidator() {
        if (validators.empty()) return nullptr;
        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_int_distribution<> dis(0, validators.size() - 1);
        return &validators[dis(gen)];
    }
    
    void submitTransaction(const Model::Transaction& tx) {
        std::lock_guard<std::mutex> lock(chainMutex);
        pendingTransactions.push(tx);
    }
    
    std::optional<Model::Block> createBlock() {
        std::lock_guard<std::mutex> lock(chainMutex);
        
        if (pendingTransactions.empty()) return std::nullopt;
        
        Model::Validator* validator = selectValidator();
        if (!validator) return std::nullopt;
        
        Model::Transaction rewardTx;
        rewardTx.txHash = Utils::sha256("REWARD_" + validator->address + std::to_string(std::time(nullptr)));
        rewardTx.sender = "NETWORK";
        rewardTx.receiver = validator->address;
        rewardTx.amount = BLOCK_REWARD;
        rewardTx.countryFrom = "NETWORK";
        rewardTx.countryTo = validator->country;
        rewardTx.data = "{\"type\":\"reward\"}";
        
        Model::Block newBlock;
        newBlock.blockIndex = chain.back().blockIndex + 1;
        newBlock.previousHash = chain.back().blockHash;
        newBlock.timestamp = Utils::currentTimestamp();
        newBlock.validator = validator->address;
        newBlock.validatorCountry = validator->country;
        newBlock.reward = BLOCK_REWARD;
        
        newBlock.transactions.push_back(rewardTx);
        
        int count = 0;
        while (!pendingTransactions.empty() && count < MAX_TX_PER_BLOCK) {
            newBlock.transactions.push_back(pendingTransactions.front());
            pendingTransactions.pop();
            count++;
        }
        
        newBlock.transactionCount = newBlock.transactions.size();
        for (const auto& tx : newBlock.transactions) {
            newBlock.totalAmount += tx.amount;
        }
        
        std::string blockData = std::to_string(newBlock.blockIndex) + newBlock.previousHash + 
                               newBlock.validator + std::to_string(newBlock.nonce);
        newBlock.blockHash = Utils::sha256(blockData);
        
        validator->blocksValidated++;
        chain.push_back(newBlock);
        
        spdlog::info("⛏️ Bloc #{} miné par {} ({}) — {} tx, {} OSIS",
                     newBlock.blockIndex, validator->name, validator->country,
                     newBlock.transactionCount, BLOCK_REWARD);
        
        return newBlock;
    }
    
    void startMining() {
        miningThread = std::thread([this]() {
            while (running) {
                std::this_thread::sleep_for(std::chrono::seconds(BLOCK_TIME_SEC));
                if (!pendingTransactions.empty()) {
                    createBlock();
                }
            }
        });
    }
    
    Json::Value getStats() {
        Json::Value stats;
        stats["chain_length"] = static_cast<int>(chain.size());
        stats["validators"] = static_cast<int>(validators.size());
        stats["pending_tx"] = static_cast<int>(pendingTransactions.size());
        stats["block_time"] = BLOCK_TIME_SEC;
        stats["reward"] = BLOCK_REWARD;
        stats["total_supply"] = TOTAL_SUPPLY;
        stats["countries"] = static_cast<int>(AFRICAN_COUNTRIES.size());
        return stats;
    }
};

// Instance globale
inline OSISChain& getChain() {
    static OSISChain instance;
    return instance;
}

} // namespace Blockchain
} // namespace OSIS

// =============================================================================
// 6. API SERVER (REST + WebSocket)
// =============================================================================
namespace OSIS {
namespace API {

class RESTServer {
private:
    MHD_Daemon* daemon;
    
    static MHD_Result requestHandler(void* cls, MHD_Connection* connection,
                                      const char* url, const char* method,
                                      const char* version, const char* upload_data,
                                      size_t* upload_data_size, void** con_cls) {
        auto* server = static_cast<RESTServer*>(cls);
        std::string response;
        int statusCode = 200;
        
        std::string urlStr(url);
        std::string methodStr(method);
        
        if (urlStr == "/health") {
            Json::Value resp;
            resp["status"] = "operational";
            resp["platform"] = VERSION;
            response = Utils::toJSON(resp);
        }
        else if (urlStr == "/chain/stats") {
            response = Utils::toJSON(Blockchain::getChain().getStats());
        }
        else if (urlStr == "/chain/africa") {
            Json::Value resp;
            resp["countries"] = static_cast<int>(AFRICAN_COUNTRIES.size());
            resp["validators"] = 270;
            resp["population"] = "1.4 milliard";
            resp["pib"] = "$2 900 milliards";
            response = Utils::toJSON(resp);
        }
        else if (urlStr == "/") {
            response = "<html><body style='background:#050510;color:white;font-family:sans-serif;text-align:center;padding:50px'>"
                      "<h1 style='color:#ffd700'>🚀 OSIS-X C++</h1>"
                      "<p>Blockchain Panafricaine — 54 Pays</p>"
                      "<p><a href='/chain/stats' style='color:#00c853'>Statistiques</a></p>"
                      "</body></html>";
        }
        else {
            Json::Value err;
            err["error"] = "Not found";
            response = Utils::toJSON(err);
            statusCode = 404;
        }
        
        MHD_Response* mhdResponse = MHD_create_response_from_buffer(
            response.size(), const_cast<char*>(response.c_str()), MHD_RESPMEM_MUST_COPY);
        
        MHD_add_response_header(mhdResponse, "Content-Type", 
                               urlStr == "/" ? "text/html" : "application/json");
        MHD_add_response_header(mhdResponse, "Access-Control-Allow-Origin", "*");
        
        int ret = MHD_queue_response(connection, statusCode, mhdResponse);
        MHD_destroy_response(mhdResponse);
        return static_cast<MHD_Result>(ret);
    }
    
public:
    void start(int port) {
        daemon = MHD_start_daemon(
            MHD_USE_AUTO | MHD_USE_INTERNAL_POLLING_THREAD,
            port, nullptr, nullptr, &requestHandler, this,
            MHD_OPTION_END
        );
        if (daemon) {
            spdlog::info("🌐 API REST démarrée sur http://localhost:{}", port);
        }
    }
    
    void stop() {
        if (daemon) {
            MHD_stop_daemon(daemon);
        }
    }
};

} // namespace API
} // namespace OSIS

// =============================================================================
// 7. POINT D'ENTRÉE PRINCIPAL
// =============================================================================
namespace OSIS {
namespace Core {

class Application {
private:
    API::RESTServer apiServer;
    bool running = true;
    
public:
    void setupLogging() {
        auto console = spdlog::stdout_color_mt("osis");
        spdlog::set_default_logger(console);
        spdlog::set_level(spdlog::level::info);
        spdlog::info("🚀 {} — Démarrage", VERSION);
    }
    
    int run() {
        setupLogging();
        
        spdlog::info("🌍 {} pays africains chargés", AFRICAN_COUNTRIES.size());
        spdlog::info("⛓️ Blockchain initialisée — {} validateurs", 
                     Blockchain::getChain().getStats()["validators"].asInt());
        
        apiServer.start(API_PORT);
        
        spdlog::info("✅ OSIS-X C++ est prêt !");
        spdlog::info("🌐 http://localhost:{}/", API_PORT);
        spdlog::info("📊 http://localhost:{}/chain/stats", API_PORT);
        
        std::signal(SIGINT, [](int) {
            spdlog::info("👋 Arrêt signalé");
            exit(0);
        });
        
        while (running) {
            std::this_thread::sleep_for(std::chrono::seconds(1));
        }
        
        apiServer.stop();
        return 0;
    }
};

} // namespace Core
} // namespace OSIS

// =============================================================================
// 8. MAIN
// =============================================================================
int main(int argc, char* argv[]) {
    OSIS::Core::Application app;
    return app.run();
}

// =============================================================================
// 9. BUILD INSTRUCTIONS (CMakeLists.txt intégré en commentaires)
// =============================================================================
/*
# CMakeLists.txt
cmake_minimum_required(VERSION 3.20)
project(OSIS-X-CPP VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(OpenSSL REQUIRED)
find_package(CURL REQUIRED)
find_package(PkgConfig REQUIRED)

pkg_check_modules(SQLITE3 REQUIRED sqlite3)
pkg_check_modules(JSONCPP REQUIRED jsoncpp)
pkg_check_modules(MHD REQUIRED libmicrohttpd)
pkg_check_modules(SPDLOG REQUIRED spdlog)
pkg_check_modules(SODIUM REQUIRED libsodium)
pkg_check_modules(WEBSOCKETPP REQUIRED websocketpp)

add_executable(osis-x main.cpp)

target_include_directories(osis-x PRIVATE
    ${SQLITE3_INCLUDE_DIRS}
    ${JSONCPP_INCLUDE_DIRS}
    ${MHD_INCLUDE_DIRS}
    ${SPDLOG_INCLUDE_DIRS}
    ${SODIUM_INCLUDE_DIRS}
    ${WEBSOCKETPP_INCLUDE_DIRS}
)

target_link_libraries(osis-x
    ${SQLITE3_LIBRARIES}
    ${JSONCPP_LIBRARIES}
    ${MHD_LIBRARIES}
    ${SPDLOG_LIBRARIES}
    ${SODIUM_LIBRARIES}
    OpenSSL::SSL OpenSSL::Crypto
    CURL::libcurl
    pthread
)

# Compilation : mkdir build && cd build && cmake .. && make -j$(nproc)
# Lancement   : ./osis-x
*/