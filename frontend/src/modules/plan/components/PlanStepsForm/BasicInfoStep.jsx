/**
 * BasicInfoStep 组件
 * Step 1: 填写计划基本信息
 */
import React from 'react';
import { Form, Input, Select, DatePicker, Radio } from 'antd';
import { categoryOptions, priorityOptions } from '../../api/types';

const { Option } = Select;
const { TextArea } = Input;

/**
 * 基本信息步骤组件
 */
const BasicInfoStep = ({ form }) => {
  return (
    <Form
      form={form}
      layout="vertical"
      initialValues={{
        priority: 'P1',
      }}
    >
      <Form.Item
        name="name"
        label="计划名称"
        rules={[
          { required: true, message: '请输入计划名称' },
          { max: 200, message: '计划名称最多200个字符' },
        ]}
      >
        <Input placeholder="例如：订单系统v2.0上线" />
      </Form.Item>

      <Form.Item
        name="category"
        label="计划分类"
        rules={[{ required: true, message: '请选择计划分类' }]}
      >
        <Select placeholder="请选择计划分类">
          {categoryOptions.map((opt) => (
            <Option key={opt.value} value={opt.value}>
              {opt.label}
            </Option>
          ))}
        </Select>
      </Form.Item>

      <Form.Item
        name="priority"
        label="优先级"
        rules={[{ required: true, message: '请选择优先级' }]}
      >
        <Radio.Group>
          {priorityOptions.map((opt) => (
            <Radio.Button 
              key={opt.value} 
              value={opt.value}
              style={{ color: opt.color }}
            >
              {opt.label}
            </Radio.Button>
          ))}
        </Radio.Group>
      </Form.Item>

      <Form.Item
        name="planned_start_time"
        label="计划开始时间"
        rules={[{ required: true, message: '请选择计划开始时间' }]}
      >
        <DatePicker
          showTime
          format="YYYY-MM-DD HH:mm"
          style={{ width: '100%' }}
          placeholder="选择计划开始执行的时间"
        />
      </Form.Item>

      <Form.Item
        name="planned_end_time"
        label="计划结束时间（可选）"
      >
        <DatePicker
          showTime
          format="YYYY-MM-DD HH:mm"
          style={{ width: '100%' }}
          placeholder="预估完成时间"
        />
      </Form.Item>

      <Form.Item
        name="description"
        label="计划说明"
      >
        <TextArea
          rows={4}
          placeholder="补充说明计划的背景、目标等信息"
          maxLength={2000}
          showCount
        />
      </Form.Item>
    </Form>
  );
};

export default BasicInfoStep;
