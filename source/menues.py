"""
                          Coder : Omar rs
                          Version : v2.1.2B
                          version Date :  19 / 6 / 2024
                          Code Type : key recorder app for specific app window
                          Title : KeyRec-Asda
                          Interpreter : cPython  v3.11.0 [Compiler : MSC v.1933 AMD64]
                          EXE using : pyinstaller module
"""

import sys
import utils
import os


def get_fav_rec_events():
   utils.flush_in_buffer()
   favs_ls, limit =  utils.get_favs_list()
   print(f"(showing top {limit} favorite records...)")
   print("\n\n--------------------------------")
   print("\nC H O O S E   R E C O R D: ")
   utils.print_options(favs_ls)
   print("\n\n--------------------------------")
   
   fav_idx =  int(input(">> ").strip())
   invaild_option_check = fav_idx >= len(favs_ls) or fav_idx < 0
   if(invaild_option_check):
      print("\n( ERROR! INVALID INPUT! \nretry please...)")
      return get_fav_rec_events()
   else:# ok! valid input!
      fav_rec_name: str = favs_ls[fav_idx][0:-5] #get the file name only with out extension ',jons'
      
      _events = utils.load_record(utils.defaults_dict["root_app_path"] + r"\favs", fav_rec_name)
         
      return _events
      
      
   
   
def get_one_of_recent_windows() -> str:
   utils.flush_in_buffer()
   limit = 10
   windows = utils.get_windows_names(_limit = limit)
   print(f"(showing last {limit} different used Windows...)")
   print("\n\n--------------------------------")
   print("\nC H O O S E   R E C O R D: ")
   print("NO Options") if windows == None else utils.print_options(windows)
   print("\n\n--------------------------------")
   option_idx = int(input(">> ").strip())
   
   invalid_option_check = (windows == None or option_idx < 0 or option_idx >= len(windows))
   if invalid_option_check:
      print(f"\n ERROR! invalid input! \nretry please...")
      return get_one_of_recent_windows()
   else:# ok! valid input!
      chosen_window_name = windows[option_idx]
      return chosen_window_name
 
 
def recording_menu() -> int:
   _user_choice :int = None
   
   IsFirstRec = not bool(utils.count_files())
   IsFirstFav = not bool(utils.count_files(directory= utils.defaults_dict["root_app_path"] + r"\favs"))
   
   print("\n\n--------------------------------")
   print("\n\n C H O O S E: ")
   print(f"\n-> '1' New Record ") 
   print(f"\n-> '2' Use last Record ")  if not IsFirstRec else print("", end="")
   print(f"\n-> '3' Favorite Records ") if not IsFirstFav else print("", end="")
   print("\n-> '0' Exit ")
   print("\n\n--------------------------------")
   
   try:
      utils.flush_in_buffer()
      _user_choice: str = input(">> ").strip()
      
      if not _user_choice.isnumeric(): raise Exception
      _user_choice = int(_user_choice)
      
      if _user_choice < 0: raise Exception
      if IsFirstRec and _user_choice >= 2: raise Exception #handle if user choosed 2 even if the option is hidden
      if IsFirstFav and _user_choice >= 3: raise Exception #handle if user choosed 3 even if the option is hidden
        
   except Exception as e:
      # os.system("cls")
      print(f"\n ERROR! you've mostly entered an invalid input! \nReloading...")
      _user_choice = recording_menu()
         
   return _user_choice

def target_menu() -> int:
   _user_choice2 :int = None
   
   while True :
      winLogFile = utils.put_user_name(utils.defaults_dict["root_app_path"] + '\\' + utils.defaults_dict["window_log_file"])
      IsFrstWindow = 1 if os.path.getsize(winLogFile) == 0 else 0
      
      utils.flush_in_buffer()
      print("\n\n--------------------------------")
      print("\n\n C H O O S E: ")
      print("\n\n-> '1' Play KeyRec on custom window")
      print("\n-> '2' Play KeyRec on Asda Story window")
      print("\n-> '3' Show recent used Windows") if not IsFrstWindow else print("", end="")
      print("\n-> '0' Exit ")
      print("\n\n--------------------------------")
      _user_choice2 =  input(">> ")

      if _user_choice2.isnumeric() and  0 <= int(_user_choice2) <= (3 if not IsFrstWindow else 2) :
         break
      else :
         print ("\n\n(ERROR! INVALID INPUT!) \nretry please...")
         _user_choice2 = target_menu()
         
   return int(_user_choice2)


def main_keyrec(state : bool = True) -> bool :
   
   print("\t    ~~~~~~~~~ WELCOME TO (KeyRec - Asda)  by ORS ~~~~~~~~~\n")
   print(
   """
         Coder : Omar
         Version : v2.1.2B
         Code Type : key recorder tool for specific app window
         Title : KeyRec-Asda
         Interpreter : cPython  v3.11.0 [Compiler : MSC v.1933 AMD64]
         EXEd using : pyinstaller module
   
       ~WORKS IF Your GAME OR APP is out of focus even if minimized!! <3~
        ~KeyRec data is auto saved to: '~\AppData\Roaming\KeyRec_Asda\\'~
     ~~~~~~~~~---~~~~~~~~~---~~~~~~~~~---~~~~~~~~~---~~~~~~~~~---~~~~~~~~~
   """)
   
   #INIT
   key_mapping = utils.get_keys_map_dict()
   utils.make_data_directory()#make it if not exist
   
   #MAIN LOOP
   while state == True : 
      
      #this loop consumes all keyboard library buffer so no control char messes out our tool
      utils.flush_in_buffer()

      #MENU 1 START
      user_choice1: int = recording_menu()
      if user_choice1 == 1 : #new record 
         events = utils.new_record(start_key='f10')
      elif user_choice1 == 2 : #load last record
         events = utils.load_record()
      elif user_choice1 == 3 : #show favs then get the chosen record(dont show all! only until the internal show limit)
         events = get_fav_rec_events()
      elif user_choice1 == 0 : #exit app loop
         state = False
         break
      #MENU 1 END
      else : 
         # os.system('cls')
         print ("\n\n#INVALID INPUT! Restarting tool..\n")
         main_keyrec()
         break
      
      print (f"num. of key strokes: {len(events)//2}" )
         

      #MENU 2 START
      user_choice2 = target_menu()
      if user_choice2 == 1 : #get window by typing it's name
         utils.flush_in_buffer()
         window_name = str(input("\n\n Enter Your Window name: \n >> ")).strip()
         # keyboard.add_abbreviation("@", window_name) #when you type space will auto type last entered window name
         utils.replay_in_window(events, key_mapping=key_mapping, replay_key='f12',window_name= window_name)
      elif user_choice2 == 2 : #use the default target window
         utils.replay_in_window(events, key_mapping=key_mapping, replay_key='f12')
      elif user_choice2 == 3 : #show recent 5 used windows and try play on one of them 
         window_name = get_one_of_recent_windows()
         utils.replay_in_window(events, key_mapping=key_mapping, replay_key='f12')
      elif user_choice2 == 0 : #exit app loop
         state = False
         break
      #MENU 2 END
         
   print(
      "\n\n\nexiting KeyRec by ORS...\n  \t~R E M A R K S~\nwas made for my childhood game asda-story 1 <3 ... \nfor win not for unix...")
   sys.exit(0)