import { Card } from "@/components/ui";
import {
  formatPercent,
  formatCurrency,
  formatSharpeRatio,
} from "@/utils/format";
import type { BacktestResult, ComparisonResult } from "@/types";

interface ResultsTableProps {
  results: BacktestResult[];
  comparison: ComparisonResult;
}

export function ResultsTable({ results, comparison }: ResultsTableProps) {
  return (
    <div className="space-y-4">
      <Card title="回測結果" className="brutalist-tilt-0-5">
        <div className="overflow-x-auto border-4 border-brutal-black">
          <table className="w-full border-collapse">
            <thead className="bg-brutal-black text-white">
              <tr>
                <th className="text-left px-6 py-4 text-sm font-black uppercase tracking-wider border-r-2 border-white">
                  股票
                </th>
                <th className="text-right px-6 py-4 text-sm font-black uppercase tracking-wider border-r-2 border-white">
                  總報酬率
                </th>
                <th className="text-right px-6 py-4 text-sm font-black uppercase tracking-wider border-r-2 border-white">
                  年化報酬率
                </th>
                <th className="text-right px-6 py-4 text-sm font-black uppercase tracking-wider border-r-2 border-white">
                  最大回撤
                </th>
                <th className="text-right px-6 py-4 text-sm font-black uppercase tracking-wider border-r-2 border-white">
                  波動率
                </th>
                <th className="text-right px-6 py-4 text-sm font-black uppercase tracking-wider border-r-2 border-white">
                  夏普比率
                </th>
                <th className="text-right px-6 py-4 text-sm font-black uppercase tracking-wider">
                  最終價值
                </th>
              </tr>
            </thead>
            <tbody>
              {results.map((result) => (
                <tr
                  key={result.symbol}
                  className="border-b-2 border-brutal-black transition-all duration-150 hover:bg-brutal-yellow hover:translate-x-[-1px] hover:translate-y-[-1px]"
                >
                  <td className="px-6 py-4 border-r-2 border-[#E5E5E5]">
                    <div>
                      <div className="font-bold text-base text-brutal-black">
                        {result.symbol}
                      </div>
                      <div className="text-sm font-medium text-[#666666]">
                        {result.name}
                      </div>
                    </div>
                  </td>
                  <td
                    className={`text-right px-6 py-4 text-base font-mono font-bold border-r-2 border-[#E5E5E5] ${
                      result.total_return >= 0
                        ? "text-success-500"
                        : "text-danger-500"
                    }`}
                  >
                    {formatPercent(result.total_return)}
                  </td>
                  <td
                    className={`text-right px-6 py-4 text-base font-mono font-bold border-r-2 border-[#E5E5E5] ${
                      result.cagr >= 0 ? "text-success-500" : "text-danger-500"
                    }`}
                  >
                    {formatPercent(result.cagr)}
                  </td>
                  <td className="text-right px-6 py-4 text-base font-mono font-bold text-danger-500 border-r-2 border-[#E5E5E5]">
                    {formatPercent(result.max_drawdown)}
                  </td>
                  <td className="text-right px-6 py-4 text-base font-mono font-bold text-brutal-black border-r-2 border-[#E5E5E5]">
                    {formatPercent(result.volatility)}
                  </td>
                  <td className="text-right px-6 py-4 text-base font-mono font-bold text-brutal-black border-r-2 border-[#E5E5E5]">
                    {formatSharpeRatio(result.sharpe_ratio)}
                  </td>
                  <td className="text-right px-6 py-4 text-base font-mono font-bold text-brutal-black">
                    {formatCurrency(result.final_value)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Neubrutalism 強調卡片 with Tilt */}
      <div className="bg-brutal-yellow border-4 border-brutal-black shadow-brutal-lg p-10 brutalist-tilt-1">
        <h3 className="text-3xl font-black uppercase tracking-wide text-brutal-black mb-8 text-center">
          投資組合比較
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {/* 最佳報酬 - 傾斜 -0.5° */}
          <div className="text-center p-6 bg-white border-4 border-brutal-black shadow-brutal-md brutalist-tilt-minus-0-5">
            <div className="text-sm font-black uppercase tracking-wide text-brutal-black mb-3">
              最佳報酬
            </div>
            <div className="text-4xl font-black font-mono text-success-500 mb-2">
              {comparison.best_performer.symbol}
            </div>
            <div className="text-base font-bold text-brutal-black">
              {formatPercent(comparison.best_performer.total_return)}
            </div>
          </div>

          {/* 最差報酬 - 傾斜 0.5° */}
          <div className="text-center p-6 bg-white border-4 border-brutal-black shadow-brutal-md brutalist-tilt-0-5">
            <div className="text-sm font-black uppercase tracking-wide text-brutal-black mb-3">
              最差報酬
            </div>
            <div className="text-4xl font-black font-mono text-danger-500 mb-2">
              {comparison.worst_performer.symbol}
            </div>
            <div className="text-base font-bold text-brutal-black">
              {formatPercent(comparison.worst_performer.total_return)}
            </div>
          </div>

          {/* 平均報酬率 - 傾斜 1° */}
          <div className="text-center p-6 bg-white border-4 border-brutal-black shadow-brutal-md brutalist-tilt-1">
            <div className="text-sm font-black uppercase tracking-wide text-brutal-black mb-3">
              平均報酬率
            </div>
            <div
              className={`text-4xl font-black font-mono mb-2 ${
                comparison.average_return >= 0
                  ? "text-success-500"
                  : "text-danger-500"
              }`}
            >
              {formatPercent(comparison.average_return)}
            </div>
          </div>

          {/* 總投資金額 - 傾斜 -1° */}
          <div className="text-center p-6 bg-white border-4 border-brutal-black shadow-brutal-md brutalist-tilt-minus-1">
            <div className="text-sm font-black uppercase tracking-wide text-brutal-black mb-3">
              總投資金額
            </div>
            <div className="text-3xl font-black font-mono text-brutal-black">
              {formatCurrency(comparison.total_invested)}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
