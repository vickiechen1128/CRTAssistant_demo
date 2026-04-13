#!/usr/bin/env python3
"""
Serv00 生产环境启动脚本
针对 Proxy 模式部署优化
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
                if lines:
                    version_info['version'] = lines[0].strip()
                if len(lines) > 1:
                    version_info['build_time'] = lines[1].strip()
        except Exception as e:
            print(f"读取版本文件失败: {e}")
    
    return version_info

if __name__ == "__main__":
    # 读取版本信息
    version_info = read_version()
    version = version_info.get('version', 'unknown')
    build_time = version_info.get('build_time', 'unknown')
    
    print(f"=" * 50)
    print(f"OpsPilot Serv00 生产环境")
    print(f"版本: {version}")
    print(f"构建时间: {build_time}")
    print(f"=" * 50)
    
    # 从环境变量读取配置，或使用默认值
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "60361"))
    
    print(f"启动服务: http://{host}:{port}")
    print(f"前端路径: ~/opspilot/frontend/dist")
    print(f"=" * 50)
    
    # 启动服务
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=False,
        workers=1,
        limit_max_requests=1000,
        timeout_keep_alive=5,
    )
