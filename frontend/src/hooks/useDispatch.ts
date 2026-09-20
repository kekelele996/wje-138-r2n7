import { useCallback } from 'react';
import { message } from 'antd';
import { DispatchStatus, type DispatchOrder } from '../types';
import type { CreateDispatchPayload, ReassignPayload } from '../types';
import { useDispatchStore } from '../stores/dispatchStore';

export function useDispatch() {
  const {
    createOrder,
    startOrder,
    completeOrder,
    cancelOrder,
    reassignOrder,
    actingId
  } = useDispatchStore();

  const canCreate = true;
  const canStart = (order: DispatchOrder) => order.status === DispatchStatus.Assigned;
  const canComplete = (order: DispatchOrder) => order.status === DispatchStatus.InProgress;
  const canCancel = (order: DispatchOrder) =>
    order.status === DispatchStatus.Assigned || order.status === DispatchStatus.InProgress;
  // 运输中的单据不得改派
  const canReassign = (order: DispatchOrder) => order.status === DispatchStatus.Assigned;

  const isFinished = (order: DispatchOrder) =>
    order.status === DispatchStatus.Completed || order.status === DispatchStatus.Cancelled;

  const nextStatus = (order: DispatchOrder) =>
    order.status === DispatchStatus.Pending
      ? DispatchStatus.Assigned
      : order.status === DispatchStatus.Assigned
        ? DispatchStatus.InProgress
        : DispatchStatus.Completed;

  const run = useCallback(
    async (
      actionName: string,
      fn: () => Promise<unknown>,
      successText?: string
    ): Promise<boolean> => {
      try {
        await fn();
        message.success(successText ?? `${actionName}成功`);
        return true;
      } catch (err) {
        const reason = err instanceof Error ? err.message : `${actionName}失败`;
        message.error({ content: `${actionName}失败：${reason}`, duration: 5 });
        return false;
      }
    },
    []
  );

  const create = useCallback(
    (payload: CreateDispatchPayload) => run('创建调度单', () => createOrder(payload), '调度单创建成功'),
    [createOrder, run]
  );
  const start = useCallback(
    (id: number) => run('开始运输', () => startOrder(id), '运输已开始，车辆与司机切换为 OnTrip'),
    [startOrder, run]
  );
  const complete = useCallback(
    (id: number) => run('完成运输', () => completeOrder(id), '运输已完成，车辆与司机恢复 Available'),
    [completeOrder, run]
  );
  const cancel = useCallback(
    (id: number) => run('取消调度单', () => cancelOrder(id), '调度单已取消，资源已释放'),
    [cancelOrder, run]
  );
  const reassign = useCallback(
    (id: number, payload: ReassignPayload) =>
      run('改派', () => reassignOrder(id, payload), '改派成功'),
    [reassignOrder, run]
  );

  return {
    canCreate,
    canStart,
    canComplete,
    canCancel,
    canReassign,
    isFinished,
    nextStatus,
    actingId,
    create,
    start,
    complete,
    cancel,
    reassign
  };
}
