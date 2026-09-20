import { useEffect, useState } from 'react';
import { Button, Card, Form, Input, InputNumber, Modal, Select, Space, message } from 'antd';
import { PlusOutlined, ReloadOutlined } from '@ant-design/icons';
import { vehicleApi } from '../api/vehicle';
import type { CreateVehiclePayload, Vehicle } from '../types';
import { VehicleCard } from '../components/common/VehicleCard';
import { PageShell } from './PageShell';

const VEHICLE_TYPES = ['轻卡', '中卡', '重卡', '冷链车', '危化车'];

export function VehicleManage() {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [loading, setLoading] = useState(false);
  const [createOpen, setCreateOpen] = useState(false);
  const [form] = Form.useForm<CreateVehiclePayload & { vehicleType: string }>();

  const load = () => {
    setLoading(true);
    vehicleApi
      .list()
      .then(setVehicles)
      .catch(() => setVehicles([]))
      .finally(() => setLoading(false));
  };
  useEffect(load, []);

  const handleCreate = async () => {
    const values = await form.validateFields();
    try {
      await vehicleApi.create(values);
      message.success('车辆已添加，初始状态 Available');
      setCreateOpen(false);
      form.resetFields();
      load();
    } catch (err) {
      message.error(err instanceof Error ? err.message : '添加失败');
    }
  };

  return (
    <PageShell title="车辆管理">
      <Card
        extra={
          <Space>
            <Button icon={<ReloadOutlined />} onClick={load} loading={loading}>
              刷新
            </Button>
            <Button type="primary" icon={<PlusOutlined />} onClick={() => setCreateOpen(true)}>
              添加车辆
            </Button>
          </Space>
        }
      >
        <div className="grid grid-3">
          {vehicles.map((vehicle) => (
            <VehicleCard vehicle={vehicle} key={vehicle.id} />
          ))}
        </div>
      </Card>

      <Modal
        title="添加车辆"
        open={createOpen}
        onCancel={() => setCreateOpen(false)}
        onOk={handleCreate}
        okText="保存"
        cancelText="取消"
        destroyOnClose
      >
        <Form form={form} layout="vertical">
          <Form.Item name="plateNo" label="车牌号" rules={[{ required: true, message: '请输入车牌号' }]}>
            <Input placeholder="沪A-1234" />
          </Form.Item>
          <Form.Item name="vehicleType" label="车辆类型" rules={[{ required: true, message: '请选择类型' }]}>
            <Select options={VEHICLE_TYPES.map((value) => ({ value, label: value }))} />
          </Form.Item>
          <Form.Item name="brandModel" label="品牌型号" rules={[{ required: true, message: '请输入品牌型号' }]}>
            <Input placeholder="东风天锦 KR" />
          </Form.Item>
          <Form.Item name="payloadCapacity" label="额定载重 (kg)" rules={[{ required: true, message: '请输入额定载重' }]}>
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="insuranceExpireDate" label="保险到期日" rules={[{ required: true, message: '请选择保险到期日' }]}>
            <Input placeholder="YYYY-MM-DD" />
          </Form.Item>
          <Form.Item name="inspectionExpireDate" label="年检到期日">
            <Input placeholder="YYYY-MM-DD" />
          </Form.Item>
          <Form.Item name="tankCapacity" label="油箱容量 (L)">
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>
    </PageShell>
  );
}
