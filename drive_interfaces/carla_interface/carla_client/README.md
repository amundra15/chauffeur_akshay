# README #



### What is this repository for? ###




### Installation ( dependencies ) ###

apt-get packages 

python-pygame 
python-protobuf


### Running ### 

The client has an usage test example (carla_manual_control.py) on the master branch that is used just to test communication and the agent control.

You should run it like this:
python carla_manual_control <host> <port>


where host is the ip address of the server
And <port> is the port
After that two consecutive ports are going to used
For instance, if you set port 2000, the system will use ports 
2000,2001,2002

There is a option the enable logs and logs on the stdout.
To have logs saved run with -l option.
To show logs on stdout run with -lv option


### Contribution guidelines ###

