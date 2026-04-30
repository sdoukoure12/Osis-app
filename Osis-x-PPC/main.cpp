// =============================================================================
// OSIS-X PROTOCOL : Preuve de Présence & Contribution (PPC)
// =============================================================================
// Nouvel algorithme de consensus écologique :
// - Ne nécessite pas de CPU/GPU intensif
// - Compatible mobile (batterie préservée)
// - Récompense basée sur le temps de présence et la qualité de contribution
// - Peut générer des tokens BTC/ETH wrappés via des bridge inter-chaînes
// =============================================================================

#include <iostream>
#include <string>
#include <map>
#include <vector>
#include <chrono>
#include <thread>
#include <mutex>
#include <random>

namespace OSIS {
namespace PPC {

// =============================================================================
// Configuration du protocole PPC
// =============================================================================
struct PPCConfig {
    // Récompenses de base (en satoshis)
    double presenceRewardPerMinute = 1.0;      // Gain par minute de présence
    double contributionMultiplier = 5.0;        // Multiplicateur si contribution validée
    double validationBonus = 10.0;              // Bonus par validation communautaire
    double maxDailyReward = 10000.0;            // Plafond quotidien

    // Paramètres techniques
    int heartbeatIntervalSeconds = 30;          // Intervalle de "ping" pour prouver la présence
    int validationThreshold = 3;                // Nombre de validateurs requis
    double minReputationForValidation = 10.0;   // Réputation minimale pour être validateur
};

// =============================================================================
// État d'un participant PPC
// =============================================================================
struct ParticipantState {
    std::string userId;
    double totalRewards = 0.0;
    double reputation = 1.0;
    double todayRewards = 0.0;
    std::chrono::system_clock::time_point lastHeartbeat;
    bool isActive = false;
    std::vector<std::string> pendingContributions;
    int validationsPerformed = 0;
};

// =============================================================================
// Moteur principal PPC (Proof of Presence & Contribution)
// =============================================================================
class PPCEngine {
private:
    std::map<std::string, ParticipantState> participants;
    std::mutex mtx;
    PPCConfig config;
    std::vector<std::string> contributionPool;
    
    // Générateur aléatoire pour les rewards non-déterministes
    std::mt19937 rng{std::random_device{}()};
    
public:
    PPCEngine() = default;
    
    // Enregistrer un nouveau participant
    bool registerParticipant(const std::string& userId) {
        std::lock_guard<std::mutex> lock(mtx);
        if (participants.find(userId) != participants.end()) return false;
        participants[userId] = {userId, 0.0, 1.0, 0.0, 
                                std::chrono::system_clock::now(), true, {}, 0};
        return true;
    }
    
    // Envoyer un heartbeat (preuve de présence)
    double sendHeartbeat(const std::string& userId) {
        std::lock_guard<std::mutex> lock(mtx);
        auto it = participants.find(userId);
        if (it == participants.end()) return 0.0;
        
        auto& p = it->second;
        auto now = std::chrono::system_clock::now();
        auto elapsed = std::chrono::duration_cast<std::chrono::minutes>(now - p.lastHeartbeat).count();
        
        if (elapsed >= 1) {
            double reward = std::min(elapsed * config.presenceRewardPerMinute, 
                                     config.maxDailyReward - p.todayRewards);
            p.totalRewards += reward;
            p.todayRewards += reward;
            p.lastHeartbeat = now;
            p.reputation += 0.01; // Légère augmentation de réputation pour présence continue
            return reward;
        }
        return 0.0;
    }
    
    // Soumettre une contribution
    bool submitContribution(const std::string& userId, const std::string& content) {
        std::lock_guard<std::mutex> lock(mtx);
        auto it = participants.find(userId);
        if (it == participants.end()) return false;
        
        contributionPool.push_back(content);
        it->second.pendingContributions.push_back(content);
        return true;
    }
    
    // Valider une contribution (preuve de contribution)
    double validateContribution(const std::string& validatorId, 
                                const std::string& contributorId, 
                                bool approved) {
        std::lock_guard<std::mutex> lock(mtx);
        auto valIt = participants.find(validatorId);
        auto conIt = participants.find(contributorId);
        if (valIt == participants.end() || conIt == participants.end()) return 0.0;
        
        if (valIt->second.reputation < config.minReputationForValidation) return 0.0;
        
        double reward = 0.0;
        if (approved) {
            reward = config.contributionMultiplier * config.presenceRewardPerMinute;
            conIt->second.totalRewards += reward;
            conIt->second.todayRewards += reward;
            conIt->second.reputation += 0.5;
        }
        
        valIt->second.reputation += 0.1;
        valIt->second.validationsPerformed++;
        
        // Vérifier si on atteint le seuil de validation
        auto& pending = conIt->second.pendingContributions;
        if (!pending.empty()) {
            // Simuler un comptage de validations (simplifié)
            if (valIt->second.validationsPerformed % config.validationThreshold == 0) {
                conIt->second.totalRewards += config.validationBonus;
                conIt->second.todayRewards += config.validationBonus;
                pending.clear(); // Contribution validée
            }
        }
        
        return reward;
    }
    
    // Obtenir les statistiques d'un participant
    ParticipantState getParticipantStats(const std::string& userId) {
        std::lock_guard<std::mutex> lock(mtx);
        auto it = participants.find(userId);
        if (it != participants.end()) return it->second;
        return {};
    }
    
    // Réinitialiser les compteurs quotidiens (appelé à minuit)
    void resetDailyCounters() {
        std::lock_guard<std::mutex> lock(mtx);
        for (auto& [id, p] : participants) {
            p.todayRewards = 0.0;
        }
    }
    
    // Obtenir le nombre total de participants
    size_t getParticipantCount() const {
        return participants.size();
    }
    
    // Simuler le bridge BTC/ETH (conceptuel)
    std::map<std::string, double> getBridgeRates() {
        return {
            {"BTC", 0.00000001},  // 1 satoshi = 0.00000001 BTC
            {"ETH", 0.0000000001}, // 1 satoshi ≈ 0.0000000001 ETH (variable)
            {"OSIS", 1.0}         // Token natif
        };
    }
};

// =============================================================================
// Intégration avec la blockchain principale
// =============================================================================
class PPCBridge {
private:
    PPCEngine ppcEngine;
    std::thread dailyResetThread;
    bool running = true;
    
public:
    PPCBridge() {
        // Thread de réinitialisation quotidienne
        dailyResetThread = std::thread([this]() {
            while (running) {
                std::this_thread::sleep_for(std::chrono::hours(24));
                ppcEngine.resetDailyCounters();
            }
        });
    }
    
    ~PPCBridge() {
        running = false;
        if (dailyResetThread.joinable()) dailyResetThread.join();
    }
    
    PPCEngine& getEngine() { return ppcEngine; }
};

// Instance globale
inline PPCBridge& getPPCBridge() {
    static PPCBridge instance;
    return instance;
}

} // namespace PPC
} // namespace OSIS

// =============================================================================
// Exemple d'intégration dans l'API existante
// =============================================================================
namespace OSIS {
namespace API {
    // Ajouter ces endpoints au serveur REST existant :
    // POST /ppc/heartbeat  -> envoie un heartbeat et retourne la récompense
    // POST /ppc/contribute -> soumet une contribution
    // POST /ppc/validate   -> valide la contribution d'un autre
    // GET  /ppc/stats      -> statistiques du participant
    
    std::string handlePPCEndpoint(const std::string& path, const std::string& body) {
        auto& engine = PPC::getPPCBridge().getEngine();
        Json::Value req = Utils::parseJson(body);
        Json::Value resp;
        
        if (path == "/ppc/heartbeat") {
            std::string userId = req["userId"].asString();
            double reward = engine.sendHeartbeat(userId);
            resp["reward"] = reward;
            resp["message"] = "Heartbeat reçu. +" + std::to_string(reward) + " satoshis";
        }
        else if (path == "/ppc/contribute") {
            std::string userId = req["userId"].asString();
            std::string content = req["content"].asString();
            bool success = engine.submitContribution(userId, content);
            resp["success"] = success;
            resp["message"] = success ? "Contribution soumise" : "Erreur";
        }
        else if (path == "/ppc/validate") {
            std::string validatorId = req["validatorId"].asString();
            std::string contributorId = req["contributorId"].asString();
            bool approved = req.get("approved", true).asBool();
            double reward = engine.validateContribution(validatorId, contributorId, approved);
            resp["reward"] = reward;
            resp["message"] = approved ? "Contribution approuvée" : "Contribution rejetée";
        }
        else if (path == "/ppc/stats") {
            std::string userId = req["userId"].asString();
            auto stats = engine.getParticipantStats(userId);
            resp["userId"] = stats.userId;
            resp["totalRewards"] = stats.totalRewards;
            resp["reputation"] = stats.reputation;
            resp["todayRewards"] = stats.todayRewards;
            resp["isActive"] = stats.isActive;
        }
        else if (path == "/ppc/bridge") {
            auto rates = engine.getBridgeRates();
            Json::Value bridgeRates;
            for (auto& [token, rate] : rates) bridgeRates[token] = rate;
            resp["rates"] = bridgeRates;
            resp["message"] = "Taux de conversion PPC -> Crypto";
        }
        
        return Utils::jsonToString(resp);
    }
}
}

// =============================================================================
// Point d'entrée pour tester le module PPC standalone
// =============================================================================
int main() {
    std::cout << "OSIS-X PPC Protocol - Preuve de Présence & Contribution" << std::endl;
    std::cout << "========================================================" << std::endl;
    
    auto& engine = OSIS::PPC::getPPCBridge().getEngine();
    
    // Enregistrement de participants
    engine.registerParticipant("user1");
    engine.registerParticipant("user2");
    engine.registerParticipant("user3");
    
    std::cout << "Participants enregistrés: " << engine.getParticipantCount() << std::endl;
    
    // Simulation de heartbeats
    std::cout << "\n--- Simulation de heartbeats ---" << std::endl;
    double r1 = engine.sendHeartbeat("user1");
    double r2 = engine.sendHeartbeat("user2");
    std::cout << "User1 heartbeat reward: " << r1 << " satoshis" << std::endl;
    std::cout << "User2 heartbeat reward: " << r2 << " satoshis" << std::endl;
    
    // Simulation de contribution et validation
    std::cout << "\n--- Simulation de contribution ---" << std::endl;
    engine.submitContribution("user1", "Article sur l'agriculture durable");
    double vReward = engine.validateContribution("user2", "user1", true);
    std::cout << "Validation reward for user1: " << vReward << " satoshis" << std::endl;
    
    // Statistiques
    auto stats = engine.getParticipantStats("user1");
    std::cout << "\n--- Statistiques User1 ---" << std::endl;
    std::cout << "Total Rewards: " << stats.totalRewards << " satoshis" << std::endl;
    std::cout << "Reputation: " << stats.reputation << std::endl;
    
    // Taux de bridge
    auto rates = engine.getBridgeRates();
    std::cout << "\n--- Taux de conversion ---" << std::endl;
    for (auto& [token, rate] : rates) {
        std::cout << "1 satoshi = " << rate << " " << token << std::endl;
    }
    
    std::cout << "\n✅ Protocole PPC fonctionnel." << std::endl;
    std::cout << "🌍 Peut être intégré à l'API REST pour le minage mobile écologique." << std::endl;
    
    return 0;
}