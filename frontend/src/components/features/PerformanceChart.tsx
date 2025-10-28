import ReactECharts from 'echarts-for-react';
import { Card } from '@/components/ui';
import { CHART_COLORS } from '@/constants';
import { formatCurrency, formatDateString } from '@/utils/format';
import type { BacktestResult } from '@/types';
import type { EChartsOption } from 'echarts';

interface PerformanceChartProps {
  results: BacktestResult[];
}

export function PerformanceChart({ results }: PerformanceChartProps) {
  const option: EChartsOption = {
    title: {
      text: '投資組合價值變化',
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 600,
      },
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const date = params[0].axisValue;
        let content = `<div style="font-weight: 600; margin-bottom: 4px;">${date}</div>`;

        params.forEach((param: any) => {
          const value = formatCurrency(param.value);
          content += `
            <div style="display: flex; align-items: center; margin-top: 4px;">
              <span style="display: inline-block; width: 10px; height: 10px; background: ${param.color}; border-radius: 50%; margin-right: 8px;"></span>
              <span style="flex: 1;">${param.seriesName}</span>
              <span style="font-weight: 600; margin-left: 16px;">${value}</span>
            </div>
          `;
        });

        return content;
      },
    },
    legend: {
      data: results.map((r) => r.symbol),
      bottom: 0,
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '60px',
      top: '60px',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: results[0]?.history.map((h) => formatDateString(h.date, 'yyyy/MM/dd')) || [],
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: (value: number) => {
          if (value >= 1000000) {
            return `${(value / 1000000).toFixed(1)}M`;
          }
          if (value >= 1000) {
            return `${(value / 1000).toFixed(0)}K`;
          }
          return value.toFixed(0);
        },
      },
    },
    series: results.map((result, index) => ({
      name: result.symbol,
      type: 'line',
      smooth: true,
      symbol: 'none',
      lineStyle: {
        width: 2,
      },
      data: result.history.map((h) => h.value),
      color: CHART_COLORS[index % CHART_COLORS.length],
    })),
  };

  return (
    <Card>
      <ReactECharts
        option={option}
        style={{ height: '400px', width: '100%' }}
        opts={{ renderer: 'canvas' }}
      />
    </Card>
  );
}
