# Virtual Pet Simulator Task Manager

## Name
Kali Banghart

## Program Summary
This project is an interactive virtual pet simulator combined with a task management system. The user takes care of a digital pet while also managing tasks, creating a system where productivity directly impacts the pet’s well-being.

The application includes a graphical user interface, persistent data storage, and a multi-language backend. The goal of the project was to combine engaging gameplay with practical task tracking while also integrating Python and C++ in a meaningful way.

## Language Overview
This program starts in **Python** and uses **C++** as a secondary language.

## How Each Language is Used and Why

### Python
Python is used for the main application logic and user interface. This includes:
- Building the GUI using PySide6 (Qt)
- Handling buttons, layouts, and user interactions
- Managing task tracking and storage
- Controlling overall program flow

Python works well here because it allows for fast development and flexible interface design.

### C++
C++ is used for the core pet simulation logic. This includes:
- Managing pet state (health, energy, mood, etc.)
- Updating the pet based on user actions
- Handling structured and performance-focused systems

C++ is a good choice because it provides stronger control over data and enforces a clean object-oriented design.

## How the Languages are Connected
The Python and C++ portions are connected through a bridge system.

- The program starts in `main.py`
- Python communicates with C++ through bridge files (`engine_bridge.py` / `cpp_bridge.py`)
- The C++ engine processes the pet simulation using JSON input/output
- Updated pet state is returned to Python
- Python updates the interface based on the returned data

This creates a clear separation:
- Python handles the user experience
- C++ handles the simulation logic

## Features
- Interactive virtual pet system
- Task manager integrated into gameplay
- Graphical user interface using Qt (PySide6)
- Multiple pet stats (health, energy, mood, etc.)
- Persistent storage using JSON
- Cross-language integration between Python and C++

## Installations / How to Run

### Requirements
- Python 3
- C++ compiler (g++ or clang++)
- PySide6

### Setup
1. Install dependencies:
3. Run the program from the project root:


## What I Learned
- Integrating multiple programming languages in one project
- Building GUI applications with PySide6
- Using JSON for communication between systems
- Designing clean separation between frontend and backend
- Debugging cross-language file and path issues

## Known Issues
- File path errors can occur if not run from the correct directory
- GUI styling is basic and could be improved
- Error handling for corrupted JSON files is limited

## Future Work
- Integrate with platforms like Brightspace or external task systems
- Improve GUI design and user experience
- Add notifications or reminders for tasks
- Expand pet behaviors and interactions
- Make the application deployable as a desktop app

## Citations
- PySide6 Documentation (Qt for Python GUI framework):  
  https://doc.qt.io/qtforpython/

- Qt Widgets Documentation:  
  https://doc.qt.io/qt-6/qtwidgets-index.html

- QPainter Documentation:  
  https://doc.qt.io/qt-6/qpainter.html

- Python JSON Documentation:  
  https://docs.python.org/3/library/json.html

- W3Schools JSON Tutorial:  
  https://www.w3schools.com/python/python_json.asp

- Stack Overflow (JSON file handling):  
  https://stackoverflow.com/questions/12309269/how-do-i-write-json-data-to-a-file

- Stack Overflow (PyQt/PySide basics):  
  https://stackoverflow.com/questions/6760685/creating-a-simple-gui-application-using-pyqt

