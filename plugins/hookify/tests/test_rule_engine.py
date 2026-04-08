"""Tests for hookify rule_engine module."""

import os
import sys
import pytest
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from hookify.core.config_loader import Condition, Rule
from hookify.core.rule_engine import RuleEngine, compile_regex


def make_rule(
    name="test-rule",
    conditions=None,
    action="warn",
    tool_matcher=None,
    enabled=True,
    message="Test message",
    event="bash",
):
    return Rule(
        name=name,
        enabled=enabled,
        event=event,
        conditions=conditions or [],
        action=action,
        tool_matcher=tool_matcher,
        message=message,
    )


def bash_input(command="ls"):
    return {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": command}}


def write_input(file_path="file.py", content="hello"):
    return {"hook_event_name": "PreToolUse", "tool_name": "Write", "tool_input": {"file_path": file_path, "content": content}}


def edit_input(file_path="file.py", new_string="new", old_string="old"):
    return {
        "hook_event_name": "PreToolUse",
        "tool_name": "Edit",
        "tool_input": {"file_path": file_path, "new_string": new_string, "old_string": old_string},
    }


def multiedit_input(file_path="file.py", edits=None):
    return {
        "hook_event_name": "PreToolUse",
        "tool_name": "MultiEdit",
        "tool_input": {"file_path": file_path, "edits": edits or []},
    }


# ---------------------------------------------------------------------------
# compile_regex (LRU cache)
# ---------------------------------------------------------------------------

class TestCompileRegex:
    def test_basic_pattern(self):
        r = compile_regex(r"rm\s+-rf")
        assert r.search("rm -rf /")

    def test_case_insensitive(self):
        r = compile_regex("HELLO")
        assert r.search("hello world")

    def test_cache_returns_same_object(self):
        r1 = compile_regex("foo")
        r2 = compile_regex("foo")
        assert r1 is r2


# ---------------------------------------------------------------------------
# RuleEngine._matches_tool
# ---------------------------------------------------------------------------

class TestMatchesTool:
    engine = RuleEngine()

    def test_wildcard_matches_anything(self):
        assert self.engine._matches_tool("*", "Bash")
        assert self.engine._matches_tool("*", "Write")

    def test_exact_match(self):
        assert self.engine._matches_tool("Bash", "Bash")
        assert not self.engine._matches_tool("Bash", "Write")

    def test_pipe_or_match(self):
        assert self.engine._matches_tool("Edit|Write", "Edit")
        assert self.engine._matches_tool("Edit|Write", "Write")
        assert not self.engine._matches_tool("Edit|Write", "Bash")


# ---------------------------------------------------------------------------
# RuleEngine._extract_field
# ---------------------------------------------------------------------------

class TestExtractField:
    engine = RuleEngine()

    def test_bash_command(self):
        val = self.engine._extract_field("command", "Bash", {"command": "ls -la"})
        assert val == "ls -la"

    def test_write_content(self):
        val = self.engine._extract_field("content", "Write", {"content": "print('hi')"})
        assert val == "print('hi')"

    def test_edit_new_string(self):
        val = self.engine._extract_field("new_string", "Edit", {"new_string": "new value"})
        assert val == "new value"

    def test_edit_new_text_alias(self):
        val = self.engine._extract_field("new_text", "Edit", {"new_string": "aliased"})
        assert val == "aliased"

    def test_edit_old_string(self):
        val = self.engine._extract_field("old_string", "Edit", {"old_string": "old value"})
        assert val == "old value"

    def test_edit_content_falls_back_to_new_string(self):
        val = self.engine._extract_field("content", "Edit", {"new_string": "via new_string"})
        assert val == "via new_string"

    def test_edit_content_prefers_content_key(self):
        val = self.engine._extract_field("content", "Edit", {"content": "direct", "new_string": "ignored"})
        assert val == "direct"

    def test_file_path_write(self):
        val = self.engine._extract_field("file_path", "Write", {"file_path": "/src/foo.py"})
        assert val == "/src/foo.py"

    def test_file_path_multiedit(self):
        val = self.engine._extract_field("file_path", "MultiEdit", {"file_path": "/src/bar.py"})
        assert val == "/src/bar.py"

    def test_multiedit_new_text_concatenates_edits(self):
        edits = [{"new_string": "part1"}, {"new_string": "part2"}]
        val = self.engine._extract_field("new_text", "MultiEdit", {"edits": edits})
        assert "part1" in val
        assert "part2" in val

    def test_direct_tool_input_field(self):
        val = self.engine._extract_field("custom_field", "Bash", {"custom_field": "value"})
        assert val == "value"

    def test_unknown_field_returns_none(self):
        val = self.engine._extract_field("nonexistent", "Bash", {"command": "ls"})
        assert val is None

    def test_reason_from_input_data(self):
        val = self.engine._extract_field("reason", "Bash", {}, input_data={"reason": "done"})
        assert val == "done"

    def test_user_prompt_from_input_data(self):
        val = self.engine._extract_field("user_prompt", "", {}, input_data={"user_prompt": "hello"})
        assert val == "hello"

    def test_transcript_reads_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("transcript content")
            path = f.name
        try:
            val = self.engine._extract_field("transcript", "", {}, input_data={"transcript_path": path})
            assert val == "transcript content"
        finally:
            os.unlink(path)

    def test_transcript_missing_file_returns_empty(self):
        val = self.engine._extract_field("transcript", "", {}, input_data={"transcript_path": "/nonexistent/path"})
        assert val == ""

    def test_non_string_value_converted(self):
        val = self.engine._extract_field("count", "Bash", {"count": 42})
        assert val == "42"


# ---------------------------------------------------------------------------
# RuleEngine._check_condition  (all operators)
# ---------------------------------------------------------------------------

class TestCheckCondition:
    engine = RuleEngine()

    def _cond(self, field, operator, pattern):
        return Condition(field=field, operator=operator, pattern=pattern)

    def test_regex_match_hit(self):
        c = self._cond("command", "regex_match", r"rm\s+-rf")
        assert self.engine._check_condition(c, "Bash", {"command": "rm -rf /"})

    def test_regex_match_miss(self):
        c = self._cond("command", "regex_match", r"rm\s+-rf")
        assert not self.engine._check_condition(c, "Bash", {"command": "ls"})

    def test_regex_match_invalid_pattern(self, capsys):
        c = self._cond("command", "regex_match", r"[invalid")
        result = self.engine._check_condition(c, "Bash", {"command": "anything"})
        assert result is False

    def test_contains_hit(self):
        c = self._cond("command", "contains", "sudo")
        assert self.engine._check_condition(c, "Bash", {"command": "sudo apt-get"})

    def test_contains_miss(self):
        c = self._cond("command", "contains", "sudo")
        assert not self.engine._check_condition(c, "Bash", {"command": "ls"})

    def test_equals_hit(self):
        c = self._cond("command", "equals", "ls")
        assert self.engine._check_condition(c, "Bash", {"command": "ls"})

    def test_equals_miss(self):
        c = self._cond("command", "equals", "ls")
        assert not self.engine._check_condition(c, "Bash", {"command": "ls -la"})

    def test_not_contains_hit(self):
        c = self._cond("command", "not_contains", "sudo")
        assert self.engine._check_condition(c, "Bash", {"command": "ls"})

    def test_not_contains_miss(self):
        c = self._cond("command", "not_contains", "sudo")
        assert not self.engine._check_condition(c, "Bash", {"command": "sudo ls"})

    def test_starts_with_hit(self):
        c = self._cond("command", "starts_with", "git ")
        assert self.engine._check_condition(c, "Bash", {"command": "git push"})

    def test_starts_with_miss(self):
        c = self._cond("command", "starts_with", "git ")
        assert not self.engine._check_condition(c, "Bash", {"command": "ls"})

    def test_ends_with_hit(self):
        c = self._cond("file_path", "ends_with", ".py")
        assert self.engine._check_condition(c, "Write", {"file_path": "script.py"})

    def test_ends_with_miss(self):
        c = self._cond("file_path", "ends_with", ".py")
        assert not self.engine._check_condition(c, "Write", {"file_path": "script.ts"})

    def test_unknown_operator_returns_false(self):
        c = self._cond("command", "unknown_op", "foo")
        assert not self.engine._check_condition(c, "Bash", {"command": "foo"})

    def test_none_field_value_returns_false(self):
        c = self._cond("nonexistent_field", "contains", "x")
        assert not self.engine._check_condition(c, "Bash", {"command": "ls"})


# ---------------------------------------------------------------------------
# RuleEngine.evaluate_rules
# ---------------------------------------------------------------------------

class TestEvaluateRules:
    engine = RuleEngine()

    def _warn_rule(self, field="command", pattern="rm", tool_matcher=None):
        return make_rule(
            conditions=[Condition(field=field, operator="contains", pattern=pattern)],
            action="warn",
            tool_matcher=tool_matcher,
        )

    def _block_rule(self, field="command", pattern="rm"):
        return make_rule(
            name="block-rule",
            conditions=[Condition(field=field, operator="contains", pattern=pattern)],
            action="block",
        )

    def test_no_rules_returns_empty(self):
        assert self.engine.evaluate_rules([], bash_input("ls")) == {}

    def test_no_match_returns_empty(self):
        rule = self._warn_rule(pattern="sudo")
        assert self.engine.evaluate_rules([rule], bash_input("ls")) == {}

    def test_warn_match_returns_system_message(self):
        rule = self._warn_rule(pattern="rm")
        result = self.engine.evaluate_rules([rule], bash_input("rm -rf /"))
        assert "systemMessage" in result
        assert "hookSpecificOutput" not in result

    def test_warn_message_includes_rule_name(self):
        result = self.engine.evaluate_rules([self._warn_rule()], bash_input("rm foo"))
        assert "test-rule" in result["systemMessage"]

    def test_block_pretooluse_returns_deny(self):
        rule = self._block_rule()
        result = self.engine.evaluate_rules([rule], bash_input("rm -rf /"))
        assert result["hookSpecificOutput"]["permissionDecision"] == "deny"
        assert result["hookSpecificOutput"]["hookEventName"] == "PreToolUse"

    def test_block_stop_event_returns_decision_block(self):
        rule = make_rule(
            conditions=[Condition(field="reason", operator="contains", pattern="bad")],
            action="block",
        )
        input_data = {"hook_event_name": "Stop", "tool_name": "", "tool_input": {}, "reason": "bad reason"}
        result = self.engine.evaluate_rules([rule], input_data)
        assert result["decision"] == "block"
        assert "reason" in result

    def test_block_other_event_returns_only_system_message(self):
        rule = make_rule(
            conditions=[Condition(field="user_prompt", operator="contains", pattern="bad")],
            action="block",
        )
        input_data = {"hook_event_name": "UserPromptSubmit", "tool_name": "", "tool_input": {}, "user_prompt": "bad prompt"}
        result = self.engine.evaluate_rules([rule], input_data)
        assert "systemMessage" in result
        assert "hookSpecificOutput" not in result
        assert "decision" not in result

    def test_block_takes_priority_over_warn(self):
        warn_rule = self._warn_rule(pattern="rm")
        block_rule = self._block_rule(pattern="rm")
        result = self.engine.evaluate_rules([warn_rule, block_rule], bash_input("rm foo"))
        # Should have hookSpecificOutput (block), not just systemMessage (warn)
        assert "hookSpecificOutput" in result
        assert result["hookSpecificOutput"]["permissionDecision"] == "deny"

    def test_multiple_warn_rules_messages_combined(self):
        rule1 = make_rule(name="rule1", conditions=[Condition(field="command", operator="contains", pattern="rm")], message="msg1")
        rule2 = make_rule(name="rule2", conditions=[Condition(field="command", operator="contains", pattern="rm")], message="msg2")
        result = self.engine.evaluate_rules([rule1, rule2], bash_input("rm foo"))
        assert "msg1" in result["systemMessage"]
        assert "msg2" in result["systemMessage"]

    def test_rule_no_conditions_does_not_match(self):
        rule = make_rule(conditions=[])
        assert self.engine.evaluate_rules([rule], bash_input("anything")) == {}

    def test_tool_matcher_filters_tool(self):
        rule = self._warn_rule(pattern="rm", tool_matcher="Write")
        # Bash input should not match a Write-only rule
        assert self.engine.evaluate_rules([rule], bash_input("rm foo")) == {}

    def test_tool_matcher_wildcard_matches_any_tool(self):
        rule = self._warn_rule(pattern="rm", tool_matcher="*")
        assert self.engine.evaluate_rules([rule], bash_input("rm foo")) != {}

    def test_all_conditions_must_match(self):
        rule = make_rule(conditions=[
            Condition(field="command", operator="contains", pattern="rm"),
            Condition(field="command", operator="contains", pattern="-rf"),
        ])
        # Only first condition matches
        assert self.engine.evaluate_rules([rule], bash_input("rm foo")) == {}
        # Both conditions match
        assert self.engine.evaluate_rules([rule], bash_input("rm -rf /")) != {}
