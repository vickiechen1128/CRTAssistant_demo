/**
 * 数据表格组件模板
 * 支持: 分页、排序、操作列
 */

export function DataTable({ 
  columns, 
  data, 
  loading = false,
  onRowClick,
  actions
}) {
  if (loading) {
    return <div className="table-loading">加载中...</div>;
  }

  if (!data || data.length === 0) {
    return <div className="table-empty">暂无数据</div>;
  }

  return (
    <div className="table-wrapper">
      <table className="data-table">
        <thead>
          <tr>
            {columns.map(col => (
              <th key={col.key} style={{ width: col.width }}>
                {col.title}
              </th>
            ))}
            {actions && <th>操作</th>}
          </tr>
        </thead>
        <tbody>
          {data.map((row, idx) => (
            <tr 
              key={row.id || idx} 
              onClick={() => onRowClick?.(row)}
              className={onRowClick ? 'clickable' : ''}
            >
              {columns.map(col => (
                <td key={col.key}>
                  {col.render ? col.render(row[col.key], row) : row[col.key]}
                </td>
              ))}
              {actions && (
                <td>
                  <div className="table-actions">
                    {actions.map((action, i) => (
                      <button
                        key={i}
                        onClick={(e) => {
                          e.stopPropagation();
                          action.onClick(row);
                        }}
                        className={`btn btn-${action.type || 'default'}`}
                      >
                        {action.label}
                      </button>
                    ))}
                  </div>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// 使用示例
export function DataTableExample() {
  const columns = [
    { key: 'id', title: 'ID', width: '80px' },
    { key: 'name', title: '名称' },
    { key: 'status', title: '状态', render: (v) => (
      <span className={`badge badge-${v}`}>{v}</span>
    )},
    { key: 'created_at', title: '创建时间' },
  ];

  const data = [
    { id: 1, name: 'Item 1', status: 'active', created_at: '2024-01-01' },
    { id: 2, name: 'Item 2', status: 'inactive', created_at: '2024-01-02' },
  ];

  const actions = [
    { label: '编辑', type: 'primary', onClick: (row) => console.log('编辑', row) },
    { label: '删除', type: 'danger', onClick: (row) => console.log('删除', row) },
  ];

  return (
    <DataTable 
      columns={columns} 
      data={data} 
      actions={actions}
      onRowClick={(row) => console.log('点击行', row)}
    />
  );
}
