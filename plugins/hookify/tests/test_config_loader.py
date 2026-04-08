"""Tests for hookify config_loader module."""

import pytest
import os
import tempfile

import sys
# Add plugins/ to path so `hookify` is importable as a top-level package
# (matching the import style used inside the package itself)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from hookify.core.config_loader import (
    Condition,
    Rule,
    extract_frontmatter,
    load_rule_file,
)


# ---------------------------------------------------------------------------
# extract_frontmatter
# ---------------------------------------------------------------------------

class TestExtractFrontmatter:
    def test_simple_key_value(self):
        content = "---\nname: my-rule\nenabled: true\n---\nMessage body"
        fm, msg = extract_frontmatter(content)
        assert fm["name"] == "my-rule"
        assert fm["enabled"] is True
        assert msg == "Message body"

    def test_boolean_false(self):
        content = "---\nenabled: false\n---\nbody"
        fm, _ = extract_frontmatter(content)
        assert fm["enabled"] is False

    def test_quoted_value(self):
        content = '---\nname: "quoted-name"\n---\nbody'
        fm, _ = extract_frontmatter(content)
        assert fm["name"] == "quoted-name"

    def test_single_quoted_value(self):
        content = "---\nname: 'single-quoted'\n---\nbody"
        fm, _ = extract_frontmatter(content)
        assert fm["name"] == "single-quoted"

    def test_missing_frontmatter_returns_empty(self):
        content = "No frontmatter here"
        fm, msg = extract_frontmatter(content)
        assert fm == {}
        assert msg == "No frontmatter here"

    def test_incomplete_frontmatter_returns_empty(self):
        content = "---\nname: foo"
        fm, _ = extract_frontmatter(content)
        assert fm == {}

    def test_message_body_stripped(self):
        content = "---\nname: r\n---\n\n  hello  \n"
        _, msg = extract_frontmatter(content)
        assert msg == "hello"

    def test_simple_list(self):
        content = "---\ntags:\n- bug\n- feature\n---\nbody"
        fm, _ = extract_frontmatter(content)
        assert fm["tags"] == ["bug", "feature"]

    def test_conditions_list_multiline(self):
        content = (
            "---\n"
            "conditions:\n"
            "- field: command\n"
            "  operator: regex_match\n"
            "  pattern: 'rm -rf'\n"
            "---\n"
            "Dangerous!"
        )
        fm, msg = extract_frontmatter(content)
        assert isinstance(fm["conditions"], list)
        assert len(fm["conditions"]) == 1
        cond = fm["conditions"][0]
        assert cond["field"] == "command"
        assert cond["operator"] == "regex_match"
        assert cond["pattern"] == "rm -rf"
        assert msg == "Dangerous!"

    def test_conditions_list_inline_comma(self):
        content = (
            "---\n"
            "conditions:\n"
            "- field: command, operator: contains, pattern: sudo\n"
            "---\n"
            "body"
        )
        fm, _ = extract_frontmatter(content)
        cond = fm["conditions"][0]
        assert cond["field"] == "command"
        assert cond["operator"] == "contains"
        assert cond["pattern"] == "sudo"

    def test_multiple_conditions(self):
        content = (
            "---\n"
            "conditions:\n"
            "- field: command\n"
            "  operator: contains\n"
            "  pattern: rm\n"
            "- field: command\n"
            "  operator: contains\n"
            "  pattern: -rf\n"
            "---\n"
            "body"
        )
        fm, _ = extract_frontmatter(content)
        assert len(fm["conditions"]) == 2

    def test_comments_ignored(self):
        content = "---\n# this is a comment\nname: foo\n---\nbody"
        fm, _ = extract_frontmatter(content)
        assert fm["name"] == "foo"
        assert "#" not in fm


# ---------------------------------------------------------------------------
# Condition.from_dict
# ---------------------------------------------------------------------------

class TestConditionFromDict:
    def test_basic(self):
        c = Condition.from_dict({"field": "command", "operator": "contains", "pattern": "rm"})
        assert c.field == "command"
        assert c.operator == "contains"
        assert c.pattern == "rm"

    def test_defaults(self):
        c = Condition.from_dict({})
        assert c.field == ""
        assert c.operator == "regex_match"
        assert c.pattern == ""


# ---------------------------------------------------------------------------
# Rule.from_dict
# ---------------------------------------------------------------------------

class TestRuleFromDict:
    def _make_rule(self, fm, msg=""):
        return Rule.from_dict(fm, msg)

    def test_simple_pattern_bash(self):
        rule = self._make_rule({"name": "r", "enabled": True, "event": "bash", "pattern": r"rm -rf"})
        assert len(rule.conditions) == 1
        assert rule.conditions[0].field == "command"
        assert rule.conditions[0].operator == "regex_match"
        assert rule.conditions[0].pattern == r"rm -rf"

    def test_simple_pattern_file(self):
        rule = self._make_rule({"name": "r", "enabled": True, "event": "file", "pattern": "eval("})
        assert rule.conditions[0].field == "new_text"

    def test_simple_pattern_other_event(self):
        rule = self._make_rule({"name": "r", "enabled": True, "event": "all", "pattern": "foo"})
        assert rule.conditions[0].field == "content"

    def test_explicit_conditions_take_priority_over_pattern(self):
        fm = {
            "name": "r",
            "enabled": True,
            "event": "bash",
            "pattern": "ignored-pattern",
            "conditions": [{"field": "command", "operator": "equals", "pattern": "explicit"}],
        }
        rule = self._make_rule(fm)
        assert len(rule.conditions) == 1
        assert rule.conditions[0].pattern == "explicit"

    def test_defaults(self):
        rule = self._make_rule({})
        assert rule.name == "unnamed"
        assert rule.enabled is True
        assert rule.action == "warn"
        assert rule.tool_matcher is None

    def test_action_block(self):
        rule = self._make_rule({"action": "block"})
        assert rule.action == "block"

    def test_message_stripped(self):
        rule = self._make_rule({}, "  hello  ")
        assert rule.message == "hello"

    def test_tool_matcher_set(self):
        rule = self._make_rule({"tool_matcher": "Bash|Write"})
        assert rule.tool_matcher == "Bash|Write"

    def test_no_conditions_no_pattern(self):
        rule = self._make_rule({"name": "r", "enabled": True, "event": "bash"})
        assert rule.conditions == []


# ---------------------------------------------------------------------------
# load_rule_file
# ---------------------------------------------------------------------------

class TestLoadRuleFile:
    def _write_tmp(self, content):
        f = tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False)
        f.write(content)
        f.close()
        return f.name

    def test_valid_file(self):
        path = self._write_tmp("---\nname: t\nenabled: true\nevent: bash\npattern: foo\n---\nMsg")
        try:
            rule = load_rule_file(path)
            assert rule is not None
            assert rule.name == "t"
            assert rule.message == "Msg"
        finally:
            os.unlink(path)

    def test_missing_frontmatter_returns_none(self, capsys):
        path = self._write_tmp("No frontmatter")
        try:
            rule = load_rule_file(path)
            assert rule is None
        finally:
            os.unlink(path)

    def test_nonexistent_file_returns_none(self):
        rule = load_rule_file("/nonexistent/path/file.md")
        assert rule is None
