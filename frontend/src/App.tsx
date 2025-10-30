import {
  BacktestForm,
  ResultsTable,
  PerformanceChart,
} from "@/components/features";
import { Spinner, ErrorMessage } from "@/components/ui";
import { useBacktest } from "@/hooks/useBacktest";

function App() {
  const mutation = useBacktest();
  const { data, isPending, isError, error } = mutation;

  return (
    <div className="min-h-screen bg-gradient-to-br from-yellow-100 to-yellow-200">
      {/* Neubrutalism Header with Tilt */}
      <header className="bg-brutal-yellow border-b-4 border-brutal-black shadow-brutal-lg brutalist-tilt-minus-1">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-4xl font-black uppercase tracking-tight text-brutal-black">
            BackTester
          </h1>
          <p className="text-base font-bold uppercase tracking-wide text-brutal-black mt-1">
            投資回測分析系統
          </p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <BacktestForm mutation={mutation} />
          </div>

          <div className="lg:col-span-2">
            {isPending && (
              <div className="flex items-center justify-center h-96">
                <div className="text-center">
                  <Spinner size="lg" />
                  <p className="mt-4 text-base font-bold text-brutal-black uppercase">
                    計算中，請稍候...
                  </p>
                </div>
              </div>
            )}

            {isError && (
              <ErrorMessage
                message={error?.message || "發生錯誤，請稍後再試"}
              />
            )}

            {data && (
              <div className="space-y-6">
                <PerformanceChart results={data.results} />
                <ResultsTable
                  results={data.results}
                  comparison={data.comparison}
                />
              </div>
            )}

            {!isPending && !isError && !data && (
              <div className="flex items-center justify-center h-96 bg-brutal-gray rounded-none border-3 border-dashed border-brutal-black">
                <div className="text-center">
                  <svg
                    className="mx-auto h-20 w-20 text-brutal-black"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    strokeWidth={3}
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                    />
                  </svg>
                  <h3 className="mt-4 text-xl font-black uppercase text-brutal-black">
                    尚無回測結果
                  </h3>
                  <p className="mt-2 text-sm font-bold text-[#666666]">
                    請填寫左側表單開始回測
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Neubrutalism Footer */}
      <footer className="bg-brutal-black border-t-5 border-brutal-black mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm font-bold uppercase tracking-wide text-white">
            BackTester - 投資回測分析系統 © {new Date().getFullYear()}
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
