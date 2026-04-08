import { describe, it, expect } from "vitest";
import { lifecycle, STALE_UPVOTE_THRESHOLD } from "../issue-lifecycle.ts";

describe("issue-lifecycle", () => {
  describe("lifecycle array", () => {
    it("contains all expected labels", () => {
      const labels = lifecycle.map((l) => l.label);
      expect(labels).toContain("invalid");
      expect(labels).toContain("needs-repro");
      expect(labels).toContain("needs-info");
      expect(labels).toContain("stale");
      expect(labels).toContain("autoclose");
    });

    it("every entry has a positive days value", () => {
      for (const entry of lifecycle) {
        expect(entry.days).toBeGreaterThan(0);
      }
    });

    it("every entry has a non-empty reason", () => {
      for (const entry of lifecycle) {
        expect(entry.reason.length).toBeGreaterThan(0);
      }
    });

    it("every entry has a non-empty nudge message", () => {
      for (const entry of lifecycle) {
        expect(entry.nudge.length).toBeGreaterThan(0);
      }
    });

    it("invalid label closes faster than stale", () => {
      const invalid = lifecycle.find((l) => l.label === "invalid")!;
      const stale = lifecycle.find((l) => l.label === "stale")!;
      expect(invalid.days).toBeLessThan(stale.days);
    });

    it("needs-repro and needs-info have equal timeouts", () => {
      const repro = lifecycle.find((l) => l.label === "needs-repro")!;
      const info = lifecycle.find((l) => l.label === "needs-info")!;
      expect(repro.days).toEqual(info.days);
    });
  });

  describe("STALE_UPVOTE_THRESHOLD", () => {
    it("is a positive integer", () => {
      expect(STALE_UPVOTE_THRESHOLD).toBeGreaterThan(0);
      expect(Number.isInteger(STALE_UPVOTE_THRESHOLD)).toBe(true);
    });

    it("is set to 10", () => {
      expect(STALE_UPVOTE_THRESHOLD).toBe(10);
    });
  });
});
