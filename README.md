PROJECT NAME: ARL Battlespace

PROJECT DESCRIPTION: A Python strategy game, similar to Axis and Allies, Battleship, and chess. It is a simple wargame with two teams of two players each, i.e. two humans versus two AIs. The purpose is to provide a flexible platform to develop novel AIs for command and control decision aids. The AIs in this game take random actions, either from a uniform distribution or from a human-derived distribution. The focus of this project is to modify the AIs based on reinforcement learning, and in particular to tackle multiplayer decision-making.


Version number:  1.2   A text-based game with visualization
System requirements: 	Python 3, conda install dill, pip install tk

Copyright 2021 U.S. Army Research Laboratory:  
	 	 MIT Open Source License 
            https://opensource.org/licenses/MIT

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

ARL Battlespace is to be released as open source software for promoting its commercial and non-commercial use. It is not intended to become the subject of any patent application or license. All patent rights ARL may be able to assert or establish are hereby waived.


Credits: J. Zach Hare, B. Christopher Rinderspacher, Walter Peregrim, Sue E. Kase, Simon M. Su, and Chou P. Hung, U.S. DEVCOM Army Research Laboratory


Due to COVID restrictions, and consistent with the ARL 20-119 Exemption Determination Letter, any game play with people outside your household (friends or co-workers) must be remote or via Teams (e.g. by telephone or an online app).

Contact: Chou Hung (chou.p.hung.civ@mail.mil)

--

This repo contains the source code to the wargame ARL Battlespace. The configuration is 1 server + 2 clients, i.e. one standalone machine or multiple machines across a network, on Windows, Mac, Linux platforms.

# Setting up
1) Install Python (e.g. 3.7.9) and Anaconda (e.g. 4.9.2)
2) conda install dill
3) pip install tk

# Running Two Humans vs. UniformRandomAgent AI, Capture-the-Flag game with Wall (minefield)
The two humans begin in the North quadrants, and the 2 AI players begin in the South quadrants. Each player has 3 ground units, 1 air unit, and a flag. The opposing forces are separated by a minefield with a gap. The humans should cooperate to breach the gap and destory the enemy forces or capture the flags. Units have limited visibility.


1) Open 2 terminal windows. One will be the Server, and the other will be Client 1 (i.e. Player 1, a.k.a. 'Agent 2')

2) In terminal 1 ('Server'), navigate to the 'test' folder.

3) Start the server by typing: python ServerWithUI.py --test
	Note your Server's external IP address (e.g. 71.114.23.43) and your server's local IP address (e.g. 192.168.1.13)

4) If one or both clients are communicating with the server across a network, modify your server's router's Port Forwarding so that port 5050 is forwarded to your server's local IP address.

5) In terminal 2 ('Client 1'), navigate to the 'test' folder.  Type:  python HumanInterface.py
(Because terminal 2 is on the same machine as terminal 1): Hit <enter>.  It will automatically reach out to your server on the same machine.

6) In terminal 3 ('Client 2', a.k.a. 'Agent 3'), navigate to the 'test' folder. Type:  python HumanInterface.py
<If terminal 3 is on a computer across the network>: Type the address of the server, i.e. 71.114.23.43.
<If terminal 3 is on the same computer as the server>: Hit <enter>.

7) Player 1 (i.e. 'Agent 2') begins clicking on the yellow region to place units (3 ground, 1 air, 1 flag). Alert Player 2 to begin placing units.

8) Player 2 (i.e. 'Agent 3') waits for Player 1 to finish placing units. Player 2 then begins clicking on the yellow region to place units.

9) Player 1 enters actions into the terminal.  Ground and air units can advance, turn, and fire missiles. Ground units can also ram (advance 1 step and attack). Ground units can capture the flag, but they cannot run into walls (mine fields). Air units can bomb the square directly below and fly over walls (mine fields), but cannot capture the flag.

10) Player 2 enters actions into the terminal

11) Game ends when both enemy flags are captured, or all enemy ground units are destroyed.


CITATIONS:  

1.    Hare JZ, Rinderspacher BC, Kase S, Su S & Hung CP (2021) Battlespace: using AI to understand friendly vs. hostile decision dynamics in MDO. Proc. SPIE 11746, Artificial Intelligence and Machine Learning for Multi-Domain Operations Applications III. 1174615 (12 April 2021); https://doi.org/10.1117/12.2585785.

https://www.spiedigitallibrary.org/conference-proceedings-of-spie/11746/1174615/Battlespace--using-AI-to-understand-friendly-vs-hostile-decision/10.1117/12.2585785.full?SSO=1


2.    Su S, Kase S, Hung C, Hare JZ, Rinderspacher BC & Amburn C (2021) Mixed Reality Visualization of Friendly vs Hostile Decision Dynamics. In: Chen J.Y.C., Fragomeni G. (eds) Virtual, Augmented and Mixed Reality. HCII 2021. Lecture Notes in Computer Science, vol 12770, Springer, Cham.  https://link.springer.com/chapter/10.1007/978-3-030-77599-5_37 
