# 依赖管理说明

## 文件说明

| 文件 | 用途 | 使用场景 |
|------|------|----------|
| `requirements.txt` | 生产环境依赖 | Serv00 部署、生产服务器 |
| `requirements-dev.txt` | 开发环境依赖 | 本地开发、调试 |

## 版本策略

### 生产环境 (requirements.txt)
- **严格锁定版本**：使用 `==` 精确指定版本号
- **最小化依赖**：只包含运行必需的依赖
- **兼容性测试**：所有版本已在 Serv00 (FreeBSD + Python 3.9) 测试通过

### 开发环境 (requirements-dev.txt)
- **包含生产依赖**：前部分与 `requirements.txt` 完全一致
- **额外开发工具**：代码格式化、调试、文档等工具
- **本地优化**：支持热重载、性能分析等

## 环境差异说明

### Serv00 环境限制
- **操作系统**：FreeBSD 13.x
- **Python 版本**：3.9.x
- **内存限制**：512 MB
- **磁盘限制**：3 GB

### 本地开发环境
- **操作系统**：macOS / Linux / Windows
- **Python 版本**：3.10+ (推荐 3.12)
- **无资源限制**

## 依赖版本详情

### 核心框架
| 包名 | 版本 | 说明 |
|------|------|------|
| fastapi | 0.110.3 | Web 框架，支持 Python 3.9+ |
| uvicorn | 0.29.0 | ASGI 服务器，标准依赖 |
| sqlalchemy | 2.0.30 | ORM 框架 |
| pydantic | 2.7.1 | 数据验证 |

### 安全相关
| 包名 | 版本 | 说明 |
|------|------|------|
| passlib | 1.7.4 | 密码哈希 |
| python-jose | 3.3.0 | JWT 处理 |
| python-multipart | 0.0.9 | 表单解析 |

### 测试相关
| 包名 | 版本 | 说明 |
|------|------|------|
| pytest | 8.2.0 | 测试框架 |
| pytest-asyncio | 0.23.6 | 异步测试支持 |
| httpx | 0.27.0 | HTTP 客户端 |

## 安装命令

### 生产环境
```bash
# 在 Serv00 或生产服务器执行
pip install -r requirements.txt --user
```

### 开发环境
```bash
# 在本地开发环境执行
pip install -r requirements-dev.txt

# 或使用虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows
pip install -r requirements-dev.txt
```

## 更新依赖流程

### 1. 测试新版本
```bash
# 在本地测试新版本
pip install package==new.version
```

### 2. 验证兼容性
- 运行完整测试套件
- 检查 Serv00 兼容性（Python 3.9）

### 3. 更新文件
```bash
# 更新 requirements.txt
pip freeze | grep -E "^(fastapi|uvicorn|...)" > requirements.txt

# 同步到 requirements-dev.txt
# 手动复制生产依赖部分
```

### 4. 部署验证
```bash
# 在 Serv00 测试部署
pip install -r requirements.txt --user
python serv00_start.py
```

## 常见问题

### Q: 为什么 Serv00 和本地版本不一致？
A: Serv00 使用 FreeBSD 和 Python 3.9，部分依赖的最新版本可能不支持。我们锁定的版本经过测试，在两个环境都能正常工作。

### Q: 可以升级依赖版本吗？
A: 可以，但需要：
1. 在本地测试新版本
2. 确认支持 Python 3.9
3. 在 Serv00 测试环境验证
4. 更新两个 requirements 文件

### Q: 开发环境的额外依赖会影响生产吗？
A: 不会。生产环境只安装 `requirements.txt`，不包含开发工具。

## 相关文档

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [Serv00 Python 支持](https://docs.serv00.com/Python/)
