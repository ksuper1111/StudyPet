cmake_minimum_required(VERSION 3.15)
project(M1AP)

set(CMAKE_CXX_STANDARD 17)

add_executable(M1AP main.cpp
        PetState.h
        PetState.cpp
        Engine.cpp
        Engine.h
        Json.h)
