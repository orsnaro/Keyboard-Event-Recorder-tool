
"""
                          Coder : Omar rs
                          Version : v2.1.2B
                          version Date :  19 / 6 / 2024
                          Code Type : key recorder app for specific app window
                          Title : KeyRec-Asda
                          Interpreter : cPython  v3.11.0 [Compiler : MSC v.1933 AMD64]
                          EXE using : pyinstaller module
"""
#TODO : easy: user choose timing (easy if timing range is const between all strokes) (each event has time since epoch)
#TODO : easy:  export and import .Key_Rec files (could use pandas or save to csv)
#TODO : easy:  try to use (https://pywinauto.readthedocs.io/en/latest/) instead of low level win32 gui modules
#TODO : depends: OOP it 
#TODO : mid: GUI it
#TODO : mid-hard: mouse recording
#TODO : fix Some windows titles could not be found easily 
#TODO s:
# * Select app by its PID in task maneger (very soon)
# * Select App from Window Title list
# * Select App By pointing to it using mouse hover on app
# * choose your game/app from history of last 5 used apps/games in the tool
# * use key combo e.g.(ctrl + shift)
#TODO: fix some key codes crashes the tool i.e.(insert key)

import menues

if __name__ == '__main__':
   menues.main_keyrec()
