import { useEffect, useState } from 'react';
import ReactECharts from 'echarts-for-react';
import { Card, Col, Row, Statistic } from 'antd';
import { fuelApi, type MonthlyFuelSummary } from '../api/fuel';
import type { FuelRecord } from '../types';
import { PageShell } from './PageShell';

export function FuelAnalytics() {
  const [records, setRecords] = useState<FuelRecord[]>([]);
  const [summary, setSummary] = useState<MonthlyFuelSummary[]>([]);

  useEffect(() => {
    fuelApi.list().then(setRecords).catch(() => setRecords([]));
    fuelApi.monthlySummary().then(setSummary).catch(() => setSummary([]));
  }, []);

  const totalLiters = records.reduce((sum, item) => sum + item.liters, 0);
  const totalAmount = records.reduce((sum, item) => sum + item.totalAmount, 0);

  const trendOption = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: records.map((r) => r.date) },
    yAxis: { type: 'value', name: '金额(元)' },
    series: [
      {
        type: 'line',
        name: '加油金额',
        data: records.map((r) => r.totalAmount),
        smooth: true,
        areaStyle: {}
      }
    ]
  };

  const monthlyOption = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: summary.map((s) => s.month ?? '未知') },
    yAxis: { type: 'value', name: '加油量(L)' },
    series: [
      {
        type: 'bar',
        name: '月度总油耗',
        data: summary.map((s) => s.liters),
        itemStyle: { color: '#0f766e' }
      }
    ]
  };

  return (
    <PageShell title="油耗分析">
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={8}>
          <Card>
            <Statistic title="累计加油量" value={totalLiters} precision={1} suffix="L" />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic title="累计加油金额" value={totalAmount} precision={2} prefix="¥" />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic title="加油次数" value={records.length} suffix="次" />
          </Card>
        </Col>
      </Row>
      <div className="grid grid-2">
        <Card title="加油金额趋势">
          <ReactECharts style={{ height: 320 }} option={trendOption} />
        </Card>
        <Card title="月度总油耗">
          <ReactECharts style={{ height: 320 }} option={monthlyOption} />
        </Card>
      </div>
    </PageShell>
  );
}
