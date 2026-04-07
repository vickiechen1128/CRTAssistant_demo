# 文件上传 404 错误修复总结

## 问题描述

前端上传文件时出现 404 错误：
```
Failed to load resource: the server responded with a status of 404 (Not Found)
```

## 问题原因

1. 后端缺少 `/api/upload` 文件上传接口
2. 前端请求路径与后端路由不匹配

## 修复内容

### 1. 后端修复

#### 新建文件：`app/core/upload.py`
文件上传工具模块，包含：
- `validate_file()` - 验证文件类型和大小
- `generate_file_path()` - 生成唯一文件路径
- `get_file_url()` - 生成文件访问 URL
- `save_upload_file()` - 保存上传的文件

支持：
- 文件类型：PDF、JPG、PNG、GIF、WEBP、DOC、DOCX
- 最大文件大小：20MB
- 按月份组织上传目录

#### 新建文件：`app/core/file_routes.py`
文件上传路由，提供：
- `POST /api/upload` - 上传单个文件
- `POST /api/upload/batch` - 批量上传文件

响应格式：
```json
{
  "success": true,
  "message": "文件上传成功",
  "data": {
    "file_id": "uuid-string",
    "file_name": "document.pdf",
    "file_url": "/uploads/202603/20260330_xxxx.pdf",
    "file_size": 1024576,
    "content_type": "application/pdf",
    "uploaded_at": "2026-03-30T16:47:24.175Z"
  }
}
```

#### 更新文件：`app/main.py`
- 导入并注册文件上传路由
- 挂载静态文件目录 `/uploads`

```python
# 注册文件上传路由（无前缀，与前端对齐）
app.include_router(file_router, prefix="/api")

# 挂载静态文件目录
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")
```

### 2. 前端修复

#### 更新文件：`src/modules/plan/components/PlanStepsForm/ApprovalFilesStep.jsx`
- 增强响应处理逻辑，支持多种响应格式
- 添加错误提示信息
- 正确处理后端返回的文件 URL

```javascript
// 处理后端返回的响应格式
if (response && response.success && response.data) {
  // 标准响应格式: { success: true, data: { ... } }
  fileDetail = {
    file_name: response.data.file_name,
    file_url: response.data.file_url,
    file_size: response.data.file_size,
    uploaded_at: response.data.uploaded_at,
    file_id: response.data.file_id,
  };
}
```

## 验证测试

### 测试命令
```bash
# 后端测试
cd CRTAssistant_demo/backend
python3 -c "
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# 创建模拟 PDF 内容
pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\n'

# 测试上传
response = client.post(
    '/api/upload',
    files={'file': ('test.pdf', pdf_content, 'application/pdf')}
)

print(f'Status: {response.status_code}')
print(f'Response: {response.json()}')
"
```

### 测试结果
```
Status: 200
Success: True
File URL: /uploads/202603/20260330_f313a825.pdf
```

### 路由验证
```
GET /api/upload: 405 (正确，需要 POST)
Route: /api/upload
Route: /api/upload/batch
Route: /uploads
```

## 文件结构

```
backend/
├── app/
│   ├── core/
│   │   ├── upload.py          # 新建：上传工具
│   │   └── file_routes.py     # 新建：上传路由
│   ├── main.py                # 更新：注册路由
│   └── ...
└── uploads/                   # 新建：上传文件存储目录

frontend/
└── src/modules/plan/components/PlanStepsForm/
    └── ApprovalFilesStep.jsx  # 更新：响应处理
```

## 使用说明

### 前端调用方式
```javascript
const uploadProps = {
  name: 'file',
  action: '/api/upload',
  onChange: (info) => {
    if (info.file.status === 'done') {
      const fileDetail = info.file.response.data;
      // fileDetail.file_url 为可访问的文件路径
    }
  }
};
```

### 直接访问上传的文件
```
GET /uploads/202603/20260330_f313a825.pdf
```

## 后续优化建议

1. **文件存储** - 当前存储在本地目录，可改为云存储（OSS/S3）
2. **文件压缩** - 图片上传前自动压缩
3. **缩略图生成** - 图片上传后自动生成缩略图
4. **文件清理** - 定期清理未引用的上传文件
5. **上传进度** - 添加大文件上传进度显示

---

**修复日期**: 2026-03-30
**修复状态**: ✅ 已验证
