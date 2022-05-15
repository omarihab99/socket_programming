import socket
import sys
cached_requests = dict()
socket_exist = False


def convert_to_http_request(requests_list):
    requests = []
    j = 0
    for i in range(len(requests_list)):
        if requests_list[i][j] == 'GET':
            request = requests_list[i][j] + ' ' + requests_list[i][j+1] + ' ' + 'HTTP/1.1' + '\r\n' + 'Host: ' + requests_list[i][j+2] + ':' + requests_list[i][j+3] +'\r\n\r\n'
            requests.append(request)
        elif requests_list[i][j] == 'POST':
            content = read_POST_request_file(requests_list[i][j + 1])
            request = requests_list[i][j] + ' ' + requests_list[i][j + 1] + ' ' + 'HTTP/1.1' + '\r\n' + 'Host: ' + requests_list[i][j + 2] + ':' + requests_list[i][j + 3] + '\r\n\r\n' + content + '\r\n'
            requests.append(request)

    return requests


def read_POST_request_file(filename):
    filename = filename.replace('/', '')
    with open(filename, 'r') as file:
        content = file.read()
        return content


def read_input_file_content(filename):
    test_list = []
    with open(filename, 'r') as file:
        for line in file:
            line_list = list(line.split())
            test_list.append(line_list)

    file.close()
    return test_list


"""
Function to cache requests
"""


def cache_request(cached_requests, request, cached_response, file_content, request_type):
    if request_type == 'GET' and file_content:
        cached_requests[request] = list()
        cached_requests[request] = [cached_response, file_content]
    elif request_type == 'POST' or (request_type == 'GET' and not file_content):
        cached_requests[request] = cached_response



"""
Function to check if a request is cached or not
if request method = 'GET' and it's ok ---> print response and file content
else if request method == 'GET' and it's not found --> print response only
"""


def is_cached(request, request_type):
    if request in cached_requests:
        if request_type == 'GET' and cached_requests[request][1]:
            print('[CLIENT] This request is already exists')
            print('[CLIENT] Cached response ', cached_requests[request][0])
            print('[CLIENT] Cached file content ', cached_requests[request][1])
        elif request_type == 'POST' or (request_type == 'GET' and not cached_requests[request][1]):
            print('[CLIENT] This request is already exists')
            print('[CLIENT] Cached response ', cached_requests[request])
        return True
    else:
        return False


def write_content_to_file(content, filename):
    with open(filename, 'w') as f:
        f.write(content)


def get_data(message):
    body = message.split('\r\n\r\n')[1]
    return body.split('\r\n')[0]


def get_info_from_request(request, info):
    if info == 'type':
        return request.split()[0]
    elif info == 'filename':
        filename = request.split()[1]
        filename = filename.replace('/','')
        return filename


def start_connection(host, port, requests):
    for request in (requests):
        request_type = get_info_from_request(request, info='type')
        cached_status = is_cached(request, request_type)
        global socket_exist
        if cached_status:
            continue
        else:
            if not socket_exist:
                server_address = (host, int(port))
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(server_address)
                socket_exist = True
                print(f"[CLIENT] Starting connection to {server_address}")
            print(request)
            sock.sendall(request.encode())
            print(f'[CLIENT] Request sent to server {server_address}')
            response = sock.recv(1024)
            message = response.decode()
            print(f"[CLIENT] Response received from {server_address} ", message)
            request_type = get_info_from_request(request, info='type')
            content = get_data(message)
            if request_type == 'GET':
                if content == 'File Not Found':
                    cache_request(cached_requests=cached_requests, request=request, cached_response=message, file_content='', request_type='GET')
                    print('[CLIENT] DONE! Request is cached')
                else:
                    print(f"[CLIENT] Data received from {server_address} ", content)
                    file_name = get_info_from_request(request, info='filename')
                    write_content_to_file(content, file_name)
                    print(f"[CLIENT] Data saved in file {file_name}")
                    cache_request(cached_requests, request, message, content, request_type='GET')
                    print('[CLIENT] DONE! Request is cached')
            elif request_type == 'POST':
                cache_request(cached_requests=cached_requests, request=request, cached_response=message, file_content='', request_type='POST')
                print('[CLIENT] DONE! Request is cached')
    sock.close()


input_file_name = sys.argv[1]
request_list = read_input_file_content(input_file_name)
host, port = request_list[0][2:4]
requests = convert_to_http_request(request_list)
start_connection(host, port, requests)