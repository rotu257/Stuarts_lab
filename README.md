# Stuarts_lab
Python based codes to automize Stuart's lab

Available instruments:
	
	Scope:
		- DPO4104     (ethernet)
		- DSA91304a  (ethernet) => codes available also to plot interactively spatio-temporal diagrams
	
	Controller:
		- ITC_4001      (usb)   (very basic, only able to modify the current)
		- SIM900         (GPIB)
		- TGA_12104   (usb)
		- TLB_6700      (usb)
		- agilent33220a (ethernet)		

Notes:

    - Some of the codes are very basic and/or in test phase => please report problems/suggestions to Bruno
    - All the codes are not very well documented yet.
    - Be sure to have all the necessary python libraries
        notably: pyvisa, pyvisa-py (backend @py de pyvisa), pyusb, appropriate GPIB libraries for your OS (linux-gpib for linux)
        Other helpful libraries: matplotlib, numpy, scipy, time, math, ...
    - Have a look on Prog_Guide folder if you want to implement your own functions and help improve the repository


To setup one of the code for using in Windows OS, assuming the code is called mycode.py:

    1) - If the code is already called mycode_WINDOWS.py then you can skip steps 1) and 2).
    Otherwise, please copy the code to a new one following the next example:
    mycode.py => mycode_WINDOWS.py
    The bash command is simply: cp mycode.py mycode_WINDOWS.py

    2) - Open the code in a text editor and modify the first line:
    from: #!/usr/bin/python
    to: #!/c/Python27/python.exe

    For this step be sure your python executable is well located to the new path you are providing (/c/Python27/python.exe).

    Then please update the github repository adding the new file.

    After this step the code should be working calling it from its own directory (only locally): ./mycode_WINDOWS.py -[options] argument

    3) - If it does not currently exist, please create a folder called bin to your root location (called ~ in bash).
    To identify your root: - open a bash prompt
                                     - type the command: cd (that will bring you to the right location where you should already be if the prompt was just opened)
                                     - type the command: pwd (to know the path of it)

    To create the directory, go to your root (cd), and type the following command: mkdir bin (where bin is the name of the created folder)
    Its path will be ~/bin (~ is a shortcut for something like /c/your_name/)

    4) - Add the last created directory to the environment variable called PATH. Accessible from Windows's configuration panel.

    5) - Go to the ~/bin and create a global link by typing a command similar to:

    ln -s FULLPATH/mycode_WINDOWS.py mycode             (mycode will be the name of the link)

    Please note that _WINDOWS has been remove from the link name for self coherence with linux system.

    You will then be able to call the executable from everywhere simply typing: mycode
