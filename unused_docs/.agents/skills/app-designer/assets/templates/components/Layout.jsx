/**
 * 布局组件模板
 * 包含: Header, Sidebar, Main Content Area
 */

export function Layout({ children }) {
  return (
    <div className="layout">
      <Header />
      <div className="layout-body">
        <Sidebar />
        <main className="layout-main">{children}</main>
      </div>
    </div>
  );
}

export function Header() {
  return (
    <header className="header">
      <div className="header-logo">🚀 App Name</div>
      <nav className="header-nav">
        <a href="/">首页</a>
        <a href="/about">关于</a>
      </nav>
    </header>
  );
}

export function Sidebar() {
  const menuItems = [
    { label: 'Dashboard', path: '/', icon: '📊' },
    { label: 'Items', path: '/items', icon: '📋' },
    { label: 'Settings', path: '/settings', icon: '⚙️' },
  ];

  return (
    <aside className="sidebar">
      <nav>
        {menuItems.map(item => (
          <a key={item.path} href={item.path} className="sidebar-link">
            <span>{item.icon}</span>
            <span>{item.label}</span>
          </a>
        ))}
      </nav>
    </aside>
  );
}
