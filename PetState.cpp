//
// Created by Kali Banghart on 2/28/26.

#include "PetState.h"

#include <algorithm>

// Clamps all stats to valid range and handles death.

void PetState::clamp() {
    health    = std::clamp(health,    0, 100);
    energy    = std::clamp(energy,    0, 100);
    happiness = std::clamp(happiness, 0, 100);

    if (health <= 0)
        alive = false;
}