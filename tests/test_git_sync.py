import unittest

import git_sync


class TestGitSync(unittest.TestCase):
    def test_parse_status_with_ahead_behind_and_changes(self):
        text = """## main...origin/main [ahead 2, behind 1]
 M README.md
?? new_file.md
"""
        stats = git_sync.parse_status(text)
        self.assertEqual(stats["ahead"], 2)
        self.assertEqual(stats["behind"], 1)
        self.assertEqual(stats["local_changes"], 2)

    def test_parse_status_without_changes(self):
        text = "## main...origin/main\n"
        stats = git_sync.parse_status(text)
        self.assertEqual(stats["ahead"], 0)
        self.assertEqual(stats["behind"], 0)
        self.assertEqual(stats["local_changes"], 0)

    def test_format_command_error_authentication(self):
        msg = git_sync.format_command_error(["git", "push"], "Authentication failed")
        self.assertIn("认证失败", msg)

    def test_format_command_error_network(self):
        msg = git_sync.format_command_error(["git", "push"], "Could not resolve host")
        self.assertIn("网络不可用", msg)

    def test_format_command_error_conflict(self):
        msg = git_sync.format_command_error(["git", "push"], "non-fast-forward")
        self.assertIn("落后于远程", msg)

    def test_get_commit_message_blank_should_fail(self):
        with self.assertRaises(git_sync.GitSyncError):
            git_sync.get_commit_message("   ")

    def test_get_commit_message_ok(self):
        self.assertEqual(git_sync.get_commit_message("  test message  "), "test message")


if __name__ == "__main__":
    unittest.main()
