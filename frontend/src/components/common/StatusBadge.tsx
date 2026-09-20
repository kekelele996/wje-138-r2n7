import { Tag } from 'antd';
import { DispatchStatus, DriverStatus, VehicleStatus } from '../../types';

const COLOR_MAP: Record<string, string> = {
  // 车辆状态
  [VehicleStatus.Available]: 'green',
  [VehicleStatus.OnTrip]: 'processing',
  [VehicleStatus.Maintenance]: 'orange',
  [VehicleStatus.Retired]: 'default',
  // 司机状态
  [DriverStatus.Leave]: 'orange',
  [DriverStatus.Suspended]: 'red',
  // 调度单状态
  [DispatchStatus.Pending]: 'default',
  [DispatchStatus.Assigned]: 'blue',
  [DispatchStatus.InProgress]: 'processing',
  [DispatchStatus.Completed]: 'green',
  [DispatchStatus.Cancelled]: 'red'
};

const LABEL_MAP: Record<string, string> = {
  Available: '可用',
  OnTrip: '运输中',
  Maintenance: '维保中',
  Retired: '已报废',
  Leave: '休假',
  Suspended: '停职',
  Pending: '待指派',
  Assigned: '已指派',
  InProgress: '运输中',
  Completed: '已完成',
  Cancelled: '已取消'
};

export function StatusBadge({ status }: { status: string }) {
  return (
    <Tag color={COLOR_MAP[status] ?? 'default'} style={{ marginInlineEnd: 0 }}>
      {LABEL_MAP[status] ?? status}
    </Tag>
  );
}
