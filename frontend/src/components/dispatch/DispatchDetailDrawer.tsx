import { Descriptions, Drawer, Space, Tag } from 'antd';
import { DispatchStatus, type DispatchOrder } from '../../types';
import { StatusBadge } from '../common/StatusBadge';
import { Timeline, buildDispatchTimeline } from '../common/Timeline';

interface Props {
  order: DispatchOrder | null;
  onClose: () => void;
}

export function DispatchDetailDrawer({ order, onClose }: Props) {
  if (!order) return <Drawer open={false} onClose={onClose} />;
  const timeline = buildDispatchTimeline(order.timeline);

  return (
    <Drawer
      width={560}
      title={
        <Space>
          <span>{order.orderNo}</span>
          <StatusBadge status={order.status} />
        </Space>
      }
      open={!!order}
      onClose={onClose}
    >
      <Descriptions column={1} bordered size="small">
        <Descriptions.Item label="路线">
          {order.origin} → {order.destination}
        </Descriptions.Item>
        <Descriptions.Item label="车辆">
          {order.vehiclePlateNo}
          <Tag style={{ marginInlineStart: 8 }}>{order.vehicleType}</Tag>
        </Descriptions.Item>
        <Descriptions.Item label="司机">
          {order.driverName}
          <span style={{ color: '#8c8678', marginInlineStart: 8 }}>{order.driverPhone}</span>
        </Descriptions.Item>
        <Descriptions.Item label="货物">
          {order.cargo || '—'}｜{order.weight.toLocaleString()}kg｜运费 ¥{order.freight.toLocaleString()}
        </Descriptions.Item>
        <Descriptions.Item label="预计出发">{order.planDepartAt ?? '—'}</Descriptions.Item>
        <Descriptions.Item label="预计到达">{order.planArriveAt ?? '—'}</Descriptions.Item>
        <Descriptions.Item label="实际出发">
          {order.actualDepartAt ?? (order.status === DispatchStatus.Pending ? '—' : '待发车')}
        </Descriptions.Item>
        <Descriptions.Item label="实际到达">{order.actualArriveAt ?? '—'}</Descriptions.Item>
        {order.note ? <Descriptions.Item label="备注">{order.note}</Descriptions.Item> : null}
      </Descriptions>

      <h3 style={{ margin: '20px 0 12px' }}>运输时间线</h3>
      {timeline.length ? <Timeline items={timeline} /> : <div style={{ color: '#8c8678' }}>暂无事件</div>}
    </Drawer>
  );
}
