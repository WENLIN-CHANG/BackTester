import { BacktestForm, ResultsTable, PerformanceChart } from '@/components/features';
import { Spinner, ErrorMessage } from '@/components/ui';
import { useBacktest } from '@/hooks/useBacktest';

function App() {
  const mutation = useBacktest();
  const { data, isPending, isError, error } = mutation;

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-2xl font-bold text-gray-900">BackTester</h1>
          <p className="text-sm text-gray-600 mt-1">投資回測分析系統</p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <BacktestForm mutation={mutation} />
          </div>

          <div className="lg:col-span-2">
            {isPending && (
              <div className="flex items-center justify-center h-96">
                <div className="text-center">
                  <Spinner size="lg" />
                  <p className="mt-4 text-gray-600">計算中，請稍候...</p>
                </div>
              </div>
            )}

            {isError && (
              <ErrorMessage
                message={error?.message || '發生錯誤，請稍後再試'}
              />
            )}

            {data && (
              <div className="space-y-6">
                <PerformanceChart results={data.results} />
                <ResultsTable results={data.results} comparison={data.comparison} />
              </div>
            )}

            {!isPending && !isError && !data && (
              <div className="flex items-center justify-center h-96 bg-white rounded-lg border-2 border-dashed border-gray-300">
                <div className="text-center">
                  <svg
                    className="mx-auto h-12 w-12 text-gray-400"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                    />
                  </svg>
                  <h3 className="mt-2 text-sm font-medium text-gray-900">尚無回測結果</h3>
                  <p className="mt-1 text-sm text-gray-500">請填寫左側表單開始回測</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <p className="text-center text-sm text-gray-500">
            BackTester - 投資回測分析系統 © {new Date().getFullYear()}
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
