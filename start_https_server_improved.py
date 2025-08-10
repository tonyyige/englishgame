#!/usr/bin/env python3

import http.server
import ssl
import socketserver
import os
import sys
from pathlib import Path

# 配置
PORT = 8443
HOST = '0.0.0.0'  # 监听所有接口
Handler = http.server.SimpleHTTPRequestHandler

class CORSHandler(http.server.SimpleHTTPRequestHandler):
    """添加CORS支持的请求处理器"""
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def find_cert_files():
    """查找证书文件"""
    possible_names = [
        '192.168.31.206+1.pem',
        'localhost.pem',
        'server.pem',
        'cert.pem'
    ]
    
    for cert_name in possible_names:
        key_name = cert_name.replace('.pem', '-key.pem')
        if cert_name.startswith('192.168'):
            key_name = '192.168.31.206+1-key.pem'
        
        if os.path.exists(cert_name) and os.path.exists(key_name):
            return cert_name, key_name
    
    return None, None

def setup_ssl_context(cert_file, key_file):
    """设置SSL上下文"""
    try:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        
        # 安全配置
        context.set_ciphers('HIGH:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!SRP:!CAMELLIA')
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        
        # 加载证书
        context.load_cert_chain(cert_file, key_file)
        
        return context
    except ssl.SSLError as e:
        print(f"SSL配置错误: {e}")
        return None
    except Exception as e:
        print(f"加载证书时出错: {e}")
        return None

def main():
    print("🚀 启动HTTPS服务器...")
    print(f"📂 当前目录: {os.getcwd()}")
    
    # 查找证书文件
    cert_file, key_file = find_cert_files()
    
    if not cert_file or not key_file:
        print("❌ 错误：找不到SSL证书文件")
        print("请确保以下文件存在：")
        print("  - 192.168.31.206+1.pem")
        print("  - 192.168.31.206+1-key.pem")
        print("或者:")
        print("  - localhost.pem")
        print("  - localhost-key.pem")
        sys.exit(1)
    
    print(f"✅ 找到证书文件: {cert_file}")
    print(f"✅ 找到密钥文件: {key_file}")
    
    # 设置SSL上下文
    ssl_context = setup_ssl_context(cert_file, key_file)
    if not ssl_context:
        sys.exit(1)
    
    # 检查端口是否可用
    try:
        with socketserver.TCPServer((HOST, PORT), CORSHandler) as httpd:
            # 包装socket为SSL
            httpd.socket = ssl_context.wrap_socket(httpd.socket, server_side=True)
            
            print("🎉 HTTPS服务器启动成功！")
            print(f"📡 监听地址: {HOST}:{PORT}")
            print("🌐 访问地址:")
            print(f"   - https://localhost:{PORT}/treasure-digger.html")
            print(f"   - https://192.168.31.206:{PORT}/treasure-digger.html")
            print()
            print("📝 可用的游戏文件:")
            html_files = [f for f in os.listdir('.') if f.endswith('.html')]
            for html_file in html_files:
                print(f"   - https://localhost:{PORT}/{html_file}")
            print()
            print("⚠️  注意: 如果浏览器提示证书不安全，请点击'高级'→'继续访问'")
            print("🛑 按 Ctrl+C 停止服务器")
            print("-" * 60)
            
            httpd.serve_forever()
            
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ 错误：端口 {PORT} 已被占用")
            print("请尝试:")
            print("  1. 关闭其他占用该端口的程序")
            print("  2. 或修改脚本中的 PORT 变量使用其他端口")
        else:
            print(f"❌ 网络错误: {e}")
    except KeyboardInterrupt:
        print('\n🛑 服务器已停止')
    except Exception as e:
        print(f'❌ 启动服务器时出错: {e}')
        sys.exit(1)

if __name__ == '__main__':
    main()