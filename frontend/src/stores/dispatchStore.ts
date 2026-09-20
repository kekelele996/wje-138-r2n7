import { create } from 'zustand';
import { dispatchApi } from '../api/dispatch';
import type { CreateDispatchPayload, DispatchOrder, ReassignPayload } from '../types';

interface DispatchState {
  orders: DispatchOrder[];
  loading: boolean;
  actingId: number | null;
  fetchOrders: (status?: string) => Promise<void>;
  createOrder: (payload: CreateDispatchPayload) => Promise<DispatchOrder>;
  startOrder: (id: number) => Promise<void>;
  completeOrder: (id: number) => Promise<void>;
  cancelOrder: (id: number) => Promise<void>;
  reassignOrder: (id: number, payload: ReassignPayload) => Promise<void>;
}

export const useDispatchStore = create<DispatchState>((set, get) => {
  const applyOrder = (order: DispatchOrder) =>
    set((state) => {
      const exists = state.orders.some((o) => o.id === order.id);
      return {
        orders: exists
          ? state.orders.map((o) => (o.id === order.id ? order : o))
          : [order, ...state.orders]
      };
    });

  const runAction = async (id: number | null, action: () => Promise<unknown>) => {
    set({ actingId: id });
    try {
      await action();
    } finally {
      set({ actingId: null });
    }
  };

  return {
    orders: [],
    loading: false,
    actingId: null,

    fetchOrders: async (status) => {
      set({ loading: true });
      try {
        set({ orders: await dispatchApi.list(status) });
      } finally {
        set({ loading: false });
      }
    },

    createOrder: async (payload) => {
      const order = await dispatchApi.create(payload);
      applyOrder(order);
      return order;
    },

    startOrder: (id) =>
      runAction(id, async () => {
        applyOrder(await dispatchApi.start(id));
        // 开始后车辆/司机状态也已变化，刷新整个列表保证摘要一致
        await get().fetchOrders();
      }),

    completeOrder: (id) =>
      runAction(id, async () => {
        applyOrder(await dispatchApi.complete(id));
        await get().fetchOrders();
      }),

    cancelOrder: (id) =>
      runAction(id, async () => {
        applyOrder(await dispatchApi.cancel(id));
        await get().fetchOrders();
      }),

    reassignOrder: (id, payload) =>
      runAction(id, async () => {
        applyOrder(await dispatchApi.reassign(id, payload));
        await get().fetchOrders();
      })
  };
});
