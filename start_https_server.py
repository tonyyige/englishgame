#!/usr/bin/env python3

import http.server
import ssl
import socketserver
import os

PORT = 8443
Handler = http.server.SimpleHTTPRequestHandler

# 检查证书文件是否存在
cert_file = '192.168.31.206+1.pem'
key_file = '192.168.31.206+1-key.pem'

if not os.path.exists(cert_file):
    print(f"错误：证书文件 {cert_file} 不存在")
    exit(1)

if not os.path.exists(key_file):
    print(f"错误：密钥文件 {key_file} 不存在")
    exit(1)

try:
    with socketserver.TCPServer(('', PORT), Handler) as httpd:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cert_file, key_file)
        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
        print(f'HTTPS服务器已启动，端口: {PORT}')
        print(f'访问地址: https://192.168.31.206:{PORT}/treasure-digger.html')
        print('按 Ctrl+C 停止服务器')
        httpd.serve_forever()
except KeyboardInterrupt:
    print('\n服务器已停止')
except Exception as e:
    print(f'启动服务器时出错: {e}')