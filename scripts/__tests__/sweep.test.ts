/**
 * Tests for pure logic extracted from sweep.ts.
 *
 * sweep.ts executes top-level await and reads env vars at import time,
 * so we test the independently verifiable logic here.
 */
import { describe, it, expect } from "vitest";
import { lifecycle, STALE_UPVOTE_THRESHOLD } from "../issue-lifecycle.ts";

// ---------------------------------------------------------------------------
// Re-implementations of pure helpers (mirror what the script does)
// ---------------------------------------------------------------------------

function isStaleCandidate(issue: {
  pull_request?: unknown;
  locked?: boolean;
  assignees?: unknown[];
  updated_at: string;
  labels?: { name: string }[];
  reactions?: { "+1": number };
}, cutoff: Date): boolean {
  if (issue.pull_request) return false;
  if (issue.locked) return false;
  if ((issue.assignees ?? []).length > 0) return false;

  const updatedAt = new Date(issue.updated_at);
  if (updatedAt > cutoff) return false;

  const alreadyStale = (issue.labels ?? []).some(
    (l) => l.name === "stale" || l.name === "autoclose"
  );
  if (alreadyStale) return false;

  const thumbsUp = issue.reactions?.["+1"] ?? 0;
  if (thumbsUp >= STALE_UPVOTE_THRESHOLD) return false;

  return true;
}

function isExpiredCandidate(issue: {
  pull_request?: unknown;
  locked?: boolean;
  reactions?: { "+1": number };
}): boolean {
  if (issue.pull_request) return false;
  if (issue.locked) return false;
  const thumbsUp = issue.reactions?.["+1"] ?? 0;
  if (thumbsUp >= STALE_UPVOTE_THRESHOLD) return false;
  return true;
}

function hasHumanCommentAfter(
  comments: { user: { type: string }; created_at: string }[],
  since: Date
): boolean {
  return comments.some(
    (c) => c.user.type !== "Bot" && new Date(c.created_at) > since
  );
}

function cutoffDate(daysAgo: number): Date {
  const d = new Date();
  d.setDate(d.getDate() - daysAgo);
  return d;
}

// ---------------------------------------------------------------------------
// isStaleCandidate
// ---------------------------------------------------------------------------

describe("isStaleCandidate", () => {
  const staleCutoff = cutoffDate(
    lifecycle.find((l) => l.label === "stale")!.days
  );

  const oldDate = new Date();
  oldDate.setDate(oldDate.getDate() - 20); // 20 days ago = stale

  const recentDate = new Date();
  recentDate.setDate(recentDate.getDate() - 1); // 1 day ago = not stale

  it("marks an old inactive issue as stale candidate", () => {
    expect(
      isStaleCandidate({ updated_at: oldDate.toISOString() }, staleCutoff)
    ).toBe(true);
  });

  it("skips a recently updated issue", () => {
    expect(
      isStaleCandidate({ updated_at: recentDate.toISOString() }, staleCutoff)
    ).toBe(false);
  });

  it("skips pull requests", () => {
    expect(
      isStaleCandidate(
        { updated_at: oldDate.toISOString(), pull_request: {} },
        staleCutoff
      )
    ).toBe(false);
  });

  it("skips locked issues", () => {
    expect(
      isStaleCandidate(
        { updated_at: oldDate.toISOString(), locked: true },
        staleCutoff
      )
    ).toBe(false);
  });

  it("skips assigned issues", () => {
    expect(
      isStaleCandidate(
        { updated_at: oldDate.toISOString(), assignees: [{ login: "dev" }] },
        staleCutoff
      )
    ).toBe(false);
  });

  it("skips issues already labeled stale", () => {
    expect(
      isStaleCandidate(
        { updated_at: oldDate.toISOString(), labels: [{ name: "stale" }] },
        staleCutoff
      )
    ).toBe(false);
  });

  it("skips issues already labeled autoclose", () => {
    expect(
      isStaleCandidate(
        { updated_at: oldDate.toISOString(), labels: [{ name: "autoclose" }] },
        staleCutoff
      )
    ).toBe(false);
  });

  it("skips issues with 10+ upvotes", () => {
    expect(
      isStaleCandidate(
        { updated_at: oldDate.toISOString(), reactions: { "+1": 10 } },
        staleCutoff
      )
    ).toBe(false);
  });

  it("does NOT skip issues with 9 upvotes (below threshold)", () => {
    expect(
      isStaleCandidate(
        { updated_at: oldDate.toISOString(), reactions: { "+1": 9 } },
        staleCutoff
      )
    ).toBe(true);
  });

  it("treats missing reactions as zero upvotes", () => {
    expect(
      isStaleCandidate({ updated_at: oldDate.toISOString() }, staleCutoff)
    ).toBe(true);
  });
});

// ---------------------------------------------------------------------------
// isExpiredCandidate
// ---------------------------------------------------------------------------

describe("isExpiredCandidate", () => {
  it("approves a plain open issue for expiry", () => {
    expect(isExpiredCandidate({})).toBe(true);
  });

  it("skips PRs", () => {
    expect(isExpiredCandidate({ pull_request: {} })).toBe(false);
  });

  it("skips locked issues", () => {
    expect(isExpiredCandidate({ locked: true })).toBe(false);
  });

  it("skips issues with 10+ upvotes", () => {
    expect(isExpiredCandidate({ reactions: { "+1": 10 } })).toBe(false);
  });

  it("allows issues with 9 upvotes", () => {
    expect(isExpiredCandidate({ reactions: { "+1": 9 } })).toBe(true);
  });
});

// ---------------------------------------------------------------------------
// hasHumanCommentAfter
// ---------------------------------------------------------------------------

describe("hasHumanCommentAfter", () => {
  const labeledAt = new Date("2024-01-10T00:00:00Z");

  it("detects a human comment after the cutoff", () => {
    const comments = [
      { user: { type: "User" }, created_at: "2024-01-11T00:00:00Z" },
    ];
    expect(hasHumanCommentAfter(comments, labeledAt)).toBe(true);
  });

  it("ignores a bot comment after the cutoff", () => {
    const comments = [
      { user: { type: "Bot" }, created_at: "2024-01-11T00:00:00Z" },
    ];
    expect(hasHumanCommentAfter(comments, labeledAt)).toBe(false);
  });

  it("ignores a human comment before the cutoff", () => {
    const comments = [
      { user: { type: "User" }, created_at: "2024-01-09T00:00:00Z" },
    ];
    expect(hasHumanCommentAfter(comments, labeledAt)).toBe(false);
  });

  it("returns false for empty comment list", () => {
    expect(hasHumanCommentAfter([], labeledAt)).toBe(false);
  });

  it("returns true if any comment is human even among bots", () => {
    const comments = [
      { user: { type: "Bot" }, created_at: "2024-01-11T00:00:00Z" },
      { user: { type: "User" }, created_at: "2024-01-12T00:00:00Z" },
    ];
    expect(hasHumanCommentAfter(comments, labeledAt)).toBe(true);
  });
});

// ---------------------------------------------------------------------------
// CLOSE_MESSAGE format
// ---------------------------------------------------------------------------

describe("CLOSE_MESSAGE", () => {
  const NEW_ISSUE =
    "https://github.com/anthropics/claude-code/issues/new/choose";

  const CLOSE_MESSAGE = (reason: string) =>
    `Closing for now — ${reason}. Please [open a new issue](${NEW_ISSUE}) if this is still relevant.`;

  it("includes the reason", () => {
    const msg = CLOSE_MESSAGE("inactive for too long");
    expect(msg).toContain("inactive for too long");
  });

  it("includes a link to open a new issue", () => {
    const msg = CLOSE_MESSAGE("any reason");
    expect(msg).toContain(NEW_ISSUE);
  });
});
