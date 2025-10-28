import { useState } from 'react';
import { Input, Button } from '@/components/ui';
import { normalizeStockSymbol, getStockSymbolError } from '@/utils/validation';
import { LIMITS } from '@/constants';

interface StockSelectorProps {
  stocks: string[];
  onChange: (stocks: string[]) => void;
}

export function StockSelector({ stocks, onChange }: StockSelectorProps) {
  const [errors, setErrors] = useState<Record<number, string>>({});

  const handleStockChange = (index: number, value: string) => {
    const newStocks = [...stocks];
    newStocks[index] = value;
    onChange(newStocks);

    const normalized = normalizeStockSymbol(value);
    const error = getStockSymbolError(normalized);
    setErrors((prev) => ({
      ...prev,
      [index]: error,
    }));
  };

  const handleAddStock = () => {
    if (stocks.length < LIMITS.MAX_STOCKS) {
      onChange([...stocks, '']);
    }
  };

  const handleRemoveStock = (index: number) => {
    if (stocks.length > LIMITS.MIN_STOCKS) {
      const newStocks = stocks.filter((_, i) => i !== index);
      onChange(newStocks);

      const newErrors = { ...errors };
      delete newErrors[index];
      setErrors(newErrors);
    }
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="block text-sm font-medium text-gray-700">
          股票代碼 ({stocks.length}/{LIMITS.MAX_STOCKS})
        </label>
        {stocks.length < LIMITS.MAX_STOCKS && (
          <Button size="sm" onClick={handleAddStock}>
            + 新增股票
          </Button>
        )}
      </div>

      <div className="space-y-2">
        {stocks.map((stock, index) => (
          <div key={index} className="flex gap-2">
            <div className="flex-1">
              <Input
                value={stock}
                onChange={(e) => handleStockChange(index, e.target.value)}
                placeholder="例如：AAPL 或 2330.TW"
                error={errors[index]}
              />
            </div>
            {stocks.length > LIMITS.MIN_STOCKS && (
              <Button
                variant="danger"
                size="sm"
                onClick={() => handleRemoveStock(index)}
              >
                刪除
              </Button>
            )}
          </div>
        ))}
      </div>

      <p className="text-xs text-gray-500">
        支援美股（如 AAPL）和台股（如 2330.TW）
      </p>
    </div>
  );
}
