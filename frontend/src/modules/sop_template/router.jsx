/**
 * SOP 模板模块路由配置
 */
import React from 'react';

// 懒加载页面组件
const SOPTemplateListView = React.lazy(() => import('./views/SOPTemplateListView'));
const SOPTemplateCreateView = React.lazy(() => import('./views/SOPTemplateCreateView'));
const SOPTemplateDetailView = React.lazy(() => import('./views/SOPTemplateDetailView'));
const AuditMatrixListView = React.lazy(() => import('./views/AuditMatrixListView'));

/**
 * SOP 模板模块路由
 */
export const sopTemplateRoutes = [
  {
    path: '/sop-templates',
    element: <SOPTemplateListView />,
  },
  {
    path: '/sop-templates/create',
    element: <SOPTemplateCreateView />,
  },
  {
    path: '/sop-templates/:templateId',
    element: <SOPTemplateDetailView />,
  },
  {
    path: '/sop-templates/:templateId/edit',
    element: <SOPTemplateCreateView />, // 复用创建页面作为编辑页面
  },
  {
    path: '/audit-matrix-configs',
    element: <AuditMatrixListView />,
  },
];
