//
// Created by Kali Banghart on 2/28/26.

#include "Json.h"

#include "Engine.h"
#include <iostream>
#include <string>
//TO RUN USE THIS IN TERMIANAL python3 main.py
// main.cpp Entry point for the C++ engine binary.
// Python calls this as a subprocess, passing JSON in and reading JSON out.
// Usage: ./M1AP --in data/state_in.json --out data/state_out.json


static void usage() {
    std::cout << "Usage: pet_engine --in <input.json> --out <output.json>\n";
}

int main(int argc, char** argv) {
    std::string inPath, outPath;

    for (int i = 1; i < argc; i++) {
        std::string a = argv[i];
        if      (a == "--in"  && i + 1 < argc) inPath  = argv[++i];
        else if (a == "--out" && i + 1 < argc) outPath = argv[++i];
    }

    if (inPath.empty() || outPath.empty()) {
        usage();
        return 2;
    }

    std::string raw;
    if (!sjson::read_file(inPath, raw)) {
        std::cerr << "Failed to read input file: " << inPath << "\n";
        return 3;
    }

    sjson::Obj obj;
    if (!sjson::parse(raw, obj)) {
        std::cerr << "Failed to parse input JSON\n";
        return 4;
    }

    EngineInput in;
    in.state.name              = sjson::get_str (obj, "name",              "KaliPet");
    in.state.species           = sjson::get_str (obj, "species",           "Cat");
    in.state.health            = (int)sjson::get_num(obj, "health",        80);
    in.state.energy            = (int)sjson::get_num(obj, "energy",        70);
    in.state.happiness         = (int)sjson::get_num(obj, "happiness",     70);
    in.state.streak            = (int)sjson::get_num(obj, "streak",        0);
    in.state.evolution         = (int)sjson::get_num(obj, "evolution",     1);
    in.state.alive             = sjson::get_bool(obj, "alive",             true);
    in.state.last_update_epoch = (long long)sjson::get_num(obj, "last_update_epoch", 0);
    in.work_points             = (int)sjson::get_num(obj, "work_points",   0);
    in.seconds_elapsed         = (int)sjson::get_num(obj, "seconds_elapsed", 0);

    EngineOutput out = Engine::tick(in);

    // just  pass it through
    sjson::Obj o;
    o["name"]              = sjson::Value::str    (out.state.name);
    o["species"]           = sjson::Value::str    (out.state.species);
    o["health"]            = sjson::Value::number (out.state.health);
    o["energy"]            = sjson::Value::number (out.state.energy);
    o["happiness"]         = sjson::Value::number (out.state.happiness);
    o["streak"]            = sjson::Value::number (out.state.streak);
    o["evolution"]         = sjson::Value::number (out.state.evolution);
    o["alive"]             = sjson::Value::boolean(out.state.alive);
    o["mood_sprite"]       = sjson::Value::str    (out.mood_sprite);
    o["message"]           = sjson::Value::str    (out.message);
    o["last_update_epoch"] = sjson::Value::number ((double)out.state.last_update_epoch);

    if (!sjson::write_file(outPath, sjson::dump(o))) {
        std::cerr << "Failed to write output file: " << outPath << "\n";
        return 5;
    }

    return 0;
}