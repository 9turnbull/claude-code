/**
 * Tests for the pure logic in auto-close-duplicates.ts.
 *
 * Because the script uses a top-level async IIFE and process.env at load
 * time, we re-implement (and test) the two pure functions directly here
 * rather than importing the whole script.
 */
import { describe, it, expect } from "vitest";

// ---------------------------------------------------------------------------
// Copy of extractDuplicateIssueNumber (pure function from the script)
// ---------------------------------------------------------------------------

function extractDuplicateIssueNumber(commentBody: string): number | null {
  let match = commentBody.match(/#(\d+)/);
  if (match) return parseInt(match[1], 10);

  match = commentBody.match(/github\.com\/[^/]+\/[^/]+\/issues\/(\d+)/);
  if (match) return parseInt(match[1], 10);

  return null;
}

// ---------------------------------------------------------------------------
// Copy of duplicate-comment filter predicate (from autoCloseDuplicates loop)
// ---------------------------------------------------------------------------

interface Comment {
  id: number;
  body: string;
  created_at: string;
  user: { type: string; id: number };
}

function isDuplicateDetectionComment(comment: Comment): boolean {
  return (
    comment.body.includes("Found") &&
    comment.body.includes("possible duplicate") &&
    comment.user.type === "Bot"
  );
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe("extractDuplicateIssueNumber", () => {
  it("extracts #NNN shorthand", () => {
    expect(extractDuplicateIssueNumber("This is a duplicate of #123")).toBe(123);
  });

  it("extracts the first #NNN when multiple present", () => {
    expect(extractDuplicateIssueNumber("#42 and also #99")).toBe(42);
  });

  it("extracts from full GitHub issue URL", () => {
    expect(
      extractDuplicateIssueNumber(
        "See https://github.com/anthropics/claude-code/issues/456"
      )
    ).toBe(456);
  });

  it("prefers #NNN over URL when both present", () => {
    // #NNN match comes first in the function
    expect(
      extractDuplicateIssueNumber(
        "#7 also see https://github.com/anthropics/claude-code/issues/8"
      )
    ).toBe(7);
  });

  it("returns null when no issue number found", () => {
    expect(extractDuplicateIssueNumber("No issue reference here")).toBeNull();
  });

  it("returns null for empty string", () => {
    expect(extractDuplicateIssueNumber("")).toBeNull();
  });

  it("handles large issue numbers", () => {
    expect(extractDuplicateIssueNumber("#99999")).toBe(99999);
  });

  it("parses URL with any owner/repo", () => {
    expect(
      extractDuplicateIssueNumber(
        "https://github.com/owner/my-repo/issues/321"
      )
    ).toBe(321);
  });
});

describe("isDuplicateDetectionComment", () => {
  const botComment = (body: string): Comment => ({
    id: 1,
    body,
    created_at: new Date().toISOString(),
    user: { type: "Bot", id: 99 },
  });

  const humanComment = (body: string): Comment => ({
    id: 2,
    body,
    created_at: new Date().toISOString(),
    user: { type: "User", id: 42 },
  });

  it("matches a bot comment with correct phrasing", () => {
    expect(
      isDuplicateDetectionComment(
        botComment("Found 1 possible duplicate of this issue.")
      )
    ).toBe(true);
  });

  it("rejects a human comment even with correct phrasing", () => {
    expect(
      isDuplicateDetectionComment(
        humanComment("Found 1 possible duplicate of this issue.")
      )
    ).toBe(false);
  });

  it("rejects a bot comment missing 'Found'", () => {
    expect(
      isDuplicateDetectionComment(botComment("This is a possible duplicate."))
    ).toBe(false);
  });

  it("rejects a bot comment missing 'possible duplicate'", () => {
    expect(
      isDuplicateDetectionComment(botComment("Found something interesting."))
    ).toBe(false);
  });

  it("rejects an empty bot comment", () => {
    expect(isDuplicateDetectionComment(botComment(""))).toBe(false);
  });
});

describe("date threshold logic", () => {
  it("issue created more than 3 days ago passes filter", () => {
    const threeDaysAgo = new Date();
    threeDaysAgo.setDate(threeDaysAgo.getDate() - 3);

    const fourDaysAgo = new Date();
    fourDaysAgo.setDate(fourDaysAgo.getDate() - 4);

    expect(new Date(fourDaysAgo.toISOString()) <= threeDaysAgo).toBe(true);
  });

  it("issue created less than 3 days ago fails filter", () => {
    const threeDaysAgo = new Date();
    threeDaysAgo.setDate(threeDaysAgo.getDate() - 3);

    const twoDaysAgo = new Date();
    twoDaysAgo.setDate(twoDaysAgo.getDate() - 2);

    expect(new Date(twoDaysAgo.toISOString()) <= threeDaysAgo).toBe(false);
  });

  it("duplicate comment older than 3 days passes the age check", () => {
    const threeDaysAgo = new Date();
    threeDaysAgo.setDate(threeDaysAgo.getDate() - 3);

    const commentDate = new Date();
    commentDate.setDate(commentDate.getDate() - 5);

    // The script checks: dupeCommentDate > threeDaysAgo → skip
    // So we want dupeCommentDate <= threeDaysAgo to proceed
    expect(commentDate > threeDaysAgo).toBe(false);
  });

  it("duplicate comment newer than 3 days is skipped", () => {
    const threeDaysAgo = new Date();
    threeDaysAgo.setDate(threeDaysAgo.getDate() - 3);

    const commentDate = new Date();
    commentDate.setDate(commentDate.getDate() - 1);

    expect(commentDate > threeDaysAgo).toBe(true);
  });
});
