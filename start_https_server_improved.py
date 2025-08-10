#!/usr/bin/env python3

import http.server
import ssl
import socketserver
import os
import socket
import subprocess

PORT = 8443
Handler = http.server.SimpleHTTPRequestHandler

def get_local_ip():
    """获取本机局域网IP地址"""
    try:
        # 方法1：连接到外部地址获取本地IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        try:
            # 方法2：使用ifconfig命令
            result = subprocess.run(['ifconfig'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'inet ' in line and '127.0.0.1' not in line and 'inet 169.254' not in line:
                    ip = line.split()[1]
                    if ip.startswith('192.168.') or ip.startswith('10.') or ip.startswith('172.'):
                        return ip
        except:
            pass
        return '127.0.0.1'

def find_cert_files():
    """查找可用的证书文件"""
    current_ip = get_local_ip()
    
    # 按优先级查找证书文件
    cert_patterns = [
        f'{current_ip}+1.pem',           # 当前IP的证书
        f'{current_ip}.pem',             # 当前IP的证书（无+1）
        '192.168.31.206+1.pem',          # 原有证书
        'localhost+1.pem',               # localhost证书
        'server.pem'                     # 通用证书名
    ]
    
    key_patterns = [
        f'{current_ip}+1-key.pem',
        f'{current_ip}-key.pem',
        '192.168.31.206+1-key.pem',
        'localhost+1-key.pem',
        'server-key.pem'
    ]
    
    for cert_file, key_file in zip(cert_patterns, key_patterns):
        if os.path.exists(cert_file) and os.path.exists(key_file):
            return cert_file, key_file
    
    return None, None

def main():
    current_ip = get_local_ip()
    cert_file, key_file = find_cert_files()
    
    if not cert_file or not key_file:
        print(f"错误：找不到SSL证书文件")
        print(f"请确保以下任一证书对存在：")
        print(f"  - {current_ip}+1.pem 和 {current_ip}+1-key.pem")
        print(f"  - localhost+1.pem 和 localhost+1-key.pem")
        print(f"  - 或使用 mkcert 生成新证书")
        print(f"\n生成证书命令示例：")
        print(f"  mkcert {current_ip} localhost 127.0.0.1")
        exit(1)

    try:
        with socketserver.TCPServer(('', PORT), Handler) as httpd:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(cert_file, key_file)
            httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
            
            print(f'HTTPS服务器已启动，端口: {PORT}')
            print(f'使用证书: {cert_file}')
            print(f'当前IP地址: {current_ip}')
            print()
            print(f'访问地址：')
            print(f'  本地访问: https://localhost:{PORT}/treasure-digger.html')
            print(f'  局域网访问: https://{current_ip}:{PORT}/treasure-digger.html')
            print(f'  游戏列表: https://{current_ip}:{PORT}/')
            print()
            print('按 Ctrl+C 停止服务器')
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print('\n服务器已停止')
    except Exception as e:
        print(f'启动服务器时出错: {e}')

if __name__ == '__main__':
    main()