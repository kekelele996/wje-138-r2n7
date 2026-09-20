import { Timeline as AntTimeline } from 'antd';

export interface TimelineEntry {
  title: string;
  time?: string;
  description?: string;
  color?: string;
}

const EVENT_COLOR: Record<string, string> = {
  Created: 'blue',
  Assigned: 'blue',
  Reassigned: 'gold',
  Started: 'processing',
  Completed: 'green',
  Cancelled: 'red'
};

const EVENT_LABEL: Record<string, string> = {
  Created: '创建调度单',
  Assigned: '指派车辆与司机',
  Reassigned: '改派',
  Started: '开始运输',
  Completed: '完成运输',
  Cancelled: '取消调度单'
};

export function Timeline({ items }: { items: Array<string | TimelineEntry> }) {
  const timelineItems = items.map((item) =>
    typeof item === 'string'
      ? { children: item, color: 'gray' }
      : {
          color: item.color ?? 'blue',
          children: (
            <div>
              <div style={{ fontWeight: 600 }}>{item.title}</div>
              {item.time ? (
                <div style={{ color: '#8c8678', fontSize: 12 }}>{formatTime(item.time)}</div>
              ) : null}
              {item.description ? (
                <div style={{ color: '#5f5a50', fontSize: 13 }}>{item.description}</div>
              ) : null}
            </div>
          )
        }
  );
  return <AntTimeline items={timelineItems} />;
}

export function buildDispatchTimeline(
  events?: Array<{ eventType: string; detail: string; time: string }>
): TimelineEntry[] {
  if (!events?.length) return [];
  return events.map((event) => ({
    title: EVENT_LABEL[event.eventType] ?? event.eventType,
    time: event.time,
    description: event.detail,
    color: EVENT_COLOR[event.eventType] ?? 'blue'
  }));
}

function formatTime(iso: string): string {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return iso;
  const pad = (value: number) => String(value).padStart(2, '0');
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(
    date.getHours()
  )}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
}
