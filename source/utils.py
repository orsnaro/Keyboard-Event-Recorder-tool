"""
                          Coder : Omar rs
                          Version : v2.1.2B
                          version Date :  19 / 6 / 2024
                          Code Type : key recorder app for specific app window
                          Title : KeyRec-Asda
                          Interpreter : cPython  v3.11.0 [Compiler : MSC v.1933 AMD64]
                          EXE using : pyinstaller module
"""
# from curses import window
from imp import load_source
import os 
import win32api
import win32gui
import keyboard
import win32con
import win32process
import json
import msvcrt
import alive_progress #TODO
import scan_vk_codes_dicts as codes
import keyboard
import time
import os
import msvcrt
import json
import utils
import random


defaults_dict = {
   "root_app_path"       : r"C:\Users\%USERNAME%\AppData\Roaming\KeyRec_Asda",
   "window_log_file"     : "recent_windows.json",
   "json_main_key"       : "window_log",
   "window_name"         : "AsdaStory (AREAGAME)",
   "toggle_play_key"     : "f12",
   "toggle_record_key"   : "f10"
}


def get_keys_map_dict() -> dict:
   # Create a dictionary that maps key names to virtual key codes and scan codes
   # scan_codes_dict = codes.SCAN_CODE
   vk_codes_dict = codes.VK_CODES
   key_mapping: dict = {}

# NOTE: I dont need to use win32api.MapVirtualKey() here to get v_keys
# since i have the  dict already i can make scand codes then map directly

   for key_name, key_code in vk_codes_dict.items() :
      scan_code = win32api.MapVirtualKey(key_code,0)#map virtual key to scan code
      key_mapping[key_name] = {"vk_code": key_code, "scan_code": scan_code}

   return key_mapping


def check_add_to_fav() -> str:
   rec_name: str = None
   print("\n\n--------------------------------")
   print("\n Add this record to favorites? ... (type record name or press 'enter' to skip!)")
   utils.flush_in_buffer()
   new_fav_rec_name = (input(">> ").strip())
   print("skipped saving to favs..." if new_fav_rec_name is None or new_fav_rec_name == "" else f"OK! saving '{new_fav_rec_name}' to favs!...(similar names  overwrites old files!)")
   print("\n\n--------------------------------")
   
   return new_fav_rec_name if new_fav_rec_name != "" and new_fav_rec_name != None else None

def load_record(file_dir: str | os.PathLike = defaults_dict["root_app_path"] + r"\history", fav_rec_name: str = None) -> list[keyboard.KeyboardEvent]:
   # we'll not call this method unless the dir exist and there is old records so no need to handle this inside
   _events_list: list[keyboard.KeyboardEvent] = []
   
   file_dir = utils.put_user_name(file_dir)
   file_abs_path: os.PathLike | str = process_file_path(_file_dir= file_dir, _fav_rec_name = (fav_rec_name if fav_rec_name != None else None) )
      
   if os.path.isfile( file_abs_path ) :
      with open(file_abs_path, 'r', encoding="utf-8") as jsonFile:
         events_json: str = jsonFile.read()
         _events_dict = json.loads(events_json)
      
      for event in _events_dict:
         one_event_dict = _events_dict[event]
         _events_list.append(keyboard.KeyboardEvent(**one_event_dict)) #Say with me I Love python unpacking syntax!

   print(f"DONE loading!")
   print(f"\n\n Loaded Record = ", flush=True)
   [print(event) for event in _events_list]
   
   return _events_list


# Record the key presses
def new_record(start_key='f10'):
   events: list[keyboard.KeyboardEvent] = []
  
   print("\n\n--------------------------------")
   print(f"\n\n\n-> '{start_key}' to start record. \n-> '{start_key}' again stops record.")
   print("\n\n--------------------------------")
   print(">> ", end="")
   
   while True:
      if keyboard.is_pressed(start_key):
         print("\n\n--------------------------------")
         print(f"\nSTARTED RECORDING...({start_key} again to stop)")

         utils.flush_in_buffer()
         # exprimental: suppress=True the recorded events are not sent to the operating system, effectively blocking them from being observed by other applications
         events = keyboard.record(until=start_key, suppress=True) 

         keyboard.unhook_all()
         print(f"DONE RECORDING! Saving To 'keyrec{str(utils.count_files()+1)}.json'...")
         break
   
   events_done = events[1:-1] #skip the record control key 'start_key' events
 
   print(f"\n\nFull Record = ", flush=True)
   [print(event) for event in events_done]
   rec_file_name: str= check_add_to_fav()
   save_record(rec_to_save= events_done) if rec_file_name == None else save_record(rec_to_save= events_done, add_to_favorites_list= True, fav_rec_name= rec_file_name)
   
   del events
   return events_done

def  waitLoop(waitTime: float, instant_stop_key):
   startT = time.monotonic()
   while time.monotonic() - startT < waitTime :
      if keyboard.is_pressed(instant_stop_key):
         return True
   return False

# Replay the key presses to a specific application identified by its PID
def replay_in_window(events: list[keyboard.KeyboardEvent],  key_mapping: dict, replay_key: str = defaults_dict["toggle_play_key"], stop_key: str = defaults_dict["toggle_record_key"], window_name: str = defaults_dict["window_name"]):

   # Set the window name you want to search for

   # Get a handle to the application's main window
   hwnd = win32gui.FindWindow(None, window_name)
   
   
   if hwnd == False  or window_name == '': #retry
      print("\n\n (Error! Finding Your Window title) \nretry please...\n\n")
      return False #use it later
      
 
   tid , pid = win32process.GetWindowThreadProcessId(hwnd)
   crnt_thread_id = win32api.GetCurrentThreadId()
   target_proc_id , _ = win32process.GetWindowThreadProcessId(hwnd)
   
   try:
      # now two threads can share input like keyboard state and crnt focus window
      win32process.AttachThreadInput(crnt_thread_id , target_proc_id , True)
   except Exception as e :
      print(f"(ERROR! probably Access is denied try running the tool as admin.) details:\n {e}\n\n\n RESTARTING KeYRec tool...")
      return False
   
   log_window_name(window_name)
 
   # print to user some info about window
   rect = win32gui.GetWindowRect(hwnd)
   print ("\n\t\tWINDOW DETAILS:")
   print(f"\nName: '{window_name}' Shape: {rect}")
   print("NOTE: This window control is :" , end= '')
   enabled = "Enabled" if win32gui.IsWindowEnabled(hwnd) else "Disabled"
   print (f" ({enabled})")
   
   
   print("\n\n--------------------------------")
   print( f"\n\n\n-> '{replay_key}' to start replay. \n-> '{replay_key}' again pauses replay")
   print("\n\n--------------------------------")
   print(">> ", end="")

   while True: #NOTE: most inner loop controls terminating this loop
      if keyboard.is_pressed(replay_key):
         while keyboard.is_pressed(replay_key) : pass
         print(f"\nSTARTED PLAYING!...({replay_key} again to stop)")
         # time.sleep(0.1)

         notedHiddenOnce = False
         while True:
            #next 2 lines brings window you want to focus and show  it at top most
            # win32gui.SetForegroundWindow(hwnd)
            # events = events[:-1]
            
            #notify user that window is hidden only once when it starts being
            if not win32gui.IsWindowVisible(hwnd) and not notedHiddenOnce:
               print (f"Note: window '{window_name}' is minimized or hidden")
               notedHiddenOnce = True
            elif win32gui.IsWindowVisible(hwnd) and notedHiddenOnce:
               print (f"Visible again!")
               notedHiddenOnce = False
               
               
            for event in events:
               # convert gotten physical key code( scan code ) to vk code and pass booth
               scan_code = event.scan_code
               vk_code   = win32api.MapVirtualKey( scan_code , 1) #map or convert  scan code to vk code
               key_name  = next((key for key , val in codes.VK_CODES.items() if val == vk_code), None) #return first elmnt if there is multiple
               #NOTE: clearing ambiguity of  next() name! 
               # When you create an iterator object from an iterable using the iter() function, the iterator is positioned before the first element in the sequence.

               if event.event_type == keyboard.KEY_DOWN:
                  msg = win32con.WM_KEYDOWN
                  wparam = vk_code #WPARAM =  name is short of WORD(16bits) PARAMETER. but its  32bit actually XD -> use .bit_length() to Check :D!
                  lparam = (scan_code << 16) | 1 #LONG PARAMETER : #FOR KEY DOWN  RMB must set to 1 (little endian)
      
                  if win32gui.IsWindow(hwnd) : #check first if window still active
                     win32gui.PostMessage(hwnd, msg, wparam, lparam)
                  else : 
                     print (f"This Window({window_name})  doesn't Exist anymore! \n RESTARTING KeYRec tool...")
                     return False 
                  

               if event.event_type == keyboard.KEY_UP:
                  msg = win32con.WM_KEYUP
                  wparam = vk_code
                  # scan_code is 8bit originally
                  lparam = (1 << 31) | (scan_code << 16)#little endian: FOR KEY UP LMB must be set to 1 
      
                  if win32gui.IsWindow(hwnd) : #check first if window still active
                     win32gui.PostMessage(hwnd, msg, wparam, lparam)
                  else : 
                     print (f"This Window({window_name})  doesn't Exist anymore! \n RESTARTING KeYRec tool... ")
                     return False
                  
               rand_sleep_time = round(random.uniform(0.025, 0.250), 3)
               isPressedInWaitLoop = waitLoop(rand_sleep_time, instant_stop_key= replay_key)
   
               if keyboard.is_pressed(replay_key) or isPressedInWaitLoop: #listen while playing if pause key pressed
                  while keyboard.is_pressed(replay_key) : pass
                  utils.flush_in_buffer()
                  # keyboard.release(replay_key)
                  # time.sleep(0.1)
                  
                  
                  try:
                     # Detach i/p crnt thread from i/p target_proc_thread 
                     win32process.AttachThreadInput(crnt_thread_id , target_proc_id , False)
                  except Exception as e :
                     print(f"ERROR! probably target app has terminated. details:\n {e} \n\n\n RESTARTING KeYRec tool...")
                     return False
               
                  print("\n\n--------------------------------")
                  print("\nPAUSED! Key Player...")
                  print(
                     f"\n  -> '{replay_key}' again to UN-PAUSE")
                  print(
                     f"  -> '{stop_key}' stop & go to Main menu ")
                  print("\n\n--------------------------------")
                  print(">> ", end="")
      
                  while True :#stop and wait for a key to unpuase
                     if keyboard.is_pressed(replay_key):
                        while keyboard.is_pressed(replay_key) : pass
                        utils.flush_in_buffer()
                        # keyboard.release(replay_key)
                        # time.sleep(0.1)
                        
                        
                        try:
                           win32process.AttachThreadInput(crnt_thread_id , target_proc_id , True)
                        except Exception as e :
                           print(f"ERROR! probably target app has terminated. details:\n {e} \n\n\n RESTARTING KeYRec tool...")
                           return False
                        
                        print(f"\nUN-PAUSED! continue PLAYING...({replay_key} again to pause)")
                        break

                     elif keyboard.is_pressed(stop_key): #STOP AND RETURN TO MAIN
                        while keyboard.is_pressed(stop_key) : pass
                        utils.flush_in_buffer()
                        # keyboard.release(stop_key)
                        # time.sleep(0.1)
                        
                        
                        # Detach i/p crnt thread from i/p target_proc_thread 
                        try:
                           win32process.AttachThreadInput(crnt_thread_id , target_proc_id , False)
                        except Exception as e :
                           print(f"ERROR! probably target app has terminated. details:\n {e} \n\n\n RESTARTING KeYRec tool...")
                           return False
                        
                        utils.flush_in_buffer()
                        return True  #success use it later


def count_files(directory= defaults_dict["root_app_path"] + r"\history"):
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
 
def make_data_directory(directory= defaults_dict["root_app_path"]) -> int:
   history_directory = put_user_name(directory+r"\history")
   favorites_directory = put_user_name(directory+r"\favs")
   recent_windows_path = put_user_name(defaults_dict["root_app_path"] + r"\recent_windows.json")
   
   
   #os.system("mkdir..") returns 0 means sucess but else wise it prints to the console! so will check if exists first to avoid un-wanted os module msgs to appear to enduser's console
   mkdir_state = os.system(f"mkdir \"{history_directory}\"") if not os.path.exists(history_directory) else 1 #1 means that couldn't make directory: already exists or any other issues (os.system() returns zero on shell cmd success)
   mkdir_state = (os.system(f"mkdir \"{favorites_directory}\"") if not os.path.exists(favorites_directory) else 1) and mkdir_state #do 'and' with prev mkdir state to ensure return if for both dirs creation status
   
   with open(recent_windows_path, 'a', encoding="utf-8") as tmp:
      pass #olny to create the file if it's isn't there
   
   return mkdir_state


def put_user_name(_path_to_edit: str) -> str:
   user_name = os.environ['USERNAME']
   _path_to_edit = _path_to_edit.replace("%USERNAME%", user_name)
   _path_to_edit = os.path.normpath(_path_to_edit) #normpath()handels forward slashed and etc..
   return _path_to_edit

def process_file_path(isNew = False, _file_dir: str = defaults_dict["root_app_path"] + r"\history", _fav_rec_name : str = None, is_window_names_log= False) -> os.PathLike | str:
   # we'll not call this method unless the dir exist and there is old records so no actual need to handle this check inside this func
   _file_dir = put_user_name(_file_dir)
   
   file_abs_path: os.PathLike | str = None
   if os.path.isdir(_file_dir): #actually it handled on caller but let's make it future proof :D
      
      
      if(not is_window_names_log):
         file_no = count_files(directory= _file_dir)  # files numbering starts with one e.g.(keyrec1) is first file (not needed if file does have name and if file does have name is to be saved in root\favs only!)
         file_name = f"keyrec{file_no + 1 if isNew else file_no}" + ".json" if _fav_rec_name == None else _fav_rec_name + ".json"
      else:
         file_name = defaults_dict["window_log_file"]
         
      file_abs_path = os.path.join(_file_dir, file_name)
      file_abs_path = os.path.normpath(file_abs_path)
      
   return file_abs_path

   
def log_window_name(Wname: str):
   
   file_abs_path: os.PathLike | str = process_file_path(_file_dir= defaults_dict["root_app_path"], is_window_names_log= True)
   
   if os.path.isfile( file_abs_path ) :
      
      try:
         with open(file_abs_path, 'r', encoding="utf-8") as jsonFile:
            window_log_json: str = jsonFile.read()
            _window_log_dict: dict = json.loads(window_log_json)
            
         _window_log_dict[defaults_dict["json_main_key"]].append({Wname.strip(): time.ctime()})
         window_log_json = json.dumps(_window_log_dict, ensure_ascii= False, indent= 4)
      except Exception as e :
         print(f"\n (creating new window log file...: {e})")
         new_json_dict = {defaults_dict["json_main_key"]: [{Wname.strip(): time.ctime()}]}
         window_log_json = json.dumps(new_json_dict, ensure_ascii= False, indent= 4)

         
      with open(file_abs_path, 'w', encoding="utf-8") as jsonFile:
         jsonFile.write(window_log_json)
                          

def save_record(rec_to_save: list, save_dir: str = defaults_dict["root_app_path"], add_to_favorites_list = False, fav_rec_name = None):
   #NOTE: also you can utilize 'keyboard.KeyboardEvent.to_json()'
   
   # save_dir = put_user_name(save_dir)
   
   history_file_path: os.PathLike | str  = process_file_path(isNew= True, _fav_rec_name= None)
   fav_file_path: os.PathLike | str  = process_file_path(isNew= True, _file_dir= save_dir + r"\favs", _fav_rec_name= fav_rec_name)  
   
   
   #turn into a .json convetable dict
   events_dict : dict = dict()
   for i in range(len(rec_to_save)): 
      event = rec_to_save[i]
      
      # attrs: dict = event.__dict__
      # prev attrs var is eq to the below 3 lines but the 3 lines ignores 'None' valued attributes
      event_attrs = dict(
         (attr, getattr(event, attr)) for attr in ['event_type', 'scan_code', 'name', 'time', 'device', 'modifiers', 'is_keypad']
         if not attr.startswith('_') and getattr(event, attr) is not None
         )
      events_dict[str(i)] = event_attrs
      
   #save 
   with open(history_file_path, 'w', encoding="utf-8") as jsonFile:
      events_json: str= json.dumps(events_dict, ensure_ascii= False, indent= 4)
      jsonFile.write(events_json)      
   
   if (add_to_favorites_list):
      with open(fav_file_path, 'w', encoding="utf-8") as jsonFile:
         events_json: str= json.dumps(events_dict, ensure_ascii= False, indent= 4)
         jsonFile.write(events_json)      
   
def get_favs_list(limit= 20) -> list :
   favs_list : list = []
   favs_dir = defaults_dict["root_app_path"] + r"\favs"
   
   favs_dir = put_user_name(favs_dir)
   
   for root, _, files in os.walk(favs_dir): #outer loop will actually loop only once 
      for file in files:
         if (len(favs_list) > limit) : break
         if os.path.isfile(os.path.join(root, file)):
            favs_list += [file]
   
   return favs_list, limit

def print_options(options_list : list):
   
   if(options_list == None):
      return None
   
   _cnt = 0
   print("\n")
   for option in options_list :
      print(f" \t-> '{_cnt}' {option} \n")
      _cnt += 1


def get_windows_names(_limit: int) -> list:
   all_loged_window_names = []
   file_abs_path: os.PathLike | str = process_file_path(_file_dir= defaults_dict["root_app_path"], is_window_names_log= True)
   
   if os.path.isfile( file_abs_path ) :
      with open(file_abs_path, 'r', encoding="utf-8") as jsonFile:
         window_log_json: str = jsonFile.read()
   
   if(window_log_json == None or window_log_json == "") :
      return None
              
   _window_log_dict: dict = json.loads(window_log_json)
   json_ls_pairs = list(_window_log_dict[defaults_dict["json_main_key"]])
   
   for pair in json_ls_pairs :
      for name, time in pair.items():
         all_loged_window_names += [name.strip()] #in accending order (we need to get the most recent so take from end of list )
         
   tot_win_cnt = len(all_loged_window_names)
   can_get_cnt = min(_limit, tot_win_cnt)
   
   n_recent_window_names = []
   lst_idx = tot_win_cnt - 1 # 9
   stop_at_idx = lst_idx - can_get_cnt # 8
   for i in range (lst_idx, stop_at_idx, -1): #take in reverse to put the latest on top of list + skip duplicates + stop at maximum no of windows we can show
      if all_loged_window_names[i] not in n_recent_window_names: 
         n_recent_window_names += [all_loged_window_names[i]]
      else:
         continue  
         
   
   
   n_recent_window_names = n_recent_window_names[0:can_get_cnt]
   
   return n_recent_window_names
   
def flush_in_buffer():
   '''
      * this loop consumes all keyboard library buffer so no control char messes out our tool:
      * NOTE: ref: https://stackoverflow.com/a/2521054/15006369
   '''
   
   while msvcrt.kbhit():
      msvcrt.getch()