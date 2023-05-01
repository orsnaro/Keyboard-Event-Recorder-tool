
"""
								  Coder : Omar
								  Version : v2.0.5B
								  version Date :  29 / 4 / 2023
								  Code Type : key recorder app for specific app window
								  Title : KeyRec-Asda
								  Interpreter : cPython  v3.11.0 [Compiler : MSC v.1933 AMD64]
								  EXE using : pyinstaller module
"""
#TODO : easy: user choose timing (easy if timing range is const between all strokes) (each event has time since epoch)
#TODO : easy:  export and import .Key_Rec files (could use pandas or save to csv)
#TODO : depends: OOP it 
#TODO : mid: GUI it
#TODO : mid-hard: mouse recording
#TODO : fix Some windows titles could not be found easily 

import scan_vk_codes_dicts as codes
import win32api
import win32gui
import win32con
import win32process
import keyboard
import random
import time
import sys
import os
import msvcrt

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


# Record the key presses
def record(start_key='f5'):
	events: list = []
  
	print(
		f"\n\n\n-> '{start_key}' to start record. \n-> '{start_key}' again stops record.")
	while True:
		if keyboard.is_pressed(start_key):
			print("\nSTARTED RECORDING...")
   
			events = keyboard.record(until=start_key)
			keyboard.unhook_all()
			print("DONE! RECORDING...")
			break
	
	events_done = events[1:-1]
	print(f"\n\nFull Record = \n {events_done} " , flush=True)
	return events_done


# Replay the key presses to a specific application identified by its PID
def replay_in_window(events,  key_mapping: dict, replay_key: str = 'f6', stop_key: str = 'f10', window_name: str = "Asdastory (ME)"):

	# Set the window name you want to search for

	# Get a handle to the application's main window
	hwnd = win32gui.FindWindow(None, window_name)
 
	if hwnd == False  or window_name == '': #retry
		print("\n\n ##Error Finding Your Window title retry please ...##\n\n")
		return False #use it later
		
 
	tid , pid = win32process.GetWindowThreadProcessId(hwnd)
	crnt_thread_id = win32api.GetCurrentThreadId()
	target_proc_id , _ = win32process.GetWindowThreadProcessId(hwnd)
 
	# now two threads can share input like keyboard state and crnt focus window
	win32process.AttachThreadInput(crnt_thread_id , target_proc_id , True)
 
	# Get the dimensions of the application's main window
	rect = win32gui.GetWindowRect(hwnd)
	print(f"\n your '{window_name}' window shape: {rect}")

	print(
		f"\n\n\n-> '{replay_key}' to start replay. \n-> '{replay_key}' again pauses replay")

	while True:
		if keyboard.is_pressed(replay_key):
			print("\nSTART RE-PLAYING...")
			time.sleep(0.2)

			while True:
				#bring window you want to focus and show  it at top most
				# win32gui.SetForegroundWindow(hwnd)
				# events = events[:-1]
    
				for event in events:
					# convert gotten physical key code( scan code ) to vk code and pass booth
					scan_code = event.scan_code
					vk_code   = win32api.MapVirtualKey( scan_code , 1) #map or convert  scan code to vk code
					key_name  = next((key for key , val in codes.VK_CODES.items() if val == vk_code), None) #return first elmnt if there is multiple
					#NOTE: clearing ambiguity of  next() name! 
					# When you create an iterator object from an iterable using the iter() function, the iterator is positioned before the first element in the sequence.

					if event.event_type == keyboard.KEY_DOWN:
						msg = win32con.WM_KEYDOWN
						wparam = vk_code #WPARAM = WORD PARAMETER but 32bit actually XD use .bit_length()
						lparam = (scan_code << 16) | 1 #LONG PARAMETER : #FOR KEY DOWN  RMB must set to 1 (little endian)
						win32gui.PostMessage(hwnd, msg, wparam, lparam)

					elif event.event_type == keyboard.KEY_UP:
						msg = win32con.WM_KEYUP
						wparam = vk_code
						# scan_code is 8bit originally
						lparam = (1 << 31) | (scan_code << 16)#little endian :FOR KEY UP LMB must be set to 1 
						win32gui.PostMessage(hwnd, msg, wparam, lparam)

					time.sleep(round(random.uniform(0.1, 0.4), 2))
	
					if keyboard.is_pressed(replay_key):
						keyboard.release(replay_key)
						time.sleep(0.2)
						os.system("cls") 
						print("\nPAUSED RE-PLAYING...")
						print(
							f"\n  '{replay_key}' again to UN-PAUSE")
						print(
							f"  -> '{stop_key}'  stop & go to Main menu ")
		
						while True :
							if keyboard.is_pressed(replay_key):
								keyboard.release(replay_key)
								time.sleep(0.2)
								print("\nUN-PAUSED continue RE-PLAYING...")
								break

							elif keyboard.is_pressed(stop_key):
								time.sleep(0.2)
								print(
									"\n\n\nexiting KeyRec by ORS...  \nwas made for my childhood game asda-story <3 ... \nfor win not for unix...")
		
								# Detach i/p crnt thread from i/p target_proc_thread 
								win32process.AttachThreadInput(crnt_thread_id , target_proc_id , False)
								return True  #success use it later

def main_keyrec(state : bool = True) -> bool :
   
	print("\t    ~~~~~~~~~ WELCOME TO (KeyRec - Asda) v2.0.5B by ORS ~~~~~~~~~\n")
	print(
	"""
			Coder : Omar
			Version : v2.0B
			Code Type : key recorder app for specific app window
			Title : KeyRec-Asda
			Interpreter : cPython  v3.11.0 [Compiler : MSC v.1933 AMD64]
			EXE using : pyinstaller module
	
	~WORKS IF Your GAME OR APP is out of focus even if minimized!! <3~
	""")

	while state == True : 

		events = record(start_key='f10')
		key_mapping = get_keys_map_dict()
		print (f"num. of key strokes: {len(events)//2}" )

		#this loop consumes all keyboard library buffer so no control char messes out our tool
		for i in range( len(events)//2 + 2): #for some reason it exists before last two
			msvcrt.getch()

		# ok = input("\n\npress 'Enter' to continue or '1' to re-record...") #dummy to take events all chars buffer and avoid print any control char
		# True if ok == '' else  main_keyrec() 
		choice = None
		while True :
			choice =  input("\n\n (1) Use on custom window \n (2) Use on Asda Story window \r\n choice: ")
			if choice.isnumeric() :
				break;
			else :
				print ("\n\n#INVALID INPUT! RETRY#")
				
		choice = int(choice)
		if choice == 1 :
			window_name = str(input("\n\n Enter Your Window name: \n")).strip()
			replay_in_window(events, key_mapping=key_mapping, replay_key='f12',window_name= window_name)
		else :
			replay_in_window(events, key_mapping=key_mapping, replay_key='f12')
    
		print(f"\n\n\n-> '1' New Record \n-> '0' Exit ")
		state = bool(input())
		os.system("cls")

	sys.exit(0)




if __name__ == '__main__':
	main_keyrec()
