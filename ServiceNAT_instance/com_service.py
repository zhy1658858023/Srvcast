import socket
from configuration import CT
import app_ct_reconstruction


def receive_file(sock, file_save_path):
    with open(file_save_path, 'wb') as file:
        while True:
            data = sock.recv(1024)
            if not data:
                break
            file.write(data)
    print('file recieved')


def send_file(sock, file_read_path):
    with open(file_read_path, 'rb') as file:
        data = file.read()
        sock.sendall(data)


def IPv6_connection():
    HOST = CT.dest_ipv6  
    PORT = CT.port 
    with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)  

        print("Listening...")
        conn, addr = server_socket.accept()
        print('Connect to', addr)

        receive_file(conn, CT.server_data_savepath)  
        print('file recieve finish')

        img, img_list = app_ct_reconstruction.data_processing(CT.server_data_savepath)
        app_ct_reconstruction.image_package(img_list, CT.server_image_savepath)

        print('waiting...')
        conn, addr = server_socket.accept()
        print('Connect to', addr)

        send_file(conn, CT.server_image_savepath)  

    print('file send finish')


def IP_connection():
    HOST = CT.dest_ipv4  
    PORT = CT.port  
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)  

        print("Listening...")
        conn, addr = server_socket.accept()
        print('Connect to', addr)

        receive_file(conn, CT.server_data_savepath)  
        print('file recieve finish')

        img, img_list = app_ct_reconstruction.data_processing(CT.server_data_savepath)
        app_ct_reconstruction.image_package(img_list, CT.server_image_savepath)

        print('waiting...')
        conn, addr = server_socket.accept()
        print('Connect to', addr)

        send_file(conn, CT.server_image_savepath)  

        print('file send finish')


if __name__ == '__main__':
    IPv6_connection()
