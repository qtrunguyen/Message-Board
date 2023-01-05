import socket, pdb
import datetime

MAX_CLIENTS = 30
PORT = 22222
QUIT_STRING = '<$quit$>'

def create_socket(address):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setblocking(0)
    s.bind(address)
    s.listen(MAX_CLIENTS)
    print("Now listening at ", address)
    return s

#A server has a "Hall", each "Hall" contain multiple "Rooms", and each room contain multiple "Users"
#Defining Hall class
class Hall:
    def __init__(self):
        self.rooms = {} # {room_name: Room}
        self.room_user_map = {} # {userName: roomName}

    #welcome new users
    def welcome_new(self, new_user):
        new_user.socket.sendall(b'Please tell us your name:\n')

    #function to list all users in a room
    def list_rooms(self, user):
        if len(self.rooms) == 0:
            msg = 'No active rooms currently. Create your own!\n' \
                + 'Use [<join> room_name] to create a room.\n'
            user.socket.sendall(msg.encode())
        else:
            msg = 'Listing current rooms\n'
            for room in self.rooms:
                msg += room + ": " + str(len(self.rooms[room].users)) + " user(s)\n"
            user.socket.sendall(msg.encode())
    
    #function to define all the commands
    def handle_msg(self, user, msg):
        
        instructions = b'Instructions:\n'\
            + b'<rooms> : to list all rooms\n'\
            + b'<join> room_name : to join a room. If there is not any, create new room with that name\n' \
            + b'<post> room_name subject content : to post a message to a group\n' \
            + b'<leave> room_name : to leave a room\n' \
            + b'<users> room_name : to list all users in room room_name\n' \
            + b'<msg> room_name id : to retrieve the content of id in a room\n' \
            + b'<quit> : to quit the server\n' \
            + b'\n'

        print(user.name + " says: " + msg)
        if "name:" in msg:
            name = msg.split()[1]
            user.name = name
            print("New connection from:", user.name)
            user.socket.sendall(instructions)

        #command to join a room
        elif "<join>" in msg:
            same_room = False
            if len(msg.split()) >= 2:
                room_name = msg.split()[1]
                if user.name in self.room_user_map:
                    if self.room_user_map[user.name] == room_name: # If the user already in the room
                        user.socket.sendall(b'You are already in room: ' + room_name.encode() + b"\n")
                        same_room = True
                if not same_room:
                    if not room_name in self.rooms: # create a new room if there is not one yet
                        new_room = Room(room_name)
                        self.rooms[room_name] = new_room
                    self.rooms[room_name].users.append(user)
                    self.rooms[room_name].welcome_new(user)
                    self.room_user_map[user.name] = room_name
            else:
                user.socket.sendall(instructions)

        #command to list all the rooms
        elif "<rooms>" in msg:
            self.list_rooms(user) 
        
        #command to quit server
        elif "<quit>" in msg:
            user.socket.sendall(QUIT_STRING.encode())
            self.remove_user(user)

        #command to leave a group
        elif "<leave>" in msg:
            if len(msg.split()) >= 2:
                room_name = msg.split()[1]
                if user.name in self.room_user_map:
                    # if self.room_user_map[user.name] == room_name:
                    self.rooms[room_name].remove_user(user)
                    self.room_user_map.pop(user.name)
                    user.socket.sendall(b'You left the room ' + room_name.encode() + b"\n")
                    # else:
                    #     user.socket.sendall(b'You are not in the room ' + room_name.encode() + b"\n")
            else:
                user.socket.sendall(instructions)
        
        #command to get list of users in a group
        elif "<users>" in msg:
            if len(msg.split()) >= 2:
                room_name = msg.split()[1]
                user.socket.sendall(b'Users in room ' + room_name.encode() + b':')
                for p in self.rooms[room_name].users:
                    user.socket.sendall(b' ' + p.name.encode())
                user.socket.sendall(b"\n")
            else:
                user.socket.sendall(instructions)

        #command to retrieve a message
        elif "<msg>" in msg:
            if len(msg.split()) >= 3:
                room_name = msg.split()[1]
                msg_id = msg.split()[2]
                if user.name in self.room_user_map:
                    if self.room_user_map[user.name] == room_name:
                        m = self.rooms[room_name].messages[int(msg_id)]
                        user.socket.sendall(b'Content in id ' + msg_id.encode() + b': ' + m + b"\n")
                    else:
                        user.socket.sendall(b'You are not in the room ' + room_name.encode() + b"\n")
            else:
                user.socket.sendall(instructions)

        #command to post a message      
        elif "<post> in msg":
            if len(msg.split()) >= 4:
                room_name = msg.split()[1]
                subject = msg.split()[2]
                m = msg.split()[3:]
                msg_string = ' '.join([str(elem) for elem in m])
                if user.name in self.room_user_map:
                    # if self.room_user_map[user.name] == room_name:
                    self.rooms[room_name].broadcast(user, msg_string.encode())
                    # else:
                    #     user.socket.sendall(b'You are not in the room ' + room_name.encode() + b"\n")
                else:
                    msg = 'You are currently not in any room! \n'
                    user.socket.sendall(msg.encode())
            else:
                user.socket.sendall(instructions)
    
    #function to remove an user from a group
    def remove_user(self, user):
        if user.name in self.room_user_map:
            self.rooms[self.room_user_map[user.name]].remove_user(user)
            del self.room_user_map[user.name]
        print("user: " + user.name + " has left\n")

#Room class   
class Room:
    def __init__(self, name):
        self.users = []
        self.name = name
        self.messages = []

    def welcome_new(self, from_user):
        msg = self.name + " welcomes: " + from_user.name + '\n'
        for user in self.users:
            user.socket.sendall(msg.encode())
    
    #broadcast the message to the group
    def broadcast(self, from_user, msg):
        self.messages.append(msg) #store in a message list
        id = max(index for index, m in enumerate(self.messages) if m == msg) #message id
        time = datetime.datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)") #time stamp
        msg = from_user.name.encode() +  b", " + str(id).encode() + b", " + time.encode() + b": " + msg + b"\n"
        for user in self.users:
            user.socket.sendall(msg)

    def remove_user(self, user):
        self.users.remove(user)
        leave_msg = user.name.encode() + b"has left the room\n"
        self.broadcast(user, leave_msg)

#User class
class User:
    def __init__(self, socket, name = "new"):
        socket.setblocking(0)
        self.socket = socket
        self.name = name

    def fileno(self):
        return self.socket.fileno()

class Message:
    def __init__(self, msg, id):
        self.msg = msg
        self.id = id
        
