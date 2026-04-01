//
// Created by Kali Banghart on 2/28/26.
//

#ifndef M1AP_PETSTATE_H
#define M1AP_PETSTATE_H
#pragma once
#include <string>

// PetState.h Stores all data for one pet.

struct PetState {
    std::string name    = "KaliPet";
    std::string species = "Cat";  // Cat, Dog, or Owl

    int health    = 80;  // 0-100
    int energy    = 70;  // 0-100
    int happiness = 70;  // 0-100
    int streak    = 0;   // consecutive productive ticks
    int evolution = 1;   // stage 1-3
    bool alive    = true;

    long long last_update_epoch = 0;  // set by Python, not us

    void clamp();
};

#endif //M1AP_PETSTATE_H