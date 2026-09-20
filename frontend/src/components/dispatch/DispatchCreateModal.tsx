import { useMemo } from 'react';
import { Form, Input, InputNumber, Modal, Select, DatePicker } from 'antd';
import dayjs from 'dayjs';
import { DriverStatus, VehicleStatus, type DispatchCreatePayload, type Driver, type Vehicle } from '../../types';

type Props = {
  open: boolean;
  loading: boolean;
  vehicles: Vehicle[];
  drivers: Driver[];
  occupiedVehicleIds: Set<number>;
  occupiedDriverIds: Set<number>;
  onCancel: () => void;
  onSubmit: (payload: DispatchCreatePayload) => Promise<void>;
};

type FormValues = {
  vehicleId: number;
  driverId: number;
  origin: string;
  destination: string;
  planRange?: [dayjs.Dayjs, dayjs.Dayjs];
  cargo: string;
  weight: number;
  freight?: number;
  note?: string;
};

function vehicleInvalidReason(vehicle: Vehicle, occupied: boolean, weight: number): string | null {
  if (occupied) return '已有未结束单据';
  if (vehicle.status !== VehicleStatus.Available) return `状态 ${vehicle.status}`;
  if (!vehicle.insuranceExpireDate || dayjs(vehicle.insuranceExpireDate).isBefore(dayjs(), 'day')) {
    return '保险已过期';
  }
  if (weight > 0 && vehicle.loadCapacity > 0 && weight > vehicle.loadCapacity) return '载重不足';
  return null;
}

function driverInvalidReason(driver: Driver, occupied: boolean): string | null {
  if (occupied) return '已有未结束单据';
  if (!driver.licenseExpireDate || dayjs(driver.licenseExpireDate).isBefore(dayjs(), 'day')) {
    return '驾照已过期';
  }
  if (driver.status !== DriverStatus.Available) return `状态 ${driver.status}`;
  return null;
}

export function DispatchCreateModal({
  open, loading, vehicles, drivers, occupiedVehicleIds, occupiedDriverIds, onCancel, onSubmit
}: Props) {
  const [form] = Form.useForm<FormValues>();
  const weight = Form.useWatch('weight', form) ?? 0;

  const vehicleOptions = useMemo(
    () =>
      vehicles.map((v) => {
        const reason = vehicleInvalidReason(v, occupiedVehicleIds.has(v.id), weight);
        return {
          value: v.id,
          disabled: reason !== null,
          label: `${v.plateNo} · ${v.type}（载重 ${v.loadCapacity}kg）${reason ? ` — ${reason}` : ''}`
        };
      }),
    [vehicles, occupiedVehicleIds, weight]
  );

  const driverOptions = useMemo(
    () =>
      drivers.map((d) => {
        const reason = driverInvalidReason(d, occupiedDriverIds.has(d.id));
        return {
          value: d.id,
          disabled: reason !== null,
          label: `${d.name} · ${d.licenseType}（驾照至 ${d.licenseExpireDate ?? '未登记'}）${reason ? ` — ${reason}` : ''}`
        };
      }),
    [drivers, occupiedDriverIds]
  );

  const handleOk = async () => {
    const values = await form.validateFields();
    const payload: DispatchCreatePayload = {
      vehicleId: values.vehicleId,
      driverId: values.driverId,
      origin: values.origin,
      destination: values.destination,
      cargo: values.cargo,
      weight: values.weight,
      freight: values.freight ?? 0,
      note: values.note ?? ''
    };
    if (values.planRange) {
      payload.planDepartAt = values.planRange[0].format('YYYY-MM-DD HH:mm:ss');
      payload.planArriveAt = values.planRange[1].format('YYYY-MM-DD HH:mm:ss');
    }
    await onSubmit(payload);
    form.resetFields();
  };

  return (
    <Modal
      title="创建调度单"
      open={open}
      confirmLoading={loading}
      onOk={handleOk}
      onCancel={() => { form.resetFields(); onCancel(); }}
      okText="创建并指派"
      cancelText="取消"
      destroyOnClose
      maskClosable={false}
    >
      <Form form={form} layout="vertical" initialValues={{ weight: 1000, freight: 0 }}>
        <Form.Item
          name="vehicleId"
          label="车辆（仅状态可用、载重足够且保险有效）"
          rules={[{ required: true, message: '请选择车辆' }]}
        >
          <Select placeholder="请选择车辆" options={vehicleOptions} showSearch optionFilterProp="label" />
        </Form.Item>
        <Form.Item
          name="driverId"
          label="司机（仅证件未过期且可用）"
          rules={[{ required: true, message: '请选择司机' }]}
        >
          <Select placeholder="请选择司机" options={driverOptions} showSearch optionFilterProp="label" />
        </Form.Item>
        <div style={{ display: 'flex', gap: 12 }}>
          <Form.Item name="origin" label="出发地" style={{ flex: 1 }} rules={[{ required: true, message: '请输入出发地' }]}>
            <Input placeholder="如：上海青浦仓" />
          </Form.Item>
          <Form.Item name="destination" label="目的地" style={{ flex: 1 }} rules={[{ required: true, message: '请输入目的地' }]}>
            <Input placeholder="如：杭州萧山仓" />
          </Form.Item>
        </div>
        <Form.Item name="planRange" label="预计出发 / 到达时间">
          <DatePicker.RangePicker showTime style={{ width: '100%' }} format="YYYY-MM-DD HH:mm" />
        </Form.Item>
        <Form.Item name="cargo" label="货物描述" rules={[{ required: true, message: '请输入货物描述' }]}>
          <Input placeholder="如：冷链食品" />
        </Form.Item>
        <div style={{ display: 'flex', gap: 12 }}>
          <Form.Item name="weight" label="重量（kg）" style={{ flex: 1 }} rules={[{ required: true, message: '请输入重量' }]}>
            <InputNumber min={0} style={{ width: '100%' }} precision={0} />
          </Form.Item>
          <Form.Item name="freight" label="运费（元）" style={{ flex: 1 }}>
            <InputNumber min={0} style={{ width: '100%' }} precision={2} />
          </Form.Item>
        </div>
        <Form.Item name="note" label="备注">
          <Input.TextArea rows={2} />
        </Form.Item>
      </Form>
    </Modal>
  );
}
