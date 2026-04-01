//
// Created by Kali Banghart on 2/28/26.

#include "Engine.h"

#include <string>
#include <algorithm>

// Engine.cpp Core game logic. Stats change based on productivity and energy level.
// Each species has slightly different bonuses - Dog is tough, Cat is happy, Owl is efficient.


static int healthBonus(const std::string& s) {
    if (s == "Dog") return 3;
    return 0;
}

static int happyBonus(const std::string& s) {
    if (s == "Cat") return 3;
    if (s == "Dog") return 1;
    return 0;
}

static int energyEfficiency(const std::string& s) {
    if (s == "Owl") return 2;
    return 0;
}

EngineOutput Engine::tick(const EngineInput& in) {
    EngineOutput out;
    out.state = in.state;

    if (!out.state.alive) {
        out.mood_sprite = "dead";
        out.message     = "Your pet is gone. Start a new one to try again.";
        return out;
    }

    // cap at 8 hours so leaving the app closed overnight doesnt instantly kill the pet
    int    dt   = std::clamp(in.seconds_elapsed, 0, 8 * 60 * 60);
    double mins = dt / 60.0;

    int dHealth = 0;
    int dEnergy = 0;
    int dHappy  = 0;

    if (in.work_points > 0) {
        out.state.streak++;

        dHealth += 2 + (in.work_points / 10) + healthBonus(out.state.species);
        dHappy  += 3 + (in.work_points / 15) + happyBonus(out.state.species);

        // bigger tasks cost more energy, owls pay less
        int cost = (1 + in.work_points / 40) - energyEfficiency(out.state.species);
        dEnergy -= std::max(0, cost);

        if (out.state.streak % 8 == 0 && out.state.evolution < 3)
            out.state.evolution++;

        out.message = "Nice work! Your pet feels cared for.";

    } else {
        // idle tick - health and happiness decay, but energy slowly recovers
        out.state.streak = std::max(0, out.state.streak - 1);

        dHealth -= static_cast<int>(1 + mins * 0.6);
        dHappy  -= static_cast<int>(2 + mins * 0.8);

        int regen = static_cast<int>(mins * 0.5) + energyEfficiency(out.state.species);
        dEnergy  += std::min(regen, 5);

        out.message = "Your pet is resting. Complete some tasks to keep it healthy!";
    }

    // energy mechanic - low energy drains health, high energy gives a bonus
    int projEnergy = std::clamp(out.state.energy + dEnergy, 0, 100);

    if (projEnergy <= 0) {
        dHealth -= 6;
        dHappy  -= 5;
        out.message += " Your pet is exhausted! Let it rest or it will get sick.";
    } else if (projEnergy <= 20) {
        dHealth -= 3;
        dHappy  -= 2;
        out.message += " Your pet is very tired.";
    } else if (projEnergy <= 40) {
        dHealth -= 1;
    } else if (projEnergy >= 80 && in.work_points > 0) {
        dHappy += 3;
        out.message = "Well rested and working hard! Your pet is thriving.";
    }

    out.state.health    += dHealth;
    out.state.energy    += dEnergy;
    out.state.happiness += dHappy;

    out.state.clamp();

    if (!out.state.alive) {
        out.mood_sprite = "dead";
        out.message     = "Your pet ran out of health. Try balancing study with rest!";
        return out;
    }

    // pick sprite based on stats
    bool exhausted  = out.state.energy    <= 20;
    bool wellRested = out.state.energy    >= 50;
    bool highHappy  = out.state.happiness >= 70;
    bool goodHealth = out.state.health    >= 50;

    if (exhausted) {
        out.mood_sprite = "sad";
    } else if (highHappy && goodHealth && wellRested) {
        out.mood_sprite = "happy";
    } else if (out.state.happiness <= 35 || out.state.health <= 30) {
        out.mood_sprite = "sad";
    } else {
        out.mood_sprite = "idle";
    }

    return out;
}