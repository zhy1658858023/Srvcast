import pickle
import socket
from configuration import CT
import app_ct_reconstruction


def send_file(conn, file_read_name):
    with open(file_read_name, 'rb') as file:
        while True:
            data = file.read(1024)
            if not data:
                break
            conn.sendall(data)

    print('send file')


def receive_file(conn, file_save_path):
    with open(file_save_path, 'wb') as file:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            file.write(data)

    print('recieve file')


def pkl_depackage(file):
    with open(file, 'rb') as f:
        data = pickle.load(f)
        print("Data loaded from {}".format(file))
        return data


def IPv6_request():
    HOST = CT.dest_ipv6  
    PORT = CT.port  

    with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))

        filename = CT.client_data_readpath  
        send_file(client_socket, filename)

    print('send finish')

    
    with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))

        receive_file(client_socket, CT.client_image_receivepath) 
        img_list = pkl_depackage(CT.client_image_receivepath)
        # app_ct_reconstruction.image_show(img_list)
    print('recieve finish')
    return img_list


def IP_request():
    HOST = CT.dest_ipv4  
    PORT = CT.port  

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))

        filename = CT.client_data_readpath  
        send_file(client_socket, filename)

    print('send finish')

    #
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))

        receive_file(client_socket, CT.client_image_receivepath)  
        img_list = pkl_depackage(CT.client_image_receivepath)
        # app_ct_reconstruction.image_show(img_list)
    print('recieve finish')
    return img_list

# if __name__ == '__main__':
#     IP_request()
