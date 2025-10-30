import { describe, it, expect } from "vitest";
import {
  isValidStockSymbol,
  isTaiwanStock,
  isUSStock,
  normalizeStockSymbol,
  isValidDateString,
  isValidDateRange,
  isNotFutureDate,
  isValidAmount,
  isValidAmountStep,
  isValidStockList,
  removeDuplicateStocks,
  getStockSymbolError,
  getDateRangeError,
  getAmountError,
} from "./validation";

describe("isValidStockSymbol", () => {
  it("validates correct stock symbols", () => {
    expect(isValidStockSymbol("AAPL")).toBe(true);
    expect(isValidStockSymbol("2330.TW")).toBe(true);
    expect(isValidStockSymbol("BRK.A")).toBe(true);
  });

  it("rejects invalid symbols", () => {
    expect(isValidStockSymbol("")).toBe(false);
    expect(isValidStockSymbol("   ")).toBe(false);
    expect(isValidStockSymbol("aapl")).toBe(false);
    expect(isValidStockSymbol("AAPL-")).toBe(false);
  });
});

describe("isTaiwanStock", () => {
  it("identifies Taiwan stocks", () => {
    expect(isTaiwanStock("2330.TW")).toBe(true);
    expect(isTaiwanStock("1234.TWO")).toBe(true);
  });

  it("rejects non-Taiwan stocks", () => {
    expect(isTaiwanStock("AAPL")).toBe(false);
    expect(isTaiwanStock("2330")).toBe(false);
  });
});

describe("isUSStock", () => {
  it("identifies US stocks", () => {
    expect(isUSStock("AAPL")).toBe(true);
    expect(isUSStock("GOOGL")).toBe(true);
    expect(isUSStock("A")).toBe(true);
  });

  it("rejects non-US stocks", () => {
    expect(isUSStock("2330.TW")).toBe(false);
    expect(isUSStock("TOOLONG")).toBe(false);
  });
});

describe("normalizeStockSymbol", () => {
  it("normalizes stock symbols", () => {
    expect(normalizeStockSymbol(" aapl ")).toBe("AAPL");
    expect(normalizeStockSymbol("2330.tw")).toBe("2330.TW");
  });
});

describe("isValidDateString", () => {
  it("validates correct date strings", () => {
    expect(isValidDateString("2024-01-15")).toBe(true);
    expect(isValidDateString("2024-12-31")).toBe(true);
  });

  it("rejects invalid date strings", () => {
    expect(isValidDateString("2024-1-15")).toBe(false);
    expect(isValidDateString("invalid")).toBe(false);
    expect(isValidDateString("2024-13-01")).toBe(false);
  });
});

describe("isValidDateRange", () => {
  it("validates correct date ranges", () => {
    expect(isValidDateRange("2024-01-01", "2024-12-31")).toBe(true);
  });

  it("rejects invalid ranges", () => {
    expect(isValidDateRange("2024-12-31", "2024-01-01")).toBe(false);
    expect(isValidDateRange("2024-01-01", "2024-01-01")).toBe(false);
    expect(isValidDateRange("invalid", "2024-12-31")).toBe(false);
  });
});

describe("isNotFutureDate", () => {
  it("accepts past dates", () => {
    expect(isNotFutureDate("2020-01-01")).toBe(true);
  });

  it("rejects future dates", () => {
    expect(isNotFutureDate("2099-12-31")).toBe(false);
  });

  it("rejects invalid dates", () => {
    expect(isNotFutureDate("invalid")).toBe(false);
  });
});

describe("isValidAmount", () => {
  it("validates correct amounts", () => {
    expect(isValidAmount(10000)).toBe(true);
    expect(isValidAmount(1000)).toBe(true);
  });

  it("rejects invalid amounts", () => {
    expect(isValidAmount(500)).toBe(false);
    expect(isValidAmount(-1000)).toBe(false);
    expect(isValidAmount(NaN)).toBe(false);
    expect(isValidAmount(Infinity)).toBe(false);
    expect(isValidAmount(1000000000000)).toBe(false);
  });
});

describe("isValidAmountStep", () => {
  it("validates amounts that are multiples of 100", () => {
    expect(isValidAmountStep(10000)).toBe(true);
    expect(isValidAmountStep(1000)).toBe(true);
  });

  it("rejects amounts that are not multiples of 100", () => {
    expect(isValidAmountStep(10050)).toBe(false);
    expect(isValidAmountStep(999)).toBe(false);
  });
});

describe("isValidStockList", () => {
  it("validates correct stock lists", () => {
    expect(isValidStockList(["AAPL", "GOOGL"])).toBe(true);
    expect(isValidStockList(["AAPL"])).toBe(true);
  });

  it("rejects invalid lists", () => {
    expect(isValidStockList([])).toBe(false);
    expect(isValidStockList(["AAPL", "", "GOOGL"])).toBe(false);
    expect(isValidStockList(Array(11).fill("AAPL"))).toBe(false);
    expect(isValidStockList("not an array" as any)).toBe(false);
  });
});

describe("removeDuplicateStocks", () => {
  it("removes duplicates", () => {
    const result = removeDuplicateStocks(["AAPL", "GOOGL", "AAPL"]);
    expect(result).toEqual(["AAPL", "GOOGL"]);
  });

  it("normalizes symbols", () => {
    const result = removeDuplicateStocks(["aapl", "AAPL", " AAPL "]);
    expect(result).toEqual(["AAPL"]);
  });
});

describe("getStockSymbolError", () => {
  it("returns empty string for valid symbols", () => {
    expect(getStockSymbolError("AAPL")).toBe("");
  });

  it("returns error for empty symbols", () => {
    expect(getStockSymbolError("")).toContain("不能為空");
  });

  it("returns error for invalid format", () => {
    expect(getStockSymbolError("aapl")).toContain("格式錯誤");
  });
});

describe("getDateRangeError", () => {
  it("returns empty string for valid range", () => {
    expect(getDateRangeError("2024-01-01", "2024-12-31")).toBe("");
  });

  it("returns error for invalid start date", () => {
    expect(getDateRangeError("invalid", "2024-12-31")).toContain("開始日期");
  });

  it("returns error for invalid end date", () => {
    expect(getDateRangeError("2024-01-01", "invalid")).toContain("結束日期");
  });

  it("returns error for reversed dates", () => {
    expect(getDateRangeError("2024-12-31", "2024-01-01")).toContain("晚於");
  });

  it("returns error for future end date", () => {
    expect(getDateRangeError("2024-01-01", "2099-12-31")).toContain("未來");
  });
});

describe("getAmountError", () => {
  it("returns empty string for valid amounts", () => {
    expect(getAmountError(10000)).toBe("");
  });

  it("returns error for NaN", () => {
    expect(getAmountError(NaN)).toContain("有效");
  });

  it("returns error for too small amount", () => {
    expect(getAmountError(500)).toContain("最少");
  });

  it("returns error for too large amount", () => {
    expect(getAmountError(1000000000000)).toContain("最多");
  });

  it("returns error for invalid step", () => {
    expect(getAmountError(10050)).toContain("倍數");
  });
});
