import { useEffect, useMemo, useState } from 'react';
import { Button, Card, Popconfirm, Space, Table, Tabs, Tag, Typography } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { PlusOutlined, ReloadOutlined } from '@ant-design/icons';
import { DispatchStatus, type DispatchOrder } from '../types';
import { useDispatchStore } from '../stores/dispatchStore';
import { useDispatch } from '../hooks/useDispatch';
import { StatusBadge } from '../components/common/StatusBadge';
import { EmptyState } from '../components/common/EmptyState';
import { CreateDispatchModal } from '../components/dispatch/CreateDispatchModal';
import { ReassignModal } from '../components/dispatch/ReassignModal';
import { DispatchDetailDrawer } from '../components/dispatch/DispatchDetailDrawer';
import { PageShell } from './PageShell';

const TABS = [
  { key: 'all', label: '全部' },
  { key: DispatchStatus.Assigned, label: '已指派' },
  { key: DispatchStatus.InProgress, label: '运输中' },
  { key: DispatchStatus.Completed, label: '已完成' },
  { key: DispatchStatus.Cancelled, label: '已取消' }
];

export function DispatchCenter() {
  const { orders, loading, actingId, fetchOrders } = useDispatchStore();
  const dispatch = useDispatch();
  const [activeTab, setActiveTab] = useState<string>('all');
  const [createOpen, setCreateOpen] = useState(false);
  const [reassignOrder, setReassignOrder] = useState<DispatchOrder | null>(null);
  const [detailOrder, setDetailOrder] = useState<DispatchOrder | null>(null);

  useEffect(() => {
    fetchOrders(activeTab === 'all' ? undefined : activeTab);
  }, [fetchOrders, activeTab]);

  const columns = useMemo<ColumnsType<DispatchOrder>>(
    () => [
      {
        title: '单号',
        dataIndex: 'orderNo',
        width: 180,
        render: (value, record) => (
          <Typography.Link onClick={() => setDetailOrder(record)}>{value}</Typography.Link>
        )
      },
      {
        title: '路线',
        render: (_, record) => (
          <span>
            {record.origin} <span style={{ color: '#0f766e' }}>→</span> {record.destination}
          </span>
        )
      },
      { title: '车辆', dataIndex: 'vehiclePlateNo', width: 120 },
      { title: '司机', dataIndex: 'driverName', width: 100 },
      {
        title: '重量 / 运费',
        width: 150,
        render: (_, record) => (
          <span>
            {record.weight.toLocaleString()}kg
            <br />
            <Typography.Text type="secondary">¥{record.freight.toLocaleString()}</Typography.Text>
          </span>
        )
      },
      { title: '状态', dataIndex: 'status', width: 100, render: (value) => <StatusBadge status={value} /> },
      {
        title: '操作',
        width: 260,
        render: (_, record) => {
          const busy = actingId === record.id;
          return (
            <Space size={4} wrap>
              <Button size="small" onClick={() => setDetailOrder(record)}>
                详情
              </Button>
              {dispatch.canStart(record) ? (
                <Button
                  type="primary"
                  size="small"
                  loading={busy}
                  onClick={() => dispatch.start(record.id)}
                >
                  开始
                </Button>
              ) : null}
              {dispatch.canComplete(record) ? (
                <Button
                  type="primary"
                  size="small"
                  ghost
                  loading={busy}
                  onClick={() => dispatch.complete(record.id)}
                >
                  完成
                </Button>
              ) : null}
              {dispatch.canReassign(record) ? (
                <Button size="small" disabled={busy} onClick={() => setReassignOrder(record)}>
                  改派
                </Button>
              ) : null}
              {dispatch.canCancel(record) ? (
                <Popconfirm
                  title="确认取消该调度单？"
                  description="取消后车辆与司机将恢复 Available"
                  onConfirm={() => dispatch.cancel(record.id)}
                  okText="取消单据"
                  cancelText="再想想"
                  okButtonProps={{ danger: true }}
                >
                  <Button size="small" danger loading={busy}>
                    取消
                  </Button>
                </Popconfirm>
              ) : null}
              {dispatch.isFinished(record) ? <Tag>{record.status === DispatchStatus.Completed ? '已闭环' : '已终止'}</Tag> : null}
            </Space>
          );
        }
      }
    ],
    [actingId, dispatch]
  );

  return (
    <PageShell title="调度中心">
      <Card
        title="调度单"
        extra={
          <Space>
            <Button icon={<ReloadOutlined />} onClick={() => fetchOrders(activeTab === 'all' ? undefined : activeTab)}>
              刷新
            </Button>
            <Button type="primary" icon={<PlusOutlined />} onClick={() => setCreateOpen(true)}>
              创建调度单
            </Button>
          </Space>
        }
      >
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={TABS.map((tab) => ({ key: tab.key, label: tab.label }))}
        />
        <Table
          rowKey="id"
          dataSource={orders}
          columns={columns}
          loading={loading}
          pagination={{ pageSize: 8, showSizeChanger: false }}
          locale={{ emptyText: <EmptyState /> }}
        />
      </Card>

      <CreateDispatchModal
        open={createOpen}
        onClose={() => setCreateOpen(false)}
        onSubmit={dispatch.create}
      />
      <ReassignModal
        order={reassignOrder}
        onClose={() => setReassignOrder(null)}
        onSubmit={(payload) =>
          reassignOrder ? dispatch.reassign(reassignOrder.id, payload) : Promise.resolve(false)
        }
      />
      <DispatchDetailDrawer order={detailOrder} onClose={() => setDetailOrder(null)} />
    </PageShell>
  );
}
