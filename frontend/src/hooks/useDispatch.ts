import { DispatchStatus, type DispatchOrder } from '../types';

/**
 * 调度单状态流转规则（前端预判，权威校验仍在后端 dispatch_service）：
 * Assigned  -> InProgress / Cancelled
 * InProgress -> Completed / Cancelled
 * Completed / Cancelled 为终态，禁止任何操作。
 */
export function useDispatch() {
  const canStart = (order: DispatchOrder) => order.status === DispatchStatus.Assigned;
  const canComplete = (order: DispatchOrder) => order.status === DispatchStatus.InProgress;
  const canCancel = (order: DispatchOrder) =>
    order.status === DispatchStatus.Assigned || order.status === DispatchStatus.InProgress;
  // 运输中（InProgress）的单据不得改派、不得重复操作
  const isLocked = (order: DispatchOrder) =>
    order.status === DispatchStatus.InProgress ||
    order.status === DispatchStatus.Completed ||
    order.status === DispatchStatus.Cancelled;
  const nextStatus = (order: DispatchOrder) =>
    order.status === DispatchStatus.Pending
      ? DispatchStatus.Assigned
      : order.status === DispatchStatus.Assigned
        ? DispatchStatus.InProgress
        : DispatchStatus.Completed;
  return { canStart, canComplete, canCancel, isLocked, nextStatus };
}
