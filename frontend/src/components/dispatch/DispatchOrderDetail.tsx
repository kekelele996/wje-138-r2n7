import { Descriptions, Empty } from 'antd';
import { DispatchStatus, type DispatchOrder } from '../../types';
import { StatusBadge } from '../common/StatusBadge';
import { Timeline } from '../common/Timeline';

const EVENT_COLOR: Record<string, string> = {
  [DispatchStatus.Assigned]: 'blue',
  [DispatchStatus.InProgress]: 'blue',
  [DispatchStatus.Completed]: 'green',
  [DispatchStatus.Cancelled]: 'red'
};

/** 调度单详情：基本信息 + 持久化的状态流转时间线（含每个变化的时间）。 */
export function DispatchOrderDetail({ order }: { order: DispatchOrder | null }) {
  if (!order) {
    return <Empty description="请选择左侧单据查看运输时间线" />;
  }

  return (
    <div>
      <Descriptions
        title={`${order.orderNo}`}
        size="small"
        column={1}
        extra={<StatusBadge status={order.status} />}
        bordered
      >
        <Descriptions.Item label="车辆">
          {order.vehicle ? `${order.vehicle.plateNo} · ${order.vehicle.brandModel}` : order.vehicleId}
        </Descriptions.Item>
        <Descriptions.Item label="司机">
          {order.driver ? `${order.driver.name} · ${order.driver.phone}` : order.driverId}
        </Descriptions.Item>
        <Descriptions.Item label="路线">{order.origin} → {order.destination}</Descriptions.Item>
        <Descriptions.Item label="货物">{order.cargo}（{order.weight}kg / {order.freight} 元）</Descriptions.Item>
        <Descriptions.Item label="预计时间">
          {order.planDepartAt ?? '-'} ~ {order.planArriveAt ?? '-'}
        </Descriptions.Item>
        <Descriptions.Item label="实际出发">{order.actualDepartAt ?? '-'}</Descriptions.Item>
        <Descriptions.Item label="实际到达">{order.actualArriveAt ?? '-'}</Descriptions.Item>
        {order.note ? <Descriptions.Item label="备注">{order.note}</Descriptions.Item> : null}
      </Descriptions>

      <h4 style={{ margin: '16px 0 8px' }}>运输时间线</h4>
      <Timeline
        items={(order.events ?? []).map((event) => ({
          children: `${event.remark}：${event.fromStatus ? `${event.fromStatus} → ` : ''}${event.toStatus}`,
          time: event.createdAt,
          color: EVENT_COLOR[event.toStatus] ?? 'gray'
        }))}
      />
    </div>
  );
}
