import select, socket, sys, pdb
from util import Hall, Room, User, Message
import util

READ_BUFFER = 99999

host = sys.argv[1] if len(sys.argv) >= 2 else ''
listen_sock = util.create_socket((host, util.PORT))

hall = Hall()
connection_list = []
connection_list.append(listen_sock)

while True:
    read_users, write_users, error_sockets = select.select(connection_list, [], [])
    for user in read_users:
        if user is listen_sock: # new connection, user is a socket
            new_socket, add = user.accept()
            new_user = User(new_socket)
            connection_list.append(new_user)
            hall.welcome_new(new_user)

        else: # new message
            msg = user.socket.recv(READ_BUFFER)
            if msg:
                msg = msg.decode().lower()
                hall.handle_msg(user, msg)
            else:
                user.socket.close()
                connection_list.remove(user)

    for sock in error_sockets: # close error sockets
        sock.close()
        connection_list.remove(sock)
