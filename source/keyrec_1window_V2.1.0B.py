
"""
                          Coder : Omar
                          Version : v2.1.1B
                          version Date :  25 / 2 / 2024
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

import scan_vk_codes_dicts as codes
import win32api
import win32gui
import win32con
import win32process
import keyboard
import time
import sys
import os
import msvcrt
import json
import utils
import random


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

def load_last_record(file_dir: str | os.PathLike = r"C:\Users\%USERNAME%\AppData\Roaming\KeyRec_Asda_history") -> list[keyboard.KeyboardEvent]:
   # we'll not call this method unless the dir exist and there is old records so no need to handle this inside
   _events_list: list[keyboard.KeyboardEvent] = []
   
   file_dir = utils.put_user_name(file_dir)
   file_abs_path: os.PathLike | str = utils.process_file_path(_file_dir= file_dir)
      
   if os.path.isfile( file_abs_path ) :
      with open(file_abs_path, 'r') as jsonFile:
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
def new_record(start_key='f5'):
   events: list[keyboard.KeyboardEvent] = []
  
   print("\n\n--------------------------------")
   print(f"\n\n\n-> '{start_key}' to start record. \n-> '{start_key}' again stops record.")
   print("\n\n--------------------------------")
   print(">> ", end="")
   
   while True:
      if keyboard.is_pressed(start_key):
         print("\n\n--------------------------------")
         print("\nSTARTED RECORDING...")

         utils.flush_in_buffer()
         # exprimental: suppress=True the recorded events are not sent to the operating system, effectively blocking them from being observed by other applications
         events = keyboard.record(until=start_key, suppress=True) 

         keyboard.unhook_all()
         print(f"DONE RECORDING! Saving To 'keyrec{str(utils.count_files()+1)}.json'...")
         break
   
   events_done = events[1:-1] #skip the record control key 'start_key' events
 
   utils.save_record(rec_to_save= events_done)
   print(f"\n\nFull Record = ", flush=True)
   [print(event) for event in events_done]
   
   del events
   return events_done


# Replay the key presses to a specific application identified by its PID
def replay_in_window(events: list[keyboard.KeyboardEvent],  key_mapping: dict, replay_key: str = 'f6', stop_key: str = 'f10', window_name: str = "AsdaGlobal"):

   # Set the window name you want to search for

   # Get a handle to the application's main window
   hwnd = win32gui.FindWindow(None, window_name)
 
   if hwnd == False  or window_name == '': #retry
      print("\n\n ##Error Finding Your Window title retry please ...##\n\n")
      return False #use it later
      
 
   tid , pid = win32process.GetWindowThreadProcessId(hwnd)
   crnt_thread_id = win32api.GetCurrentThreadId()
   target_proc_id , _ = win32process.GetWindowThreadProcessId(hwnd)
   
   try:
      # now two threads can share input like keyboard state and crnt focus window
      win32process.AttachThreadInput(crnt_thread_id , target_proc_id , True)
   except Exception as e :
      print(f"ERROR! probably Access is denied try running the tool as admin. details:\n {e}\n\n\n RESTARTING KeYRec tool...")
      return False
 
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
         print("\nSTARTED PLAYING!...")
         # time.sleep(0.1)

         while True:
            #next 2 lines brings window you want to focus and show  it at top most
            # win32gui.SetForegroundWindow(hwnd)
            # events = events[:-1]
    
            for event in events:
               
               if not win32gui.IsWindowVisible(hwnd) :
                  print (f"Note: window minimized or hidden")
     
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
    
               time.sleep(round(random.uniform(0.1, 0.4), 2))
   
               if keyboard.is_pressed(replay_key): #listen while playing if pause key pressed
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
                     f"  -> '{stop_key}'  stop & go to Main menu ")
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
                        
                        print("\nUN-PAUSED! continue PLAYING...")
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

def main_keyrec(state : bool = True) -> bool :
   
   print("\t    ~~~~~~~~~ WELCOME TO (KeyRec - Asda)  by ORS ~~~~~~~~~\n")
   print(
   """
         Coder : Omar
         Version : v2.1.1B
         Code Type : key recorder tool for specific app window
         Title : KeyRec-Asda
         Interpreter : cPython  v3.11.0 [Compiler : MSC v.1933 AMD64]
         EXEd using : pyinstaller module
   
   ~WORKS IF Your GAME OR APP is out of focus even if minimized!! <3~
   ~Key Records is auto saved to: '~\AppData\Roaming\KeyRec_Asda_history'~
   ~~~~~~~~~---~~~~~~~~~---~~~~~~~~~---~~~~~~~~~---~~~~~~~~~---~~~~~~~~~
   """)
   
   #INIT
   key_mapping = get_keys_map_dict()
   utils.make_data_directory()#make it if not exist
   
   #MAIN LOOP
   while state == True : 
      
      #this loop consumes all keyboard library buffer so no control char messes out our tool
      utils.flush_in_buffer()

      #MENU 1 START
      user_choice1: int = utils.recording_menu()
      if user_choice1 == 1 : #new record 
         events = new_record(start_key='f10')
         print (f"num. of key strokes: {len(events)//2}" )
      elif user_choice1 == 2 : #load last record
         events = load_last_record()
         print (f"num. of key strokes: {len(events)//2}" )
         
      elif user_choice1 == 0 : #exit app loop
         state = False
         break
      #MENU 1 END
      else : 
         # os.system('cls')
         print ("\n\n#INVALID INPUT! Restarting tool..\n")
         main_keyrec()
         break
         

      #MENU 2 START
      user_choice2 = utils.target_menu()
      if user_choice2 == 1 : #get window by typing it's name
         utils.flush_in_buffer()
         window_name = str(input("\n\n Enter Your Window name: \n >> ")).strip()
         # keyboard.add_abbreviation("@", window_name) #when you type space will auto type last entered window name
         replay_in_window(events, key_mapping=key_mapping, replay_key='f12',window_name= window_name)
      elif user_choice2 == 2 : #use the default target window
         replay_in_window(events, key_mapping=key_mapping, replay_key='f12')
      #MENU 2 END
         
   print(
      "\n\n\nexiting KeyRec by ORS...\n  \t~R E M A R K S~\nwas made for my childhood game asda-story 1 <3 ... \nfor win not for unix...")
   sys.exit(0)




if __name__ == '__main__':
   main_keyrec()
