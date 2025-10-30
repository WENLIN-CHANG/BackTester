import ReactECharts from "echarts-for-react";
import { Card } from "@/components/ui";
import { CHART_COLORS } from "@/constants";
import { formatCurrency, formatDateString } from "@/utils/format";
import type { BacktestResult } from "@/types";
import type { EChartsOption } from "echarts";

interface PerformanceChartProps {
  results: BacktestResult[];
}

export function PerformanceChart({ results }: PerformanceChartProps) {
  const option: EChartsOption = {
    title: {
      text: "投資組合價值變化",
      left: "center",
      textStyle: {
        fontSize: 20,
        fontWeight: 900, // Neubrutalism: 極粗
        fontFamily: "sans-serif",
        color: "#000000",
      },
    },
    tooltip: {
      trigger: "axis",
      backgroundColor: "#FFFFFF",
      borderColor: "#000000",
      borderWidth: 3,
      textStyle: {
        color: "#000000",
        fontWeight: "bold",
      },
      extraCssText: "box-shadow: 5px 5px 0px #000;",
      formatter: (params: any) => {
        const date = params[0].axisValue;
        let content = `<div style="font-weight: 900; margin-bottom: 8px; text-transform: uppercase;">${date}</div>`;

        params.forEach((param: any) => {
          const value = formatCurrency(param.value);
          content += `
            <div style="display: flex; align-items: center; margin-top: 6px;">
              <span style="display: inline-block; width: 12px; height: 12px; background: ${param.color}; border: 2px solid #000; margin-right: 8px;"></span>
              <span style="flex: 1; font-weight: bold;">${param.seriesName}</span>
              <span style="font-weight: 900; margin-left: 16px; font-family: monospace;">${value}</span>
            </div>
          `;
        });

        return content;
      },
    },
    legend: {
      data: results.map((r) => r.symbol),
      bottom: 10,
      itemWidth: 30,
      itemHeight: 3,
      textStyle: {
        color: "#000000",
        fontWeight: "bold",
        fontSize: 14,
      },
    },
    grid: {
      left: "5%",
      right: "5%",
      bottom: "80px",
      top: "80px",
      containLabel: true,
      borderWidth: 2,
      borderColor: "#000000",
    },
    xAxis: {
      type: "category",
      boundaryGap: false,
      data:
        results[0]?.history.map((h) =>
          formatDateString(h.date, "yyyy/MM/dd"),
        ) || [],
      axisLine: {
        lineStyle: {
          color: "#000000",
          width: 2,
        },
      },
      axisLabel: {
        color: "#000000",
        fontWeight: "bold",
        fontSize: 12,
      },
    },
    yAxis: {
      type: "value",
      axisLine: {
        show: true,
        lineStyle: {
          color: "#000000",
          width: 2,
        },
      },
      axisLabel: {
        color: "#000000",
        fontWeight: "bold",
        fontSize: 12,
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
      splitLine: {
        lineStyle: {
          color: "#E5E5E5",
          width: 1,
          type: "dashed",
        },
      },
    },
    series: results.map((result, index) => ({
      name: result.symbol,
      type: "line",
      smooth: false, // Neubrutalism: 不要平滑，要有稜角
      symbol: "circle",
      symbolSize: 6,
      lineStyle: {
        width: 3, // Neubrutalism: 粗線
        color: CHART_COLORS[index % CHART_COLORS.length],
      },
      itemStyle: {
        borderWidth: 2,
        borderColor: "#000000",
      },
      emphasis: {
        scale: 1.5,
      },
      data: result.history.map((h) => h.value),
      color: CHART_COLORS[index % CHART_COLORS.length],
    })),
  };

  return (
    <Card className="brutalist-tilt-minus-0-5">
      <ReactECharts
        option={option}
        style={{ height: "400px", width: "100%" }}
        opts={{ renderer: "canvas" }}
      />
    </Card>
  );
}
