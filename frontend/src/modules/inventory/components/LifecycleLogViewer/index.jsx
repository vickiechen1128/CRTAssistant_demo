/**
 * LifecycleLogViewer 组件
 * 生命周期日志查看组件 - 展示应用系统的生命周期事件
 */
import React, { useState, useEffect } from 'react';
import {
  Card,
  Timeline,
  Tag,
  Space,
  Button,
  Select,
  Empty,
  Spin,
  Typography,
  Badge,
  Tooltip,
  Descriptions,
  Drawer,
} from 'antd';
import {
  HistoryOutlined,
  RocketOutlined,
  ArrowUpOutlined,
  RollbackOutlined,
  PoweroffOutlined,
  AppstoreOutlined,
  EditOutlined,
  StopOutlined,
  SettingOutlined,
  UserSwitchOutlined,
  TagOutlined,
  FileTextOutlined,
  FilterOutlined,
  SyncOutlined,
} from '@ant-design/icons';
import { useLifecycleLogStore } from '../../store/lifecycleLogStore';

const { Title, Text } = Typography;
const { Option } = Select;

// 日志类型配置
const logTypeConfig = {
  system_launch: { label: '系统上线', icon: <RocketOutlined />, color: 'green' },
  system_upgrade: { label: '系统升级', icon: <ArrowUpOutlined />, color: 'blue' },
  system_rollback: { label: '系统回滚', icon: <RollbackOutlined />, color: 'orange' },
  system_offline: { label: '系统下线', icon: <PoweroffOutlined />, color: 'red' },
  module_launch: { label: '功能上线', icon: <AppstoreOutlined />, color: 'cyan' },
  module_update: { label: '功能变更', icon: <EditOutlined />, color: 'purple' },
  module_offline: { label: '功能下线', icon: <StopOutlined />, color: 'magenta' },
  config_change: { label: '配置变更', icon: <SettingOutlined />, color: 'gold' },
  owner_change: { label: '负责人变更', icon: <UserSwitchOutlined />, color: 'lime' },
  status_change: { label: '状态变更', icon: <TagOutlined />, color: 'geekblue' },
  manual: { label: '手动记录', icon: <FileTextOutlined />, color: 'default' },
};

/**
 * LifecycleLogViewer 组件
 */
const LifecycleLogViewer = ({ appId, planId, moduleId }) => {
  const [filterType, setFilterType] = useState(undefined);
  const [selectedLog, setSelectedLog] = useState(null);
  const [drawerVisible, setDrawerVisible] = useState(false);

  const {
    timeline,
    logTypes,
    statistics,
    loading,
    fetchTimeline,
    fetchTimelineByPlan,
    fetchModuleTimeline,
    fetchLogTypes,
    fetchStatistics,
  } = useLifecycleLogStore();

  // 加载时间线数据
  useEffect(() => {
    if (appId) {
      loadTimeline();
      fetchLogTypes(appId);
      fetchStatistics(appId);
    }
  }, [appId, planId, moduleId]);

  const loadTimeline = async () => {
    try {
      if (planId) {
        await fetchTimelineByPlan(appId, planId);
      } else if (moduleId) {
        await fetchModuleTimeline(appId, moduleId);
      } else {
        await fetchTimeline(appId, { log_type: filterType });
      }
    } catch (error) {
      console.error('加载时间线失败:', error);
    }
  };

  // 获取日志类型配置
  const getLogTypeConfig = (type) => {
    return logTypeConfig[type] || { label: type, icon: <HistoryOutlined />, color: 'default' };
  };

  // 查看日志详情
  const handleViewDetail = (log) => {
    setSelectedLog(log);
    setDrawerVisible(true);
  };

  // 筛选变更
  const handleFilterChange = (value) => {
    setFilterType(value);
    if (appId) {
      fetchTimeline(appId, { log_type: value });
    }
  };

  // 刷新数据
  const handleRefresh = () => {
    loadTimeline();
    if (appId) {
      fetchStatistics(appId);
    }
  };

  // 渲染时间线项目
  const renderTimelineItem = (item) => {
    const config = getLogTypeConfig(item.type);
    
    return (
      <Timeline.Item
        key={item.id}
        dot={
          <div style={{ color: config.color }}>
            {config.icon}
          </div>
        }
        color={config.color}
      >
        <Card
          size="small"
          hoverable
          onClick={() => handleViewDetail(item)}
          style={{ marginBottom: 8 }}
        >
          <Space direction="vertical" style={{ width: '100%' }} size="small">
            <Space>
              <Tag color={config.color}>{config.label}</Tag>
              <Text strong>{item.title}</Text>
            </Space>
            
            {item.description && (
              <Text type="secondary" style={{ fontSize: 12 }}>
                {item.description}
              </Text>
            )}
            
            <Space split={<Text type="secondary">|</Text>}>
              <Text type="secondary" style={{ fontSize: 12 }}>
                {item.time}
              </Text>
              {item.operator && (
                <Text type="secondary" style={{ fontSize: 12 }}>
                  操作人: {item.operator}
                </Text>
              )}
              {item.plan_id && (
                <Tag size="small" color="blue">
                  计划: {item.plan_title || item.plan_id}
                </Tag>
              )}
            </Space>

            {/* 变更摘要 */}
            {item.changes && item.changes.changes && item.changes.changes.length > 0 && (
              <div style={{ marginTop: 8, padding: 8, background: '#f5f5f5', borderRadius: 4 }}>
                <Text type="secondary" style={{ fontSize: 12 }}>变更内容:</Text>
                {item.changes.changes.map((change, idx) => (
                  <div key={idx} style={{ fontSize: 12, marginTop: 4 }}>
                    <Text type="secondary">{change.field}: </Text>
                    <Text delete>{JSON.stringify(change.before)}</Text>
                    <Text style={{ margin: '0 4px' }}>→</Text>
                    <Text type="success">{JSON.stringify(change.after)}</Text>
                  </div>
                ))}
              </div>
            )}
          </Space>
        </Card>
      </Timeline.Item>
    );
  };

  return (
    <Card
      title={
        <Space>
          <HistoryOutlined />
          <span>生命周期日志</span>
          <Badge count={timeline.length} style={{ backgroundColor: '#1890ff' }} />
        </Space>
      }
      extra={
        <Space>
          <Select
            placeholder="筛选类型"
            style={{ width: 120 }}
            allowClear
            value={filterType}
            onChange={handleFilterChange}
            disabled={!!planId || !!moduleId}
          >
            {logTypes.map((type) => (
              <Option key={type.value} value={type.value}>
                {type.label}
              </Option>
            ))}
          </Select>
          
          <Tooltip title="刷新">
            <Button
              icon={<SyncOutlined />}
              onClick={handleRefresh}
              loading={loading}
            />
          </Tooltip>
        </Space>
      }
    >
      {/* 统计信息 */}
      {statistics && (
        <div style={{ marginBottom: 16, padding: 12, background: '#f5f5f5', borderRadius: 4 }}>
          <Space size="large">
            <Text>总记录: <strong>{statistics.total_count}</strong></Text>
            {Object.entries(statistics.type_distribution || {}).slice(0, 3).map(([type, count]) => {
              const config = getLogTypeConfig(type);
              return (
                <Tag key={type} color={config.color}>
                  {config.label}: {count}
                </Tag>
              );
            })}
          </Space>
        </div>
      )}

      {/* 时间线 */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: 40 }}>
          <Spin />
        </div>
      ) : timeline.length === 0 ? (
        <Empty description="暂无生命周期日志" />
      ) : (
        <Timeline mode="left">
          {timeline.map(renderTimelineItem)}
        </Timeline>
      )}

      {/* 日志详情抽屉 */}
      <Drawer
        title="日志详情"
        placement="right"
        width={500}
        onClose={() => setDrawerVisible(false)}
        open={drawerVisible}
      >
        {selectedLog && (
          <Descriptions column={1} bordered>
            <Descriptions.Item label="日志类型">
              {(() => {
                const config = getLogTypeConfig(selectedLog.type);
                return <Tag color={config.color}>{config.label}</Tag>;
              })()}
            </Descriptions.Item>
            
            <Descriptions.Item label="事件标题">
              {selectedLog.title}
            </Descriptions.Item>
            
            {selectedLog.description && (
              <Descriptions.Item label="详细描述">
                {selectedLog.description}
              </Descriptions.Item>
            )}
            
            <Descriptions.Item label="操作时间">
              {selectedLog.time}
            </Descriptions.Item>
            
            {selectedLog.operator && (
              <Descriptions.Item label="操作人">
                {selectedLog.operator}
              </Descriptions.Item>
            )}
            
            {selectedLog.plan_id && (
              <Descriptions.Item label="关联计划">
                <Tag color="blue">
                  {selectedLog.plan_title || selectedLog.plan_id}
                </Tag>
              </Descriptions.Item>
            )}
            
            {selectedLog.module_id && (
              <Descriptions.Item label="关联模块">
                {selectedLog.module_id}
              </Descriptions.Item>
            )}
            
            {/* 变更详情 */}
            {selectedLog.changes && selectedLog.changes.changes && selectedLog.changes.changes.length > 0 && (
              <Descriptions.Item label="变更详情">
                <Space direction="vertical" style={{ width: '100%' }}>
                  {selectedLog.changes.changes.map((change, idx) => (
                    <Card key={idx} size="small" title={change.field}>
                      <Space direction="vertical">
                        <div>
                          <Text type="secondary">变更前: </Text>
                          <Text delete>{JSON.stringify(change.before)}</Text>
                        </div>
                        <div>
                          <Text type="secondary">变更后: </Text>
                          <Text type="success">{JSON.stringify(change.after)}</Text>
                        </div>
                      </Space>
                    </Card>
                  ))}
                </Space>
              </Descriptions.Item>
            )}
          </Descriptions>
        )}
      </Drawer>
    </Card>
  );
};

export default LifecycleLogViewer;
