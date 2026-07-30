import { describe, it, expect } from "vitest";
import { cn } from "./cn";

describe("cn", () => {
  it("should merge class names", () => {
    expect(cn("foo", "bar")).toBe("foo bar");
  });

  it("should handle conditional classes", () => {
    expect(cn("base", undefined, "visible")).toBe("base visible");
    expect(cn("base", "", "visible")).toBe("base visible");
  });

  it("should handle undefined values", () => {
    expect(cn("foo", undefined, "bar")).toBe("foo bar");
  });

  it("should handle empty inputs", () => {
    expect(cn()).toBe("");
  });
});
