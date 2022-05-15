import socket
import threading
import time
server_address = '127.0.0.1'   # server IP address
server_port = 65432            # server port number
thread_number = 1
num_of_clients = 0
is_time_calculated = False
t_end = 0
"""
Function to handle GET and POST requests ( send responses, search for files,...)
"""


def set_timeout(num_clients):
    time_out = 10 / num_clients
    return time_out


"""
Function for pipelining
"""


def handle_request(request):
    method_type = request.split()[0]
    if method_type == 'GET':
        #headers = request.split('\n')
        filename = request.split()[1]
        filename = filename.replace('/', '')
        try:
            file = open(filename)
            content = file.read()
            file.close()
            response = 'HTTP/1.1 200 OK\r\n\r\n' + content + '\r\n'
        except FileNotFoundError:
            response = 'HTTP/1.1 404 NOT FOUND\r\n\r\nFile Not Found\r\n'
    elif method_type == 'POST':
        filename = request.split()[1]
        filename = filename.replace('/', '')
        body = request.split('\r\n\r\n')[1]
        content = body.split('\r\n')[0]
        with open(filename, 'w') as f:
            f.write(content)
        response = 'HTTP/1.1 201 Created\r\n\r\n'
    return response


class ClientThread(threading.Thread):
    def __init__(self, client_address, client_socket):
        threading.Thread.__init__(self)
        print('[SERVER] Starting Thread # ', thread_number)
        self.c_socket = client_socket
        self.c_address = client_address
        print('[SERVER] New connection started from: ', self.c_address)

    def run(self):
        global is_time_calculated
        global num_of_clients
        global t_end
        print('[SERVER] Processing connection from: ', self.c_address)
        while True:
            data = self.c_socket.recv(2048)
            message = data.decode()
            if message == '':
                if is_time_calculated and time.time() >= t_end:
                    break
                elif is_time_calculated is False:
                    timeout = set_timeout(num_of_clients)
                    t_end = time.time() + timeout
                    is_time_calculated = True
                    continue
            else:
                print('[SERVER] Message: ', message, ' from client', self.c_address)
                server_response = handle_request(message)
                self.c_socket.sendall(server_response.encode())
                print('[SERVER] DATA SENT')
        print('[SERVER] Client from ', self.c_address, ' disconnected')
        is_time_calculated = False
        self.c_socket.close()


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((server_address, server_port))
    print('[SERVER] Started')
    print('[SERVER] Waiting for connection')
    s.listen()
    print('[SERVER] listening on port %s....' % server_port)
    while True:
        client_connection, client_address = s.accept()
        new_thread = ClientThread(client_address, client_connection)
        thread_number += 1
        num_of_clients = num_of_clients + 1
        new_thread.start()

    s.close()
