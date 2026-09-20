import { Card, Descriptions, Tag } from 'antd';
import type { Vehicle } from '../../types';
import { StatusBadge } from './StatusBadge';

export function VehicleCard({ vehicle }: { vehicle: Vehicle }) {
  const insuranceExpired =
    vehicle.insuranceExpireDate && new Date(vehicle.insuranceExpireDate) < new Date();
  return (
    <Card
      size="small"
      title={
        <span>
          {vehicle.plateNo}
          <span style={{ marginLeft: 8, color: '#8c8678', fontWeight: 400, fontSize: 12 }}>
            {vehicle.vehicleType ?? vehicle.type}
          </span>
        </span>
      }
      extra={<StatusBadge status={vehicle.status} />}
    >
      <Descriptions column={1} size="small">
        <Descriptions.Item label="品牌型号">{vehicle.brandModel}</Descriptions.Item>
        <Descriptions.Item label="额定载重">{vehicle.payloadCapacity.toLocaleString()} kg</Descriptions.Item>
        <Descriptions.Item label="累计里程">{vehicle.mileage.toLocaleString()} km</Descriptions.Item>
        <Descriptions.Item label="保险到期">
          {vehicle.insuranceExpireDate ?? '—'}
          {insuranceExpired ? <Tag color="red" style={{ marginInlineStart: 8 }}>已过期</Tag> : null}
        </Descriptions.Item>
      </Descriptions>
    </Card>
  );
}
