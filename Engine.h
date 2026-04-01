//
// Created by Kali Banghart on 2/28/26.
//

#ifndef M1AP_ENGINE_H
#define M1AP_ENGINE_H
#pragma once
#include "PetState.h"

// Engine.h Declares the tick function and its input/output structs.

struct EngineInput {
    PetState state;
    int work_points    = 0;  // points from tasks or focus sessions
    int seconds_elapsed = 0; // time since last tick
};

struct EngineOutput {
    PetState    state;
    std::string mood_sprite = "idle";  // idle / happy / sad / dead
    std::string message;
};

class Engine {
public:
    static EngineOutput tick(const EngineInput& in);
};

#endif //M1AP_ENGINE_H