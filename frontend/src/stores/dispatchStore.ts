import { create } from 'zustand';
import { DispatchStatus, type DispatchCreatePayload, type DispatchOrder } from '../types';
import { dispatchApi } from '../api/dispatch';

type DispatchState = {
  orders: DispatchOrder[];
  loading: boolean;
  actingId: number | null;
  fetchOrders: (status?: string) => Promise<void>;
  createOrder: (payload: DispatchCreatePayload) => Promise<DispatchOrder>;
  startOrder: (id: number) => Promise<DispatchOrder>;
  completeOrder: (id: number) => Promise<DispatchOrder>;
  cancelOrder: (id: number) => Promise<DispatchOrder>;
};

const ACTIVE_STATUSES: DispatchStatus[] = [DispatchStatus.Assigned, DispatchStatus.InProgress];

export const useDispatchStore = create<DispatchState>((set) => ({
  orders: [],
  loading: false,
  actingId: null,

  fetchOrders: async (status) => {
    set({ loading: true });
    try {
      const orders = await dispatchApi.list(status);
      set({ orders });
    } finally {
      set({ loading: false });
    }
  },

  // 创建成功后把新单据合并到列表，避免重新拉取丢失当前 Tab
  createOrder: async (payload) => {
    const created = await dispatchApi.create(payload);
    set((state) => ({ orders: [created, ...state.orders] }));
    return created;
  },

  // start/complete/cancel 均由后端做状态机校验，失败（冲突/重复操作）时抛出带原因的错误
  startOrder: async (id) => {
    set({ actingId: id });
    try {
      const updated = await dispatchApi.start(id);
      set((state) => ({ orders: state.orders.map((o) => (o.id === id ? updated : o)) }));
      return updated;
    } finally {
      set({ actingId: null });
    }
  },

  completeOrder: async (id) => {
    set({ actingId: id });
    try {
      const updated = await dispatchApi.complete(id);
      set((state) => ({ orders: state.orders.map((o) => (o.id === id ? updated : o)) }));
      return updated;
    } finally {
      set({ actingId: null });
    }
  },

  cancelOrder: async (id) => {
    set({ actingId: id });
    try {
      const updated = await dispatchApi.cancel(id);
      set((state) => ({ orders: state.orders.map((o) => (o.id === id ? updated : o)) }));
      return updated;
    } finally {
      set({ actingId: null });
    }
  }
}));

/** 未结束单据占用的车辆/司机 ID（Assigned、InProgress），创建表单中需禁用这些选项。 */
export function selectOccupied(orders: DispatchOrder[]) {
  const vehicleIds = new Set<number>();
  const driverIds = new Set<number>();
  for (const order of orders) {
    if (ACTIVE_STATUSES.includes(order.status)) {
      vehicleIds.add(order.vehicleId);
      driverIds.add(order.driverId);
    }
  }
  return { vehicleIds, driverIds };
}
