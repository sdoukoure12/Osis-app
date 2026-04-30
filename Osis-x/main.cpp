// =============================================================================
// OSIS-X C++ — Plateforme Blockchain Panafricaine Complète
// Auteur       : sdoukoure12
// GitHub       : https://github.com/sdoukoure12/Osis-app
// Email        : africain3x21@gmail.com
// Version      : OSIS-X C++ Ultimate 1.0.0
// Description  : Blockchain, API REST, Auth JWT, Dashboard, Récompenses,
//                Dictionnaire, Intentions, Jardins, Dons, Gouvernance.
// Compilation  : g++ -std=c++20 -O2 -o osis-x complete.cpp -lsqlite3 -ljsoncpp -lmicrohttpd -lspdlog -lsodium -lssl -lcrypto -lcurl -lpthread
// =============================================================================

#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <queue>
#include <thread>
#include <mutex>
#include <chrono>
#include <memory>
#include <optional>
#include <algorithm>
#include <random>
#include <sstream>
#include <iomanip>
#include <csignal>
#include <fstream>
#include <functional>
#include <unordered_map>

#include <openssl/sha.h>
#include <openssl/evp.h>
#include <openssl/hmac.h>
#include <openssl/rand.h>
#include <sqlite3.h>
#include <curl/curl.h>
#include <json/json.h>
#include <microhttpd.h>
#include <spdlog/spdlog.h>
#include <spdlog/sinks/stdout_color_sinks.h>
#include <sodium.h>

namespace OSIS {

const std::string VERSION = "OSIS-X C++ Ultimate 1.0.0";
const int API_PORT = 8080;
const int BLOCK_TIME_SEC = 3;
const double BLOCK_REWARD = 100.0;
const double TOTAL_SUPPLY = 1'000'000'000.0;
const int MAX_TX_PER_BLOCK = 100;

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

// =============================================================================
// Utilitaires
// =============================================================================
namespace Utils {
    inline std::string sha256(const std::string& input) {
        unsigned char hash[SHA256_DIGEST_LENGTH];
        SHA256(reinterpret_cast<const unsigned char*>(input.c_str()), input.size(), hash);
        std::stringstream ss;
        for (int i = 0; i < SHA256_DIGEST_LENGTH; ++i)
            ss << std::hex << std::setw(2) << std::setfill('0') << (int)hash[i];
        return ss.str();
    }
    inline std::string randomHex(int len) {
        unsigned char buf[len];
        RAND_bytes(buf, len);
        std::stringstream ss;
        for (int i = 0; i < len; ++i) ss << std::hex << std::setw(2) << std::setfill('0') << (int)buf[i];
        return ss.str();
    }
    inline std::string currentTimestamp() {
        auto now = std::chrono::system_clock::now();
        auto time = std::chrono::system_clock::to_time_t(now);
        return std::ctime(&time);
    }
    inline std::string base64Encode(const std::string& input) {
        static const char* chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
        std::string out;
        int val = 0, valb = -6;
        for (unsigned char c : input) { val = (val << 8) + c; valb += 8; while (valb >= 0) { out.push_back(chars[(val >> valb) & 0x3F]); valb -= 6; } }
        if (valb > -6) out.push_back(chars[((val << 8) >> (valb + 8)) & 0x3F]);
        while (out.size() % 4) out.push_back('=');
        return out;
    }
    inline std::string jsonToString(const Json::Value& v) { Json::StreamWriterBuilder b; b["indentation"] = ""; return Json::writeString(b, v); }
    inline Json::Value parseJson(const std::string& s) { Json::Value v; Json::CharReaderBuilder b; std::string e; std::istringstream ss(s); Json::parseFromStream(b, ss, &v, &e); return v; }
}

// =============================================================================
// Base de données
// =============================================================================
namespace DB {
    class Database {
        sqlite3* db = nullptr;
        std::mutex m;
    public:
        Database(const std::string& path) { sqlite3_open(path.c_str(), &db); init(); }
        ~Database() { if (db) sqlite3_close(db); }
        sqlite3* get() { return db; }
        std::mutex& mutex() { return m; }
    private:
        void init() {
            const char* sql = R"(
                CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT, email TEXT, country TEXT, balance REAL DEFAULT 10000, total_earned REAL DEFAULT 0, level INTEGER DEFAULT 1, token TEXT, validator_address TEXT, is_validator INTEGER DEFAULT 0);
                CREATE TABLE IF NOT EXISTS blocks(id INTEGER PRIMARY KEY, block_index INTEGER, block_hash TEXT, previous_hash TEXT, validator TEXT, timestamp TEXT);
                CREATE TABLE IF NOT EXISTS transactions(id INTEGER PRIMARY KEY, tx_hash TEXT, block_id INTEGER, sender TEXT, receiver TEXT, amount REAL, timestamp TEXT);
                CREATE TABLE IF NOT EXISTS intentions(id INTEGER PRIMARY KEY, title TEXT, description TEXT, category TEXT, value REAL DEFAULT 10000);
                CREATE TABLE IF NOT EXISTS gardens(id INTEGER PRIMARY KEY, name TEXT, value REAL DEFAULT 100, growth REAL DEFAULT 0.05);
                CREATE TABLE IF NOT EXISTS dictionary(id INTEGER PRIMARY KEY, word TEXT, definition TEXT, language TEXT);
                CREATE TABLE IF NOT EXISTS donations(id INTEGER PRIMARY KEY, donor TEXT, campaign TEXT, amount REAL);
            )";
            sqlite3_exec(db, sql, nullptr, nullptr, nullptr);
        }
    };
    inline Database& getDB() { static Database db("osis.db"); return db; }
}

// =============================================================================
// Authentification JWT
// =============================================================================
namespace Auth {
    const std::string SECRET = "osis-jwt-secret-key-change-in-production";
    std::string createJWT(int userId) {
        Json::Value header, payload;
        header["alg"] = "HS256"; header["typ"] = "JWT";
        payload["sub"] = userId;
        payload["iat"] = std::time(nullptr);
        payload["exp"] = std::time(nullptr) + 3600;
        std::string h = Utils::base64Encode(Utils::jsonToString(header));
        std::string p = Utils::base64Encode(Utils::jsonToString(payload));
        std::string toSign = h + "." + p;
        unsigned char sig[EVP_MAX_MD_SIZE];
        unsigned int sigLen;
        HMAC(EVP_sha256(), SECRET.c_str(), SECRET.size(), (unsigned char*)toSign.c_str(), toSign.size(), sig, &sigLen);
        return toSign + "." + Utils::base64Encode(std::string((char*)sig, sigLen));
    }
    int verifyJWT(const std::string& token) {
        auto d1 = token.find('.');
        auto d2 = token.find('.', d1+1);
        if (d1 == std::string::npos || d2 == std::string::npos) return -1;
        std::string toSign = token.substr(0, d2);
        unsigned char sig[EVP_MAX_MD_SIZE];
        unsigned int sigLen;
        HMAC(EVP_sha256(), SECRET.c_str(), SECRET.size(), (unsigned char*)toSign.c_str(), toSign.size(), sig, &sigLen);
        std::string expectedSig((char*)sig, sigLen);
        std::string providedSig = token.substr(d2+1);
        if (Utils::base64Encode(expectedSig) != providedSig) return -1;
        Json::Value payload = Utils::parseJson(token.substr(d1+1, d2-d1-1));
        return payload["sub"].asInt();
    }
}

// =============================================================================
// Blockchain
// =============================================================================
namespace Chain {
    using Model::Transaction;
    using Model::Block;
    struct Validator { std::string addr, name, country; double stake; int blocks = 0; };
    class OSISChain {
        std::vector<Block> chain;
        std::queue<Transaction> pending;
        std::vector<Validator> validators;
        std::mutex mtx;
        std::thread miner;
        bool running = true;
    public:
        OSISChain() {
            for (auto& [c, d] : AFRICAN_COUNTRIES) {
                std::string a = "VA_" + c; std::replace(a.begin(), a.end(), ' ', '_');
                validators.push_back({a, "Gouv. "+c, c, std::stod(d.at("pib"))*1e6});
                for (int i=0; i<std::stoi(d.at("regions")); ++i)
                    validators.push_back({a+"_R"+std::to_string(i+1), "Gouv. R"+std::to_string(i+1)+" "+c, c, std::stod(d.at("pib"))*1e5});
            }
            createGenesis();
            miner = std::thread([this]{ while(running) { std::this_thread::sleep_for(std::chrono::seconds(BLOCK_TIME_SEC)); if(!pending.empty()) createBlock(); } });
        }
        ~OSISChain() { running=false; if(miner.joinable()) miner.join(); }
        void createGenesis() {
            Transaction tx; tx.txHash = Utils::sha256("GENESIS"); tx.sender="AU"; tx.receiver="ALL"; tx.amount=TOTAL_SUPPLY;
            Block b; b.index=0; b.hash=Utils::sha256("GENESIS_BLOCK"); b.prevHash=std::string(64,'0'); b.validator="AU"; b.txs.push_back(tx);
            chain.push_back(b);
        }
        void submitTx(const Transaction& tx) { std::lock_guard l(mtx); pending.push(tx); }
        std::optional<Block> createBlock() {
            std::lock_guard l(mtx);
            if(pending.empty() || validators.empty()) return {};
            Validator& v = validators[rand()%validators.size()];
            Transaction reward; reward.txHash=Utils::sha256("REWARD"+std::to_string(time(0))); reward.sender="NETWORK"; reward.receiver=v.addr; reward.amount=BLOCK_REWARD;
            Block b; b.index=chain.back().index+1; b.prevHash=chain.back().hash; b.validator=v.addr; b.txs.push_back(reward);
            int cnt=0; while(!pending.empty() && cnt++<MAX_TX_PER_BLOCK) { b.txs.push_back(pending.front()); pending.pop(); }
            b.hash=Utils::sha256(std::to_string(b.index)+b.prevHash+b.validator);
            v.blocks++; chain.push_back(b);
            return b;
        }
        Json::Value stats() { Json::Value s; s["blocks"]=(int)chain.size(); s["validators"]=(int)validators.size(); s["pending"]=(int)pending.size(); return s; }
    };
    inline OSISChain& get() { static OSISChain c; return c; }
}

// =============================================================================
// API REST
// =============================================================================
namespace API {
    class Server {
        MHD_Daemon* d = nullptr;
        static MHD_Result callback(void* cls, MHD_Connection* c, const char* url, const char* method, const char*, const char* up, size_t* upSize, void** ptr) {
            auto* s = static_cast<Server*>(cls);
            std::string body, path(url), meth(method);
            if (*ptr == nullptr) { *ptr = new std::string; return MHD_YES; }
            auto* b = static_cast<std::string*>(*ptr);
            if (*upSize > 0) { b->append(up, *upSize); *upSize = 0; return MHD_YES; }
            body = *b; delete b; *ptr = nullptr;
            Json::Value resp; int code = 200;
            auto& db = DB::getDB();
            std::lock_guard l(db.mutex());
            if (path == "/") {
                resp["message"] = "OSIS-X C++ Ultimate"; resp["version"] = VERSION;
            } else if (path == "/auth/register" && meth == "POST") {
                Json::Value req = Utils::parseJson(body);
                std::string u = req["username"].asString(), p = req["password"].asString();
                sqlite3_stmt* stmt;
                sqlite3_prepare_v2(db.get(), "INSERT INTO users(username,password_hash,email,country,balance) VALUES(?,?,?,?,10000)", -1, &stmt, nullptr);
                sqlite3_bind_text(stmt,1,u.c_str(),-1,SQLITE_STATIC); sqlite3_bind_text(stmt,2,Utils::sha256(p).c_str(),-1,SQLITE_STATIC);
                sqlite3_bind_text(stmt,3,req["email"].asString().c_str(),-1,SQLITE_STATIC); sqlite3_bind_text(stmt,4,req.get("country","Mali").asString().c_str(),-1,SQLITE_STATIC);
                if (sqlite3_step(stmt) == SQLITE_DONE) { int uid = sqlite3_last_insert_rowid(db.get()); resp["token"] = Auth::createJWT(uid); resp["userId"] = uid; }
                else { resp["error"] = "Existe déjà"; code = 400; }
                sqlite3_finalize(stmt);
            } else if (path == "/auth/login" && meth == "POST") {
                Json::Value req = Utils::parseJson(body);
                sqlite3_stmt* stmt;
                sqlite3_prepare_v2(db.get(), "SELECT id FROM users WHERE username=? AND password_hash=?", -1, &stmt, nullptr);
                sqlite3_bind_text(stmt,1,req["username"].asString().c_str(),-1,SQLITE_STATIC); sqlite3_bind_text(stmt,2,Utils::sha256(req["password"].asString()).c_str(),-1,SQLITE_STATIC);
                if (sqlite3_step(stmt)==SQLITE_ROW) { int uid = sqlite3_column_int(stmt,0); resp["token"]=Auth::createJWT(uid); }
                else { resp["error"]="Identifiants invalides"; code=401; }
                sqlite3_finalize(stmt);
            } else if (path == "/earn" && meth == "POST") {
                Json::Value req = Utils::parseJson(body);
                int uid = req["userId"].asInt(); double amt = req["amount"].asDouble();
                sqlite3_exec(db.get(), ("UPDATE users SET balance=balance+"+std::to_string(amt)+", total_earned=total_earned+"+std::to_string(amt)+" WHERE id="+std::to_string(uid)).c_str(), nullptr, nullptr, nullptr);
                resp["earned"] = amt; resp["balance"] = 0;
            } else if (path == "/donate" && meth == "POST") {
                Json::Value req = Utils::parseJson(body);
                sqlite3_stmt* stmt;
                sqlite3_prepare_v2(db.get(), "INSERT INTO donations(donor,campaign,amount) VALUES(?,?,?)", -1, &stmt, nullptr);
                sqlite3_bind_text(stmt,1,req["donor"].asString().c_str(),-1,SQLITE_STATIC); sqlite3_bind_text(stmt,2,req["campaign"].asString().c_str(),-1,SQLITE_STATIC);
                sqlite3_bind_double(stmt,3,req["amount"].asDouble()); sqlite3_step(stmt); sqlite3_finalize(stmt);
                resp["message"] = "Merci pour votre don !";
            } else if (path == "/intention/create" && meth == "POST") {
                Json::Value req = Utils::parseJson(body);
                sqlite3_stmt* stmt;
                sqlite3_prepare_v2(db.get(), "INSERT INTO intentions(title,description,category,value) VALUES(?,?,?,10000)", -1, &stmt, nullptr);
                sqlite3_bind_text(stmt,1,req["title"].asString().c_str(),-1,SQLITE_STATIC); sqlite3_bind_text(stmt,2,req["description"].asString().c_str(),-1,SQLITE_STATIC);
                sqlite3_bind_text(stmt,3,req["category"].asString().c_str(),-1,SQLITE_STATIC); sqlite3_step(stmt); sqlite3_finalize(stmt);
                resp["id"] = (int)sqlite3_last_insert_rowid(db.get()); resp["message"] = "Intention créée !";
            } else if (path == "/dictionary/search") {
                std::string q = Utils::parseJson(body)["q"].asString();
                sqlite3_stmt* stmt;
                sqlite3_prepare_v2(db.get(), "SELECT word,definition,language FROM dictionary WHERE word LIKE ?", -1, &stmt, nullptr);
                sqlite3_bind_text(stmt,1,("%"+q+"%").c_str(),-1,SQLITE_STATIC);
                Json::Value arr;
                while (sqlite3_step(stmt)==SQLITE_ROW) {
                    Json::Value entry; entry["word"]=(const char*)sqlite3_column_text(stmt,0); entry["definition"]=(const char*)sqlite3_column_text(stmt,1); entry["language"]=(const char*)sqlite3_column_text(stmt,2);
                    arr.append(entry);
                }
                sqlite3_finalize(stmt);
                resp = arr;
            } else if (path == "/chain/stats") {
                resp = Chain::get().stats();
            } else {
                resp["error"] = "Not found"; code = 404;
            }
            std::string r = Utils::jsonToString(resp);
            auto* mhdResp = MHD_create_response_from_buffer(r.size(), const_cast<char*>(r.c_str()), MHD_RESPMEM_MUST_COPY);
            MHD_add_response_header(mhdResp, "Content-Type", "application/json"); MHD_add_response_header(mhdResp, "Access-Control-Allow-Origin", "*");
            int ret = MHD_queue_response(c, code, mhdResp); MHD_destroy_response(mhdResp);
            return (MHD_Result)ret;
        }
    public:
        void start() { d = MHD_start_daemon(MHD_USE_AUTO|MHD_USE_INTERNAL_POLLING_THREAD, API_PORT, nullptr, nullptr, &callback, this, MHD_OPTION_END); }
        void stop() { if(d) MHD_stop_daemon(d); }
    };
}

// =============================================================================
// Dashboard HTML
// =============================================================================
std::string dashboardHTML() {
    return R"(<!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8"><title>OSIS-X Ultimate</title>
<style>body{background:#050510;color:white;font-family:sans-serif;padding:20px}h1{color:#ffd700}.card{background:#1a1a3e;padding:20px;border-radius:12px;margin:10px 0}.btn{background:#ffd700;color:black;padding:10px 20px;border-radius:25px;text-decoration:none;margin:5px}</style></head><body>
<h1>🌍 OSIS-X C++ Ultimate</h1><p>Blockchain Panafricaine — 54 Pays</p>
<div class="card"><h3>⛓️ Blockchain</h3><p id="blocks">Chargement...</p></div>
<div class="card"><h3>💰 Actions</h3><button class="btn" onclick="earn()">Gagner 100 sat</button> <button class="btn" onclick="donate()">Faire un don</button></div>
<script>
async function load(){let r=await fetch('/chain/stats');let d=await r.json();document.getElementById('blocks').textContent=d.blocks+" blocs, "+d.validators+" validateurs";}
async function earn(){await fetch('/earn',{method:'POST',body:JSON.stringify({userId:1,amount:100})});alert('+100 sat !');}
async function donate(){await fetch('/donate',{method:'POST',body:JSON.stringify({donor:"user",campaign:"Hôpital",amount:50})});alert('Merci !');}
load();setInterval(load,5000);
</script></body></html>)";
}

// =============================================================================
// Application
// =============================================================================
class Application {
    API::Server api;
    bool running = true;
public:
    int run() {
        spdlog::set_default_logger(spdlog::stdout_color_mt("osis"));
        spdlog::set_level(spdlog::level::info);
        spdlog::info("{} — Démarrage", VERSION);
        api.start();
        spdlog::info("API REST sur http://localhost:{}/", API_PORT);
        std::signal(SIGINT, [](int){ exit(0); });
        while (running) std::this_thread::sleep_for(std::chrono::seconds(1));
        api.stop();
        return 0;
    }
};

} // namespace OSIS

int main() { OSIS::Application app; return app.run(); }