import { useEffect, useMemo, useState } from 'react';
import { Alert, Form, Modal, Select } from 'antd';
import { vehicleApi } from '../../api/vehicle';
import { driverApi } from '../../api/driver';
import { DriverStatus, VehicleStatus, type DispatchOrder, type Driver, type Vehicle } from '../../types';
import type { ReassignPayload } from '../../types';

interface Props {
  order: DispatchOrder | null;
  onClose: () => void;
  onSubmit: (payload: ReassignPayload) => Promise<boolean>;
}

export function ReassignModal({ order, onClose, onSubmit }: Props) {
  const [form] = Form.useForm<ReassignPayload>();
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [drivers, setDrivers] = useState<Driver[]>([]);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (order) {
      vehicleApi.list().then(setVehicles).catch(() => setVehicles([]));
      driverApi.list().then(setDrivers).catch(() => setDrivers([]));
      form.setFieldsValue({ vehicleId: order.vehicle ?? undefined, driverId: order.driver ?? undefined });
    }
  }, [order, form]);

  const availableVehicles = useMemo(
    () => vehicles.filter((v) => v.status === VehicleStatus.Available),
    [vehicles]
  );
  const availableDrivers = useMemo(
    () => drivers.filter((d) => d.status === DriverStatus.Available),
    [drivers]
  );

  const handleOk = async () => {
    const values = await form.validateFields();
    setSubmitting(true);
    try {
      const ok = await onSubmit(values);
      if (ok) onClose();
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal
      title={`改派 ${order?.orderNo ?? ''}`}
      open={!!order}
      onCancel={onClose}
      onOk={handleOk}
      okText="确认改派"
      cancelText="取消"
      confirmLoading={submitting}
      destroyOnClose
    >
      <Alert
        type="warning"
        showIcon
        style={{ marginBottom: 16 }}
        message="运输中的单据不得改派；新资源同样需满足可用、载重足够、保险/证件有效且无未结束单据。"
      />
      <Form form={form} layout="vertical">
        <Form.Item name="vehicleId" label="新车辆" rules={[{ required: true, message: '请选择车辆' }]}>
          <Select
            options={availableVehicles.map((v) => ({
              value: v.id,
              label: `${v.plateNo}｜${v.vehicleType ?? v.type}｜载重 ${v.payloadCapacity.toLocaleString()}kg｜保险 ${v.insuranceExpireDate ?? '未登记'}`
            }))}
            placeholder="选择新的车辆"
          />
        </Form.Item>
        <Form.Item name="driverId" label="新司机" rules={[{ required: true, message: '请选择司机' }]}>
          <Select
            options={availableDrivers.map((d) => ({
              value: d.id,
              label: `${d.name}｜${d.licenseType}｜${d.phone}｜驾照 ${d.licenseExpireDate ?? '未登记'}`
            }))}
            placeholder="选择新的司机"
          />
        </Form.Item>
      </Form>
    </Modal>
  );
}
