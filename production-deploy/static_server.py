#!/usr/bin/env python3
"""
前端静态文件服务器 - 用于本地测试
在 Serv00 上可以使用此脚本配合 Proxy 类型部署前端
"""
import http.server
import socketserver
import os
import sys

# 配置
PORT = 8080
# 前端构建目录路径
DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "dist")

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        # 添加 CORS 头，允许跨域访问
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()
    
    def do_OPTIONS(self):
        # 处理预检请求
        self.send_response(200)
        self.end_headers()

def main():
    # 检查目录是否存在
    if not os.path.exists(DIRECTORY):
        print(f"❌ 错误: 前端目录不存在: {DIRECTORY}")
        print("请先运行构建脚本生成 dist 目录")
        sys.exit(1)
    
    print(f"📁 服务目录: {DIRECTORY}")
    print(f"🌐 访问地址: http://localhost:{PORT}")
    print(f"🔗 或: http://127.0.0.1:{PORT}")
    print("\n按 Ctrl+C 停止服务\n")
    
    try:
        with socketserver.TCPServer(("0.0.0.0", PORT), MyHTTPRequestHandler) as httpd:
            print(f"✅ 服务器已启动，正在监听端口 {PORT}...")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 服务器已停止")
        sys.exit(0)
    except OSError as e:
        if e.errno == 48:  # 端口被占用
            print(f"\n❌ 错误: 端口 {PORT} 已被占用")
            print("请检查是否有其他程序在使用此端口")
        else:
            print(f"\n❌ 错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
