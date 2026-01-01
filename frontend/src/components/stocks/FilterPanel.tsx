/**
 * 股票筛选面板组件
 */
import React from 'react';
import { Card, Form, Select, InputNumber, Button, Space, Row, Col } from 'antd';
import { FilterOutlined, ReloadOutlined } from '@ant-design/icons';

const { Option } = Select;

export interface FilterValues {
  market?: 'sh' | 'sz';
  min_cap?: number;
  max_cap?: number;
}

interface FilterPanelProps {
  onFilter: (values: FilterValues) => void;
  onReset: () => void;
}

const FilterPanel: React.FC<FilterPanelProps> = ({ onFilter, onReset }) => {
  const [form] = Form.useForm();

  const handleFinish = (values: FilterValues) => {
    onFilter(values);
  };

  const handleReset = () => {
    form.resetFields();
    onReset();
  };

  return (
    <Card
      title={
        <span>
          <FilterOutlined style={{ marginRight: 8 }} />
          筛选条件
        </span>
      }
      size="small"
      style={{ marginBottom: 16 }}
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={handleFinish}
      >
        <Row gutter={16}>
          <Col xs={24} sm={12} md={6}>
            <Form.Item label="市场" name="market">
              <Select placeholder="选择市场" allowClear>
                <Option value="sh">上海</Option>
                <Option value="sz">深圳</Option>
              </Select>
            </Form.Item>
          </Col>
          
          <Col xs={24} sm={12} md={6}>
            <Form.Item label="最小市值（亿）" name="min_cap">
              <InputNumber
                placeholder="最小市值"
                style={{ width: '100%' }}
                min={0}
              />
            </Form.Item>
          </Col>
          
          <Col xs={24} sm={12} md={6}>
            <Form.Item label="最大市值（亿）" name="max_cap">
              <InputNumber
                placeholder="最大市值"
                style={{ width: '100%' }}
                min={0}
              />
            </Form.Item>
          </Col>
          
          <Col xs={24} sm={12} md={6}>
            <Form.Item label=" ">
              <Space>
                <Button type="primary" htmlType="submit" icon={<FilterOutlined />}>
                  筛选
                </Button>
                <Button onClick={handleReset} icon={<ReloadOutlined />}>
                  重置
                </Button>
              </Space>
            </Form.Item>
          </Col>
        </Row>
      </Form>
    </Card>
  );
};

export default FilterPanel;
