import socket


dest_ipv4 = "172.18.10.3"
port = 9000
server_data_savepath = "M:\\项目代码\\2.txt"

def receive_file(sock, file_save_path):
    with open(file_save_path, 'wb') as file:
        while True:
            data = sock.recv(1024)
            if not data:
                break
            file.write(data)
    print('文件接收完成')

def IP_connection():
    HOST = dest_ipv4  # 服务器的IP地址
    PORT = port  # 选择一个端口号
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)  # 监听传入连接

        print("服务器正在监听传入连接...")
        conn, addr = server_socket.accept()
        print('已连接到', addr)

        receive_file(conn, server_data_savepath)  # 接收并保存文件
        print('文件接收成功')


if __name__ == '__main__':
    IP_connection()