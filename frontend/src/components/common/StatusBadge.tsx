import { Tag } from 'antd';

// 不同枚举存在同值状态（车辆/司机共用 Available、OnTrip），映射表按状态字符串维护
const STATUS_COLOR: Record<string, string> = {
  Available: 'green',
  OnTrip: 'processing',
  Maintenance: 'orange',
  Retired: 'default',
  Leave: 'gold',
  Suspended: 'default',
  Pending: 'default',
  Assigned: 'blue',
  InProgress: 'processing',
  Completed: 'green',
  Cancelled: 'red',
};

const STATUS_LABEL: Record<string, string> = {
  Available: '可用',
  OnTrip: '运输中',
  Maintenance: '维保中',
  Retired: '已报废',
  Leave: '休假',
  Suspended: '停用',
  Pending: '待指派',
  Assigned: '已指派',
  InProgress: '运输中',
  Completed: '已完成',
  Cancelled: '已取消',
};

export function StatusBadge({ status }: { status: string }) {
  return <Tag color={STATUS_COLOR[status] ?? 'default'}>{STATUS_LABEL[status] ?? status}</Tag>;
}
