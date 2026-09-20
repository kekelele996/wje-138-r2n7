import { Timeline as AntTimeline } from 'antd';

type TimelineNode = {
  children: React.ReactNode;
  time?: string;
  color?: string;
};

/** 支持纯字符串节点或带时间戳的状态事件节点（调度时间线）。 */
export function Timeline({ items }: { items: Array<string | TimelineNode> }) {
  return (
    <AntTimeline
      items={items.map((item) =>
        typeof item === 'string'
          ? { children: item }
          : { children: item.children, color: item.color, label: item.time }
      )}
    />
  );
}
