# 前端模板资源

## 组件列表

### Layout.jsx
基础布局组件，包含 Header、Sidebar、Main Content 三栏布局。

### DataTable.jsx
数据表格组件，支持：
- 自定义列配置
- 操作列按钮
- 行点击事件
- 加载状态和空状态

### FormModal.jsx
表单弹窗组件，支持：
- 创建/编辑模式
- 表单验证
- 提交加载状态
- 自定义表单内容

## 样式文件

### common.css
通用基础样式，包含：
- 布局样式 (layout, header, sidebar)
- 表格样式 (data-table)
- 表单样式 (input, textarea, select)
- 按钮样式 (btn-primary, btn-secondary, btn-danger)
- 弹窗样式 (modal)
- 状态标签 (badge)

## 使用方法

1. 复制所需组件到项目 `src/components/` 目录
2. 引入样式文件到 `src/index.css` 或组件中
3. 根据业务需求修改样式变量和交互逻辑

## 自定义主题

在 `common.css` 中修改以下变量可快速定制主题：

```css
:root {
  --primary-color: #1890ff;
  --success-color: #52c41a;
  --warning-color: #faad14;
  --danger-color: #ff4d4f;
  --border-color: #e8e8e8;
  --bg-color: #f5f5f5;
}
```
