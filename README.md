# M3OEP-kbanghar

## Name
Kali Banghart

## Program Summary
This project is a pet simulator task manager it uses 
## Language Overview
This program starts in **Python** and uses **C++** as a secondary language.

## How Each Language is Used and Why

### Python
Python is used for the main application logic and  user interface. This includes:
- Handling the interface (buttons, layouts, interactions)
- Managing user input and events
- Task tracking system
- Overall program flow
Phyton is great for this because it allows for lots of variety around the interface 
### C++
C++ is used for the core pet simulation logic. This includes:
- Pet state management
- Internal systems that control how the pet behaves
- More structured and performance focused components

C++ is a good choice here because it allows for stronger control over data and structure. 

## How the Languages are Connected
The Python and C++ portions of the program are connected using a bridge between the two languages.

- The main program starts in `app.py`
- Python calls into C++ through a bridge file ( `engine_bridge.py`)
- The C++ engine handles the pet logic and returns updated state information back to Python
- Python then updates the interface based on that returned data

This creates a separation where:
- Python controls the user experience
- C++ controls the simulation logic

## Installations / How to Run
For this you just need c++ and Phython 3 able to run on your machine. 

## Future Work
With more time I hope to make this compatible with brightspace or another task manager and a way to fully have it compatible with your home screen. 

## Citations
- PySide6 Documentation (Qt for Python GUI framework):  
  https://doc.qt.io/qtforpython/

- Qt Widgets Documentation (layouts, buttons, UI elements):  
  https://doc.qt.io/qt-6/qtwidgets-index.html

- QPainter and Graphics Rendering (drawing and custom visuals):  
  https://doc.qt.io/qt-6/qpainter.html

- Python JSON Module Documentation (reading/writing JSON files):  
  https://docs.python.org/3/library/json.html

- JSON Tutorial (structure and usage examples):  
  https://www.w3schools.com/python/python_json.asp

- Stack Overflow discussion on saving/loading JSON in Python:  
  https://stackoverflow.com/questions/12309269/how-do-i-write-json-data-to-a-file

- Stack Overflow discussion on PySide6 / Qt GUI basics:  
  https://stackoverflow.com/questions/6760685/creating-a-simple-gui-application-using-pyqt

## Self-Assessment
Expected Grade: 100

The program is interactive, uses both Python and C++ in a meaningful way, and clearly demonstrates integration between the two languages.
It includes a working GUI, persistent data, and structured backend logic. The project goes beyond basic requirements by combining multiple systems. 