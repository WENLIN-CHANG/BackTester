import { Card } from '@/components/ui';
import { formatPercent, formatCurrency, formatSharpeRatio } from '@/utils/format';
import type { BacktestResult, ComparisonResult } from '@/types';

interface ResultsTableProps {
  results: BacktestResult[];
  comparison: ComparisonResult;
}

export function ResultsTable({ results, comparison }: ResultsTableProps) {
  return (
    <div className="space-y-4">
      <Card title="回測結果">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-2 px-3 font-semibold text-gray-700">股票</th>
                <th className="text-right py-2 px-3 font-semibold text-gray-700">總報酬率</th>
                <th className="text-right py-2 px-3 font-semibold text-gray-700">年化報酬率</th>
                <th className="text-right py-2 px-3 font-semibold text-gray-700">最大回撤</th>
                <th className="text-right py-2 px-3 font-semibold text-gray-700">波動率</th>
                <th className="text-right py-2 px-3 font-semibold text-gray-700">夏普比率</th>
                <th className="text-right py-2 px-3 font-semibold text-gray-700">最終價值</th>
              </tr>
            </thead>
            <tbody>
              {results.map((result) => (
                <tr key={result.symbol} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-3">
                    <div>
                      <div className="font-medium text-gray-900">{result.symbol}</div>
                      <div className="text-xs text-gray-500">{result.name}</div>
                    </div>
                  </td>
                  <td className={`text-right py-3 px-3 font-medium ${
                    result.total_return >= 0 ? 'text-success-500' : 'text-danger-500'
                  }`}>
                    {formatPercent(result.total_return)}
                  </td>
                  <td className={`text-right py-3 px-3 ${
                    result.cagr >= 0 ? 'text-success-500' : 'text-danger-500'
                  }`}>
                    {formatPercent(result.cagr)}
                  </td>
                  <td className="text-right py-3 px-3 text-danger-500">
                    {formatPercent(result.max_drawdown)}
                  </td>
                  <td className="text-right py-3 px-3 text-gray-700">
                    {formatPercent(result.volatility)}
                  </td>
                  <td className="text-right py-3 px-3 text-gray-700">
                    {formatSharpeRatio(result.sharpe_ratio)}
                  </td>
                  <td className="text-right py-3 px-3 font-medium text-gray-900">
                    {formatCurrency(result.final_value)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      <Card title="投資組合比較">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <div className="text-sm text-gray-500 mb-1">最佳報酬</div>
            <div className="text-lg font-semibold text-success-500">
              {comparison.best_performer.symbol}
            </div>
            <div className="text-sm text-gray-600">
              {formatPercent(comparison.best_performer.total_return)}
            </div>
          </div>

          <div>
            <div className="text-sm text-gray-500 mb-1">最差報酬</div>
            <div className="text-lg font-semibold text-danger-500">
              {comparison.worst_performer.symbol}
            </div>
            <div className="text-sm text-gray-600">
              {formatPercent(comparison.worst_performer.total_return)}
            </div>
          </div>

          <div>
            <div className="text-sm text-gray-500 mb-1">平均報酬率</div>
            <div className={`text-lg font-semibold ${
              comparison.average_return >= 0 ? 'text-success-500' : 'text-danger-500'
            }`}>
              {formatPercent(comparison.average_return)}
            </div>
          </div>

          <div>
            <div className="text-sm text-gray-500 mb-1">總投資金額</div>
            <div className="text-lg font-semibold text-gray-900">
              {formatCurrency(comparison.total_invested)}
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}
