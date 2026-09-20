import { useEffect, useMemo, useState } from 'react';
import {
  Button,
  Card,
  Form,
  Input,
  List,
  Modal,
  Select,
  Space,
  Tabs,
  Tag,
  message
} from 'antd';
import { PlusOutlined, ReloadOutlined } from '@ant-design/icons';
import { driverApi } from '../api/driver';
import { DriverStatus, type CreateDriverPayload, type Driver } from '../types';
import { UserAvatar } from '../components/common/UserAvatar';
import { StatusBadge } from '../components/common/StatusBadge';
import { PageShell } from './PageShell';

const STATUS_TABS = [
  { key: 'all', label: '全部' },
  { key: DriverStatus.Available, label: '可用' },
  { key: DriverStatus.OnTrip, label: '运输中' },
  { key: DriverStatus.Leave, label: '休假' },
  { key: DriverStatus.Suspended, label: '停职' }
];

export function DriverManage() {
  const [drivers, setDrivers] = useState<Driver[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('all');
  const [createOpen, setCreateOpen] = useState(false);
  const [form] = Form.useForm<CreateDriverPayload>();

  const load = () => {
    setLoading(true);
    driverApi
      .list(activeTab === 'all' ? undefined : activeTab)
      .then(setDrivers)
      .catch(() => setDrivers([]))
      .finally(() => setLoading(false));
  };
  useEffect(load, [activeTab]);

  const filtered = useMemo(
    () => (activeTab === 'all' ? drivers : drivers.filter((d) => d.status === activeTab)),
    [drivers, activeTab]
  );

  const handleCreate = async () => {
    const values = await form.validateFields();
    try {
      await driverApi.create(values);
      message.success('司机已添加，初始状态 Available');
      setCreateOpen(false);
      form.resetFields();
      load();
    } catch (err) {
      message.error(err instanceof Error ? err.message : '添加失败');
    }
  };

  return (
    <PageShell title="司机管理">
      <Card
        extra={
          <Space>
            <Button icon={<ReloadOutlined />} onClick={load} loading={loading}>
              刷新
            </Button>
            <Button type="primary" icon={<PlusOutlined />} onClick={() => setCreateOpen(true)}>
              添加司机
            </Button>
          </Space>
        }
      >
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={STATUS_TABS.map((tab) => ({ key: tab.key, label: tab.label }))}
        />
        <List
          loading={loading}
          dataSource={filtered}
          renderItem={(driver) => (
            <List.Item actions={[<StatusBadge status={driver.status} key="s" />]}>
              <List.Item.Meta
                avatar={<UserAvatar name={driver.name} />}
                title={
                  <Space>
                    {driver.name}
                    <Tag>{driver.licenseType}</Tag>
                  </Space>
                }
                description={
                  <span>
                    {driver.phone}｜驾照到期 {driver.licenseExpireDate ?? '—'}｜累计驾驶{' '}
                    {driver.drivingHours.toLocaleString()}h｜违章 {driver.violationCount} 次
                  </span>
                }
              />
            </List.Item>
          )}
        />
      </Card>

      <Modal
        title="添加司机"
        open={createOpen}
        onCancel={() => setCreateOpen(false)}
        onOk={handleCreate}
        okText="保存"
        cancelText="取消"
        destroyOnClose
      >
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="姓名" rules={[{ required: true, message: '请输入姓名' }]}>
            <Input />
          </Form.Item>
          <Form.Item name="phone" label="手机号" rules={[{ required: true, message: '请输入手机号' }]}>
            <Input placeholder="13800000000" />
          </Form.Item>
          <Form.Item name="licenseType" label="驾照类型" rules={[{ required: true, message: '请选择驾照类型' }]}>
            <Select options={['C1', 'B2', 'A2', 'A1'].map((value) => ({ value, label: value }))} />
          </Form.Item>
          <Form.Item
            name="licenseExpireDate"
            label="驾照到期日"
            rules={[{ required: true, message: '请选择驾照到期日' }]}
          >
            <Input placeholder="YYYY-MM-DD" />
          </Form.Item>
          <Form.Item name="hireDate" label="入职日期">
            <Input placeholder="YYYY-MM-DD" />
          </Form.Item>
        </Form>
      </Modal>
    </PageShell>
  );
}
