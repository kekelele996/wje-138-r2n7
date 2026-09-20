import { useEffect, useMemo, useState } from 'react';
import { App, Button, Card, Popconfirm, Space, Table, Tabs } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { vehicleApi } from '../api/vehicle';
import { driverApi } from '../api/driver';
import { DispatchStatus, type DispatchCreatePayload, type DispatchOrder, type Driver, type Vehicle } from '../types';
import { selectOccupied, useDispatchStore } from '../stores/dispatchStore';
import { useDispatch } from '../hooks/useDispatch';
import { ApiError } from '../utils/request';
import { StatusBadge } from '../components/common/StatusBadge';
import { PageShell } from './PageShell';
import { DispatchCreateModal } from '../components/dispatch/DispatchCreateModal';
import { DispatchOrderDetail } from '../components/dispatch/DispatchOrderDetail';

const TABS = [
  { key: 'all', label: '全部' },
  { key: DispatchStatus.Assigned, label: '已指派' },
  { key: DispatchStatus.InProgress, label: '运输中' },
  { key: DispatchStatus.Completed, label: '已完成' },
  { key: DispatchStatus.Cancelled, label: '已取消' }
];

export function DispatchCenter() {
  const { message } = App.useApp();
  const { orders, loading, actingId, fetchOrders, createOrder, startOrder, completeOrder, cancelOrder } =
    useDispatchStore();
  const { canStart, canComplete, canCancel } = useDispatch();

  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [drivers, setDrivers] = useState<Driver[]>([]);
  const [tab, setTab] = useState<string>('all');
  const [createOpen, setCreateOpen] = useState(false);
  const [creating, setCreating] = useState(false);
  const [selectedId, setSelectedId] = useState<number | null>(null);

  useEffect(() => {
    fetchOrders().catch((err) => message.error(err instanceof ApiError ? err.message : '调度单加载失败'));
    vehicleApi.list<Vehicle>().then(setVehicles).catch(() => setVehicles([]));
    driverApi.list<Driver>().then(setDrivers).catch(() => setDrivers([]));
  }, [fetchOrders, message]);

  // 未结束单据占用的车辆/司机
  const { vehicleIds, driverIds } = useMemo(() => selectOccupied(orders), [orders]);

  const filteredOrders = useMemo(
    () => (tab === 'all' ? orders : orders.filter((o) => o.status === tab)),
    [orders, tab]
  );

  const selectedOrder = useMemo(
    () => orders.find((o) => o.id === selectedId) ?? filteredOrders[0] ?? null,
    [orders, selectedId, filteredOrders]
  );

  const showError = (err: unknown, fallback: string) => {
    message.error(err instanceof ApiError ? err.message : fallback);
  };

  const handleCreate = async (payload: DispatchCreatePayload) => {
    setCreating(true);
    try {
      const order = await createOrder(payload);
      message.success(`调度单 ${order.orderNo} 创建成功，车辆与司机已指派`);
      setCreateOpen(false);
      setTab('all');
      setSelectedId(order.id);
    } catch (err) {
      // 冲突/非法状态：直接展示后端返回的中文原因
      showError(err, '创建调度单失败');
    } finally {
      setCreating(false);
    }
  };

  const handleAction = async (
    action: () => Promise<DispatchOrder>,
    successText: string,
    fallback: string
  ) => {
    try {
      const order = await action();
      message.success(`${successText}：${order.orderNo}`);
      // 状态变化后刷新资源占用（车辆/司机状态），保证下拉禁用最新
      vehicleApi.list<Vehicle>().then(setVehicles).catch(() => undefined);
      driverApi.list<Driver>().then(setDrivers).catch(() => undefined);
    } catch (err) {
      showError(err, fallback);
    }
  };

  const columns: ColumnsType<DispatchOrder> = [
    { title: '单号', dataIndex: 'orderNo', width: 180 },
    {
      title: '车辆',
      render: (_, r) => (r.vehicle ? `${r.vehicle.plateNo}` : r.vehicleId),
    },
    { title: '司机', render: (_, r) => (r.driver ? r.driver.name : r.driverId) },
    { title: '路线', render: (_, r) => `${r.origin} → ${r.destination}` },
    { title: '重量(kg)', dataIndex: 'weight', width: 100 },
    {
      title: '状态',
      width: 100,
      render: (_, r) => <StatusBadge status={r.status} />,
    },
    {
      title: '操作',
      width: 240,
      render: (_, r) => (
        <Space size="small">
          <Button
            size="small"
            type="primary"
            loading={actingId === r.id}
            disabled={!canStart(r)}
            onClick={() => handleAction(() => startOrder(r.id), '运输已开始，车辆/司机切换为 OnTrip', '开始运输失败')}
          >
            开始
          </Button>
          <Button
            size="small"
            loading={actingId === r.id}
            disabled={!canComplete(r)}
            onClick={() => handleAction(() => completeOrder(r.id), '运输已完成，资源恢复 Available', '完成运输失败')}
          >
            完成
          </Button>
          <Popconfirm
            title="取消该调度单？"
            description="取消后车辆与司机恢复可用，操作不可撤销"
            okText="确认取消"
            cancelText="再想想"
            okButtonProps={{ danger: true }}
            disabled={!canCancel(r)}
            onConfirm={() => handleAction(() => cancelOrder(r.id), '调度单已取消，资源恢复 Available', '取消失败')}
          >
            <Button size="small" danger disabled={!canCancel(r)} loading={actingId === r.id}>
              取消
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <PageShell title="调度中心">
      <div className="grid grid-2">
        <Card
          title="调度单"
          extra={
            <Button type="primary" onClick={() => setCreateOpen(true)}>
              创建调度单
            </Button>
          }
        >
          <Tabs
            activeKey={tab}
            onChange={setTab}
            items={TABS.map((t) => ({ key: t.key, label: t.label }))}
            style={{ marginBottom: 8 }}
          />
          <Table
            rowKey="id"
            size="small"
            loading={loading}
            dataSource={filteredOrders}
            columns={columns}
            pagination={false}
            rowClassName={(r) => (r.id === selectedOrder?.id ? 'ant-table-row-selected' : '')}
            onRow={(r) => ({ onClick: () => setSelectedId(r.id) })}
          />
        </Card>

        <Card title="调度单详情 / 运输时间线">
          <DispatchOrderDetail order={selectedOrder} />
        </Card>
      </div>

      <DispatchCreateModal
        open={createOpen}
        loading={creating}
        vehicles={vehicles}
        drivers={drivers}
        occupiedVehicleIds={vehicleIds}
        occupiedDriverIds={driverIds}
        onCancel={() => setCreateOpen(false)}
        onSubmit={handleCreate}
      />
    </PageShell>
  );
}
