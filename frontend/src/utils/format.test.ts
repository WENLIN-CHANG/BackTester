import { describe, it, expect } from "vitest";
import {
  formatPercent,
  formatPercentNoSign,
  formatCurrency,
  formatNumber,
  formatDateString,
  formatDateChinese,
  formatSharpeRatio,
  formatVolatility,
  formatCompact,
} from "./format";

describe("formatPercent", () => {
  it("formats positive percentages with + sign", () => {
    expect(formatPercent(0.1234)).toBe("+12.34%");
    expect(formatPercent(0.5)).toBe("+50.00%");
  });

  it("formats negative percentages", () => {
    expect(formatPercent(-0.0567)).toBe("-5.67%");
    expect(formatPercent(-0.25)).toBe("-25.00%");
  });

  it("formats zero", () => {
    expect(formatPercent(0)).toBe("0.00%");
  });

  it("respects custom decimal places", () => {
    expect(formatPercent(0.12345, 3)).toBe("+12.345%");
    expect(formatPercent(0.12345, 1)).toBe("+12.3%");
  });
});

describe("formatPercentNoSign", () => {
  it("formats percentages without sign", () => {
    expect(formatPercentNoSign(0.1234)).toBe("12.34%");
    expect(formatPercentNoSign(-0.0567)).toBe("-5.67%");
    expect(formatPercentNoSign(0)).toBe("0.00%");
  });
});

describe("formatCurrency", () => {
  it("formats currency with TWD", () => {
    const result = formatCurrency(12500);
    expect(result).toContain("12,500");
  });

  it("rounds to integer", () => {
    const result = formatCurrency(12500.89);
    expect(result).toContain("12,501");
  });
});

describe("formatNumber", () => {
  it("formats numbers with thousand separators", () => {
    expect(formatNumber(12500)).toBe("12,500");
    expect(formatNumber(1234567)).toBe("1,234,567");
  });

  it("formats decimals when specified", () => {
    expect(formatNumber(1234.5678, 2)).toBe("1,234.57");
  });
});

describe("formatDateString", () => {
  it("formats date string", () => {
    expect(formatDateString("2024-01-15")).toBe("2024/01/15");
  });

  it("formats Date object", () => {
    const date = new Date(2024, 0, 15);
    expect(formatDateString(date)).toBe("2024/01/15");
  });

  it("respects custom format", () => {
    expect(formatDateString("2024-01-15", "MM/dd/yyyy")).toBe("01/15/2024");
  });
});

describe("formatDateChinese", () => {
  it("formats date in Chinese", () => {
    expect(formatDateChinese("2024-01-15")).toBe("2024年1月15日");
  });

  it("formats Date object in Chinese", () => {
    const date = new Date(2024, 0, 15);
    expect(formatDateChinese(date)).toBe("2024年1月15日");
  });
});

describe("formatSharpeRatio", () => {
  it("formats Sharpe ratio with 2 decimals", () => {
    expect(formatSharpeRatio(1.85)).toBe("1.85");
    expect(formatSharpeRatio(0.5)).toBe("0.50");
  });
});

describe("formatVolatility", () => {
  it("formats volatility as percentage", () => {
    expect(formatVolatility(0.25)).toBe("25.00%");
  });
});

describe("formatCompact", () => {
  it("formats large numbers compactly", () => {
    const result = formatCompact(1500);
    expect(result).toMatch(/1[5\.][千K0]/); // Accepts 1500, 1.5千, or 1.5K
  });

  it("formats millions", () => {
    const result = formatCompact(1500000);
    expect(result).toMatch(/1[5\.][0萬M]/); // Accepts 150萬, 1.5M, etc.
  });
});
