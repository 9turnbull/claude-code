"""Tests for security_reminder_hook.py."""

import importlib.util
import json
import os
import sys
import tempfile
import time
import pytest

# Load the module directly by file path (directory name has a hyphen so it's not
# importable as a regular package).
_HOOK_PATH = os.path.join(
    os.path.dirname(__file__), '..', 'hooks', 'security_reminder_hook.py'
)
_spec = importlib.util.spec_from_file_location("security_reminder_hook", _HOOK_PATH)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

check_patterns = _mod.check_patterns
extract_content_from_input = _mod.extract_content_from_input
get_state_file = _mod.get_state_file
load_state = _mod.load_state
save_state = _mod.save_state
cleanup_old_state_files = _mod.cleanup_old_state_files
SECURITY_PATTERNS = _mod.SECURITY_PATTERNS


# ---------------------------------------------------------------------------
# check_patterns – path-based detection
# ---------------------------------------------------------------------------

class TestCheckPatternsPathBased:
    def test_github_actions_yml_detected(self):
        rule, reminder = check_patterns(".github/workflows/ci.yml", "")
        assert rule == "github_actions_workflow"
        assert "Command Injection" in reminder

    def test_github_actions_yaml_detected(self):
        rule, _ = check_patterns(".github/workflows/deploy.yaml", "")
        assert rule == "github_actions_workflow"

    def test_github_actions_leading_slash_normalised(self):
        rule, _ = check_patterns("/.github/workflows/ci.yml", "")
        assert rule == "github_actions_workflow"

    def test_non_workflow_yml_not_detected(self):
        rule, _ = check_patterns("config/settings.yml", "")
        assert rule is None

    def test_non_workflow_path_not_detected(self):
        rule, _ = check_patterns("src/index.ts", "")
        assert rule is None


# ---------------------------------------------------------------------------
# check_patterns – content-based detection
# ---------------------------------------------------------------------------

class TestCheckPatternsContentBased:
    def test_child_process_exec_detected(self):
        rule, reminder = check_patterns("src/app.ts", "child_process.exec('cmd')")
        assert rule == "child_process_exec"
        assert "execFileNoThrow" in reminder

    def test_exec_sync_detected(self):
        rule, _ = check_patterns("src/app.ts", "execSync('ls')")
        assert rule == "child_process_exec"

    def test_exec_parens_detected(self):
        rule, _ = check_patterns("src/app.ts", "exec('rm -rf')")
        assert rule == "child_process_exec"

    def test_new_function_detected(self):
        rule, _ = check_patterns("src/app.ts", "const fn = new Function('return 1')")
        assert rule == "new_function_injection"

    def test_eval_detected(self):
        rule, _ = check_patterns("src/app.ts", "eval(userInput)")
        assert rule == "eval_injection"

    def test_dangerous_set_inner_html_detected(self):
        rule, _ = check_patterns("src/app.tsx", "dangerouslySetInnerHTML={{__html: data}}")
        assert rule == "react_dangerously_set_html"

    def test_document_write_detected(self):
        rule, _ = check_patterns("src/app.js", "document.write('<b>hi</b>')")
        assert rule == "document_write_xss"

    def test_inner_html_equals_space_detected(self):
        rule, _ = check_patterns("src/app.js", "el.innerHTML = userInput")
        assert rule == "innerHTML_xss"

    def test_inner_html_equals_no_space_detected(self):
        rule, _ = check_patterns("src/app.js", "el.innerHTML=userInput")
        assert rule == "innerHTML_xss"

    def test_pickle_detected(self):
        rule, _ = check_patterns("app.py", "import pickle")
        assert rule == "pickle_deserialization"

    def test_os_system_detected(self):
        rule, _ = check_patterns("app.py", "os.system('ls')")
        assert rule == "os_system_injection"

    def test_from_os_import_system_detected(self):
        rule, _ = check_patterns("app.py", "from os import system")
        assert rule == "os_system_injection"

    def test_safe_content_returns_none(self):
        rule, _ = check_patterns("src/safe.ts", "console.log('hello')")
        assert rule is None

    def test_empty_content_path_only_no_match(self):
        rule, _ = check_patterns("src/safe.py", "")
        assert rule is None


# ---------------------------------------------------------------------------
# extract_content_from_input
# ---------------------------------------------------------------------------

class TestExtractContentFromInput:
    def test_write_tool(self):
        content = extract_content_from_input("Write", {"content": "print('hi')"})
        assert content == "print('hi')"

    def test_edit_tool(self):
        content = extract_content_from_input("Edit", {"new_string": "new code"})
        assert content == "new code"

    def test_multiedit_tool_joins_edits(self):
        edits = [{"new_string": "part1"}, {"new_string": "part2"}]
        content = extract_content_from_input("MultiEdit", {"edits": edits})
        assert "part1" in content
        assert "part2" in content

    def test_multiedit_empty_edits(self):
        content = extract_content_from_input("MultiEdit", {"edits": []})
        assert content == ""

    def test_unknown_tool_returns_empty(self):
        content = extract_content_from_input("Bash", {"command": "ls"})
        assert content == ""


# ---------------------------------------------------------------------------
# State management (load / save / cleanup)
# ---------------------------------------------------------------------------

class TestStateManagement:
    def _setup_tmp_home(self, monkeypatch, tmpdir):
        """Patch os.path.expanduser to redirect ~ to tmpdir."""
        original = os.path.expanduser
        monkeypatch.setattr(os.path, "expanduser",
                            lambda p: p.replace("~", str(tmpdir)))
        # Also patch in the loaded module
        monkeypatch.setattr(_mod.os.path, "expanduser",
                            lambda p: p.replace("~", str(tmpdir)))

    def test_load_state_empty_when_no_file(self, monkeypatch, tmp_path):
        self._setup_tmp_home(monkeypatch, tmp_path)
        state = load_state("test-session-abc")
        assert state == set()

    def test_save_and_load_roundtrip(self, monkeypatch, tmp_path):
        self._setup_tmp_home(monkeypatch, tmp_path)
        sid = "session-xyz"
        warnings = {"file.py-eval_injection", "ci.yml-github_actions_workflow"}
        save_state(sid, warnings)
        loaded = load_state(sid)
        assert loaded == warnings

    def test_load_state_handles_corrupt_file(self, monkeypatch, tmp_path):
        self._setup_tmp_home(monkeypatch, tmp_path)
        sid = "corrupt-session"
        state_file = get_state_file(sid)
        os.makedirs(os.path.dirname(state_file), exist_ok=True)
        with open(state_file, 'w') as f:
            f.write("not valid json{{")
        state = load_state(sid)
        assert state == set()

    def test_get_state_file_includes_session_id(self):
        path = get_state_file("my-session-id")
        assert "my-session-id" in path

    def test_cleanup_removes_old_files(self, monkeypatch, tmp_path):
        self._setup_tmp_home(monkeypatch, tmp_path)

        state_dir = tmp_path / ".claude"
        state_dir.mkdir(parents=True, exist_ok=True)

        # Create a file with mtime = 31 days ago
        old_file = state_dir / "security_warnings_state_old-session.json"
        old_file.write_text("[]")
        old_mtime = time.time() - (31 * 24 * 60 * 60)
        os.utime(str(old_file), (old_mtime, old_mtime))

        # Create a recent file
        new_file = state_dir / "security_warnings_state_new-session.json"
        new_file.write_text("[]")

        cleanup_old_state_files()

        assert not old_file.exists(), "Old state file should be removed"
        assert new_file.exists(), "Recent state file should be kept"

    def test_cleanup_ignores_missing_directory(self, monkeypatch):
        monkeypatch.setattr(_mod.os.path, "expanduser", lambda p: "/nonexistent/path")
        # Should not raise
        cleanup_old_state_files()
