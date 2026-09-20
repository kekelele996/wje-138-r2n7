import { useEffect, useMemo, useState } from 'react';
import {
  Alert,
  DatePicker,
  Form,
  Input,
  InputNumber,
  Modal,
  Select,
  Tag
} from 'antd';
import dayjs, { type Dayjs } from 'dayjs';
import { vehicleApi } from '../../api/vehicle';
import { driverApi } from '../../api/driver';
import { DriverStatus, VehicleStatus, type Driver, type Vehicle } from '../../types';
import type { CreateDispatchPayload } from '../../types';

interface Props {
  open: boolean;
  onClose: () => void;
  onSubmit: (payload: CreateDispatchPayload) => Promise<boolean>;
}

interface FormValues {
  vehicleId: number;
  driverId: number;
  origin: string;
  destination: string;
  weight: number;
  freight?: number;
  cargo?: string;
  note?: string;
  planRange?: [Dayjs, Dayjs];
}

export function CreateDispatchModal({ open, onClose, onSubmit }: Props) {
  const [form] = Form.useForm<FormValues>();
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [drivers, setDrivers] = useState<Driver[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const weight = Form.useWatch('weight', form);
  const selectedVehicleId = Form.useWatch('vehicleId', form);

  useEffect(() => {
    if (open) {
      vehicleApi.list().then(setVehicles).catch(() => setVehicles([]));
      driverApi.list().then(setDrivers).catch(() => setDrivers([]));
    }
  }, [open]);

  const selectedVehicle = useMemo(
    () => vehicles.find((v) => v.id === selectedVehicleId),
    [vehicles, selectedVehicleId]
  );
  const overload =
    weight != null && selectedVehicle && selectedVehicle.payloadCapacity < weight;

  const handleOk = async () => {
    const values = await form.validateFields();
    setSubmitting(true);
    try {
      const [planDepartAt, planArriveAt] = values.planRange ?? [];
      const ok = await onSubmit({
        vehicleId: values.vehicleId,
        driverId: values.driverId,
        origin: values.origin,
        destination: values.destination,
        weight: values.weight,
        freight: values.freight ?? 0,
        cargo: values.cargo ?? '',
        note: values.note ?? '',
        planDepartAt: planDepartAt ? planDepartAt.second(0).toISOString() : null,
        planArriveAt: planArriveAt ? planArriveAt.second(0).toISOString() : null
      });
      if (ok) {
        form.resetFields();
        onClose();
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal
      title="创建调度单"
      open={open}
      onCancel={onClose}
      onOk={handleOk}
      okText="创建并指派"
      cancelText="取消"
      confirmLoading={submitting}
      width={640}
      destroyOnClose
    >
      <Alert
        type="info"
        showIcon
        style={{ marginBottom: 16 }}
        message="仅可指派 Available 车辆与司机；车辆载重须足够且保险有效、司机驾照须未过期；已有未结束单据的资源会被拒绝。"
      />
      <Form form={form} layout="vertical" initialValues={{ weight: 1000, freight: 0 }}>
        <Form.Item
          name="vehicleId"
          label="车辆"
          rules={[{ required: true, message: '请选择车辆' }]}
        >
          <Select
            placeholder="选择车辆（仅展示可用车辆）"
            options={vehicles
              .filter((v) => v.status === VehicleStatus.Available)
              .map((v) => ({
                value: v.id,
                label: `${v.plateNo}｜${v.vehicleType ?? v.type}｜载重 ${v.payloadCapacity.toLocaleString()}kg｜保险 ${v.insuranceExpireDate ?? '未登记'}`
              }))}
          />
        </Form.Item>
        {selectedVehicle ? (
          <div style={{ marginTop: -8, marginBottom: 12 }}>
            {overload ? (
              <Tag color="red">超重：当前货物 {weight}kg 超过额定载重 {selectedVehicle.payloadCapacity}kg</Tag>
            ) : (
              <Tag color="green">载重满足要求</Tag>
            )}
            <Tag color={isExpired(selectedVehicle.insuranceExpireDate) ? 'red' : 'green'}>
              保险到期 {selectedVehicle.insuranceExpireDate ?? '未登记'}
            </Tag>
          </div>
        ) : null}

        <Form.Item
          name="driverId"
          label="司机"
          rules={[{ required: true, message: '请选择司机' }]}
        >
          <Select
            placeholder="选择司机（仅展示可用司机）"
            options={drivers
              .filter((d) => d.status === DriverStatus.Available)
              .map((d) => ({
                value: d.id,
                label: `${d.name}｜${d.licenseType}｜${d.phone}｜驾照 ${d.licenseExpireDate ?? '未登记'}`
              }))}
          />
        </Form.Item>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
          <Form.Item name="origin" label="出发地" rules={[{ required: true, message: '请输入出发地' }]}>
            <Input placeholder="如：上海青浦仓" />
          </Form.Item>
          <Form.Item name="destination" label="目的地" rules={[{ required: true, message: '请输入目的地' }]}>
            <Input placeholder="如：杭州萧山仓" />
          </Form.Item>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
          <Form.Item name="weight" label="货物重量 (kg)" rules={[{ required: true, message: '请输入重量' }]}>
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="freight" label="运费 (元)">
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>
        </div>

        <Form.Item name="planRange" label="预计出发 / 到达时间">
          <DatePicker.RangePicker
            showTime={{ format: 'HH:mm' }}
            format="YYYY-MM-DD HH:mm"
            style={{ width: '100%' }}
          />
        </Form.Item>

        <Form.Item name="cargo" label="货物描述">
          <Input placeholder="如：冷链食品" />
        </Form.Item>
        <Form.Item name="note" label="备注">
          <Input.TextArea rows={2} />
        </Form.Item>
      </Form>
    </Modal>
  );
}

function isExpired(date?: string | null): boolean {
  return !!date && dayjs(date).isBefore(dayjs().startOf('day'));
}
