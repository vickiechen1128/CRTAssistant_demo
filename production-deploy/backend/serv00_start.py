#!/usr/bin/env python3
"""
Serv00 生产环境启动脚本
针对 FreeBSD + 512M 内存优化
"""

import uvicorn
import os
import sys

# 添加应用目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def read_version():
    """读取版本号文件"""
    version_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "VERSION")
    version_info = {}
    
    if os.path.exists(version_file):
        try:
            with open(version_file, 'r') as f:
                lines = f.readlines()
                # 第一行是版本号
                if lines:
                    first_line = lines[0].strip()
                    if first_line and not first_line.startswith('#'):
                        # 如果第一行包含 =，按 KEY=VALUE 解析
                        if '=' in first_line:
                            version_info['VERSION'] = first_line.split('=', 1)[1].strip()
                        else:
                            # 否则第一行就是版本号
                            version_info['VERSION'] = first_line
                
                # 解析其他 KEY=VALUE 行
                for line in lines[1:]:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        version_info[key.strip()] = value.strip()
        except Exception:
            pass
    
    return version_info

def main():
    # 从环境变量读取配置
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 60361))
    
    # 读取版本信息
    version_info = read_version()
    app_version = version_info.get('VERSION', os.getenv('APP_VERSION', 'unknown'))
    build_time = version_info.get('BUILD_TIME', '')
    
    # 内存优化配置
    config = {
        "app": "app.main:app",
        "host": host,
        "port": port,
        "reload": False,  # 生产环境关闭热重载
        "log_level": "info",
        "proxy_headers": True,
        "forwarded_allow_ips": "*",
        # 内存优化
        "limit_max_requests": 1000,  # 限制单个 worker 的请求数
        "timeout_keep_alive": 5,     # 减少连接保持时间
        "workers": 1,                # 单 worker 模式（节省内存）
    }
    
    print("🚀 启动 OpsPilot 后端服务...")
    print(f"📦 版本: {app_version}")
    if build_time:
        print(f"⏰ 构建时间: {build_time}")
    print(f"📍 地址: http://{host}:{port}")
    print(f"🔧 环境: {os.getenv('ENV', 'production')}")
    
    uvicorn.run(**config)

if __name__ == "__main__":
    main()
