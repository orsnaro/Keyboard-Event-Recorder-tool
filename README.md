 # <center> Keyboard-Event-Recorder-tool 
* ### **Brief:**
Automation tool that records any given keyboard events 
  and plays them to any specific window / game  .  _Try the tool now!_ ***[Latest Release](https://github.com/orsnaro/Keyboard-Event-Recorder-tool/releases/tag/%23Keyboard)***
	
---
> #### **📞FAQ**

1) ##### _Where To Find my Game/App title name?_
	* dont get the name from task maneger they are mostly in-accurate(Mostly a proccess name  not a Window name) instead  ***for now***   use this tool: Window spy in [`AutoHotkey`](https://www.autohotkey.com/)
	to get accurate title name  by hovering on your app
  
  ----
  
  > #### **📣About Version:**
  
   * tested using ***OS:*** win10 | ***Keyboard:*** Redragon Daksa : K576R-1 blue sw. )
   * Interpreter : cPython  v3.11.0 [Compiler : MSC v.1933 AMD64]	 |	EXE using : pyinstaller module
	

![tool icon image](./KeyRec.ico)

----

> #### **✨Features :**

* -default is asda story game window my childhood game 💙- 

* works silent even if target window is:
  - out of focus ,
  - not full screen , 
  - minimized  

* wont affect any other proccess or active windows  on pc 

* experimental: even inside same game or app! you will be able to chat  and use child windows freely  while app send keys record to the app/ game and automate it! 

* tool can run in multiple instances to control multiple windows or apps!

* can puase and un-puase it  any time

* random timing between key strokes 

* works perfectly with asda story game which was main goal of tool 

-----

> #### **✨UPCOMING FEATURES:**

* Select app by Enter its PID in Task manager (very soon)
* Select App from A Window Title list
* Select App By pointing to it using mouse hover on App
* Record mouse keys
* Control timing between key strokes 
* choose from History of 5 last used Games/App in tool
* More User Friendly GUI 
* <details>
	<summary><em>  Special </em> </summary>
	
  for Asda Story game => track adreesses of gold / exp /hp/mp/ items ) to automate tasks more accuratly
 </details> 
	
----
	
> #### **🐞Known Bugs :**

* Some Window Titles in tskmgr are inaccurate  (proccess might not have a window or other issue)
	- somtimes we hook the Window but it ignores `post message `
* At recording somtimes record get flushed to console after done recording causing   UB (mostly cuz of holding a key a bit long though it's not that frequent at all any more like prev versions)ttT
* recording combined keys not working


----
  <sub> &emsp;&emsp;📍 I found that most _known_ key-recording tools is  might be not working at all as I wanted so I made my self one in ~3hours💙 , exe for both versions in : [Tool-dir](https://github.com/orsnaro/Keyboard-Event-Recorder-tool/tree/master/KeyRec-tool/)  📍 &emsp; </sub> 
