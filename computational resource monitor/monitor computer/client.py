import socket
import monitor

dest_ipv4 = "172.18.10.3"
port = 9000
client_data_readpath = "M:\\项目代码\\monitor computer\\node-info.txt"

def send_file(conn, file_read_name):
    with open(file_read_name, 'rb') as file:
        while True:
            data = file.read(1024)
            if not data:
                break
            conn.sendall(data)

    print('文件发送完成')


def IP_request():
    HOST = dest_ipv4  # 服务器的IP地址
    PORT = port  # 选择一个端口号

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))

        filename = client_data_readpath  # 指定要发送文件的路径
        send_file(client_socket, filename)

    print('文件发送成功')



if __name__ == '__main__':
    monitor.monitor_txt()
    IP_request()