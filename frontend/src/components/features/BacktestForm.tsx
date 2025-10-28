import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import type { UseMutationResult } from '@tanstack/react-query';
import { Card, Input, Button } from '@/components/ui';
import { StockSelector } from './StockSelector';
import { DEFAULT_VALUES, LIMITS } from '@/constants';
import type { BacktestRequest, BacktestResponse } from '@/types';

const backtestSchema = z.object({
  stocks: z.array(z.string().min(1, '股票代碼不能為空')).min(1).max(LIMITS.MAX_STOCKS),
  start_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, '日期格式錯誤'),
  end_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, '日期格式錯誤'),
  strategy: z.enum(['lump_sum', 'dca']),
  investment: z.object({
    amount: z.number()
      .min(LIMITS.MIN_INVESTMENT, `投資金額最少為 ${LIMITS.MIN_INVESTMENT.toLocaleString()} 元`)
      .max(LIMITS.MAX_INVESTMENT, `投資金額最多為 ${LIMITS.MAX_INVESTMENT.toLocaleString()} 元`)
      .multipleOf(LIMITS.MIN_INVESTMENT_STEP, `投資金額必須是 ${LIMITS.MIN_INVESTMENT_STEP} 的倍數`),
  }),
}).refine((data) => new Date(data.end_date) > new Date(data.start_date), {
  message: '結束日期必須晚於開始日期',
  path: ['end_date'],
});

type BacktestFormData = z.infer<typeof backtestSchema>;

interface BacktestFormProps {
  mutation: UseMutationResult<BacktestResponse, Error, BacktestRequest>;
}

export function BacktestForm({ mutation }: BacktestFormProps) {
  const { mutate, isPending } = mutation;

  const { control, handleSubmit, formState: { errors } } = useForm<BacktestFormData>({
    resolver: zodResolver(backtestSchema),
    defaultValues: {
      stocks: DEFAULT_VALUES.STOCKS,
      start_date: DEFAULT_VALUES.START_DATE,
      end_date: DEFAULT_VALUES.END_DATE,
      strategy: DEFAULT_VALUES.STRATEGY,
      investment: {
        amount: DEFAULT_VALUES.INVESTMENT_AMOUNT,
      },
    },
  });

  const onSubmit = (data: BacktestFormData) => {
    const request: BacktestRequest = {
      ...data,
      stocks: data.stocks.map((s) => s.trim().toUpperCase()),
    };

    mutate(request);
  };

  return (
    <Card title="回測設定">
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <Controller
          name="stocks"
          control={control}
          render={({ field }) => (
            <StockSelector stocks={field.value} onChange={field.onChange} />
          )}
        />

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Controller
            name="start_date"
            control={control}
            render={({ field }) => (
              <Input
                type="date"
                label="開始日期"
                error={errors.start_date?.message}
                {...field}
              />
            )}
          />

          <Controller
            name="end_date"
            control={control}
            render={({ field }) => (
              <Input
                type="date"
                label="結束日期"
                error={errors.end_date?.message}
                {...field}
              />
            )}
          />
        </div>

        <Controller
          name="strategy"
          control={control}
          render={({ field }) => (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                投資策略
              </label>
              <div className="flex gap-4">
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="lump_sum"
                    checked={field.value === 'lump_sum'}
                    onChange={field.onChange}
                    className="mr-2"
                  />
                  單筆投資
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="dca"
                    checked={field.value === 'dca'}
                    onChange={field.onChange}
                    className="mr-2"
                  />
                  定期定額
                </label>
              </div>
            </div>
          )}
        />

        <Controller
          name="investment.amount"
          control={control}
          render={({ field }) => (
            <Input
              type="number"
              label="投資金額（元）"
              placeholder="10000"
              error={errors.investment?.amount?.message}
              {...field}
              onChange={(e) => field.onChange(Number(e.target.value))}
            />
          )}
        />

        <Button type="submit" loading={isPending} className="w-full">
          {isPending ? '計算中...' : '開始回測'}
        </Button>
      </form>
    </Card>
  );
}
