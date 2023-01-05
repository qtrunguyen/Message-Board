A project for class CS 4065 - Computer System

* How to use:
- The only need is the code files and Python3 downloaded to your computer

- To run the server, type in terminal 

    python server.py 127.0.0.1 

(127.0.0.1 is an example of a host ip address, can use any address)

- To run the client, type in another terminal

    python client.py 127.0.0.1

(host ip need to match the ip of server)

* Instructions:
When a client is run, it require user to enter an user name. After entering the name, these command instructions will prompt:

    <rooms> : to list all rooms
    <join> room_name : to join/create a room (create one if there is not any of that name yet)
    <post> room_name subject content : to post a message to a group
    <leave> room_name : to leave a room
    <users> room_name : to list all users in room room_name
    <msg> room_name id : to retrieve the content of id in a room
    <quit> : to quit the server

Initially there aren't any rooms yet, but to achieve the goal of part 2 (which has 5 rooms in the server)
users can create 5 rooms using <join> command

-----------MAJOR ISSUES-------------
For the first part, our primary issues is with broadcasting the message, since python need to encode
to byte types for all the message in order to sendout to other users, which we did not know that in 
the first place

For second part, we first initially thought that we need an user need to have multiple socket to connect to multiple
chat rooms, but this is a wrong approach. We take a different approach by having this "Hall->Room->Users" system,
where Hall manage the commands, while Room can broadcast the message to only the users in that room.