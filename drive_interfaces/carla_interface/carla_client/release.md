Here we Document the latest fixes from the server and client


Release 28_02

Features:

* Now the impact ( called colision) is divided between general, pedestrian and cars

Bug Fixes:

* No more problems with police cars and mercedes
* Fixed a bug that made impossible to colide with pedestrians


Release 27_02

Features:

* More possible positions being sent
* New cars were added.
* Added rain to the system.


Bug Fixes
* Now the server sends the size  of the possible positions vector 
* Changed the client to avoid race conditions


Release 24_02

Features:

* New pedestrians added

Release 20_02

Features:

* Ports are now selected again by command line
* Now you can control physics simulation step	
	* You can set the parameter to tell how much time goes between frames.
* Added: Unity Vector with car orientation with respect to the world coordinate system


Bug Fix

* Bug Fix on client queue






Relase 17_02

Bug Fixes:

* Solved the problem with wroing starting position coordinates being received.


Features: 

* Added configuration file on the server ( config.conf) it is located
at $(server_path)/2017_02_17_Linux_Data/StreamingAssets/Carla
	* There you can control the pedestrian density  ( number of pedestrian in the city)
	* You can control the car density ( number of the cars in the city )
	* If the NPC should stop on traffic light
	* The physics simulation speed
* Now clients can disconect and reconect again.
* The server will never reset the simulation, everything should be controled by the client.
* When a new episode is asked the client now has to wait for a "END_RESET" message in order to continue.
* Mode with many cameras and depth ( german) and one camera (alexey) now can be selected by sending "1" for german and "0" by alexey at 
the begining of the simulation





