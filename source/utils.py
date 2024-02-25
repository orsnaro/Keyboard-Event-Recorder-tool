"""
                          Coder : Omar
                          Version : v2.1.1B
                          version Date :  25 / 2 / 2024
                          Code Type : key recorder app for specific app window
                          Title : KeyRec-Asda
                          Interpreter : cPython  v3.11.0 [Compiler : MSC v.1933 AMD64]
                          EXE using : pyinstaller module
"""
import os 
import win32api
import keyboard
import json
import msvcrt

def count_files(directory= r"C:\Users\%USERNAME%\AppData\Roaming\KeyRec_Asda_history"):
    """
    Counts the number of files in a directory, including subdirectories if desired.

    Args:
        directory (str): Path to the directory.

    Returns:
        int: The number of files in the directory.
    """
    directory = put_user_name(directory)
    file_count = 0
    for root, _, files in os.walk(directory):
        for file in files:
            # Check if it's a real file, not a hidden file or symbolic link
            if os.path.isfile(os.path.join(root, file)):
                file_count += 1

    return file_count
 
def make_data_directory(directory= r"C:\Users\%USERNAME%\AppData\Roaming\KeyRec_Asda_history") -> int:
   directory = put_user_name(directory)
   
   #os.system("mkdir..") returns 0 means sucess but else wise it prints to the console! so will check if exists first to avoid un-wanted os module msgs to appear to enduser's console
   mkdir_state = os.system(f"mkdir \"{directory}\"") if not os.path.exists(directory) else 1 #1 means that couldn't make directory: already exists or any other issues
   return mkdir_state

def recording_menu() -> int:
   _user_choice :int = None
   
   IsFirstRec = not bool(count_files())
   
   print("\n\n--------------------------------")
   print("\n\n C H O O S E: ")
   print(f"\n-> '1' New Record ") 
   print("\n-> '2' Use last Record ") if not IsFirstRec else print("", end="")
   print("\n-> '0' Exit ")
   print("\n\n--------------------------------")
   
   try:
      flush_in_buffer()
      _user_choice = int(input(">> "))
      if IsFirstRec and _user_choice == 2: raise #handle if user choosed 2 even if the option is hidden
        
   except Exception() as e:
      # os.system("cls")
      print(f"\n #ERROR! you've mostly entered an invalid input! \nReloading...")
      _user_choice = recording_menu()
         
   return _user_choice

def target_menu() -> int:
   _user_choice2 :int = None
   
   while True :
      flush_in_buffer()
      print("\n\n--------------------------------")
      print("\n\n C H O O S E: ")
      print("\n\n (1) Play KeyRec on custom window \n (2) Play KeyRec on Asda Story window")
      print("\n\n--------------------------------")
      _user_choice2 =  input(">> ")

      if _user_choice2.isnumeric() and  1 <= int(_user_choice2) <= 2 :
         break;
      else :
         print ("\n\n#INVALID INPUT! RETRY#")
         _user_choice2 = target_menu()
         
   return int(_user_choice2)

def put_user_name(_path_to_edit: str) -> str:
   user_name = os.environ['USERNAME']
   _path_to_edit = _path_to_edit.replace("%USERNAME%", user_name)
   _path_to_edit = os.path.normpath(_path_to_edit) #normpath()handels forward slashed and etc..
   return _path_to_edit

def process_file_path(isNew = False, _file_dir: str = r"C:\Users\%USERNAME%\AppData\Roaming\KeyRec_Asda_history") -> os.PathLike | str:
   # we'll not call this method unless the dir exist and there is old records so no need to handle this inside
   _file_dir = put_user_name(_file_dir)
   
   file_abs_path: os.PathLike | str = None
   if os.path.isdir(_file_dir): #actually it handled on caller but let's make it future proof :D
      file_no = count_files(directory= _file_dir) # files numbering starts with one e.g.(keyrec1) is first file
      file_name = f"keyrec{file_no + 1 if isNew else file_no}" + ".json"
      file_abs_path = os.path.join(_file_dir, file_name)
   
   file_abs_path = os.path.normpath(file_abs_path)
   return file_abs_path

def save_record(rec_to_save: list, save_dir: str = r"C:\Users\%USERNAME%\AppData\Roaming\KeyRec_Asda_history"):
   #NOTE: also you can utilize 'keyboard.KeyboardEvent.to_json()'
   
   save_dir = put_user_name(save_dir)
   
   file_path: os.PathLike | str  = process_file_path(isNew= True, _file_dir= save_dir)
   
   events_dict : dict = dict()
   with open(file_path, 'w') as jsonFile:
      for i in range(len(rec_to_save)): 
         event = rec_to_save[i]
         
         # attrs: dict = event.__dict__
         # prev attrs var is eq to the below 3 lines but the 3 lines ignores 'None' valued attributes
         event_attrs = dict(
            (attr, getattr(event, attr)) for attr in ['event_type', 'scan_code', 'name', 'time', 'device', 'modifiers', 'is_keypad']
            if not attr.startswith('_') and getattr(event, attr) is not None
            )
         events_dict[str(i)] = event_attrs
         
      events_json: str= json.dumps(events_dict, ensure_ascii= False, indent= 4)
      jsonFile.write(events_json)      
   
    
      
      
      
   
def flush_in_buffer():
   '''
      * this loop consumes all keyboard library buffer so no control char messes out our tool:
      * NOTE: ref: https://stackoverflow.com/a/2521054/15006369
   '''
   
   while msvcrt.kbhit():
      msvcrt.getch()