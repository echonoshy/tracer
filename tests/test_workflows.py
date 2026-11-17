import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import requests

from gewechat_client.api.login_api import LoginApi
from utils.readme_downloader import get_github_readme
from workflows import initialize, login, post_group_message

ROOT = Path(__file__).resolve().parents[1]


class WorkflowTests(unittest.TestCase):
    def test_documented_script_paths(self):
        env = dict(os.environ)
        env.pop("PYTHONPATH", None)
        for name in ("initialize", "login", "post_group_message"):
            with self.subTest(name=name):
                run = subprocess.run(
                    [sys.executable, str(ROOT / "workflows" / f"{name}.py"), "--help"],
                    env=env, cwd=ROOT.parent, capture_output=True, text=True, timeout=10,
                )
                self.assertEqual(run.returncode, 0, run.stderr)
                self.assertIn("usage:", run.stdout)

    def test_scheduler_receives_failure_exit_code(self):
        with patch.dict(os.environ, {}, clear=True), patch("sys.argv", ["post_group_message"]):
            self.assertEqual(post_group_message.main(), 1)

    def test_scheduler_receives_delivery_status(self):
        config = {"base_url": "unused", "app_id": "app", "token": "token", "chatroom_id": "group"}
        for reply, status in (({"ret": 200}, 0), ({"ret": 500}, 1), (None, 1)):
            with self.subTest(reply=reply), patch("sys.argv", ["post_group_message"]), \
                    patch.object(post_group_message, "init_config", return_value=config), \
                    patch.object(post_group_message, "send_group_message", return_value=reply):
                self.assertEqual(post_group_message.main(), status)

    def test_login_without_recipient_only_logs_in(self):
        with patch.dict(os.environ, {"BASE_URL": "unused", "TOKEN": "t", "APP_ID": "a"}), \
                patch("sys.argv", ["login"]), patch.object(login, "GewechatClient") as client:
            client.return_value.login.return_value = ("a", "")
            self.assertEqual(login.main(), 0)
            client.return_value.fetch_contacts_list.assert_not_called()
            client.return_value.post_text.assert_not_called()

    def test_partial_login_is_an_initialization_failure(self):
        with patch.object(initialize, "get_token", return_value="test"), \
                patch.object(initialize, "GewechatClient") as client:
            client.return_value.login.return_value = ("allocated-id", "timeout")
            self.assertEqual(initialize.get_app_id(), 1)

    def test_completed_login_does_not_refresh_an_expired_code(self):
        api = LoginApi("unused", "")
        with patch.object(api, "_get_and_validate_qr", side_effect=[("a", "qr")]) as get_qr, \
                patch.object(api, "check_qr", return_value={"ret": 200, "data": {"status": 2}}), \
                patch("gewechat_client.api.login_api.make_and_print_qr"):
            self.assertEqual(api.login(""), ("a", ""))
            get_qr.assert_called_once()

    def test_expiring_codes_respect_poll_limit(self):
        api = LoginApi("unused", "")
        status = {"ret": 200, "data": {"status": 1, "expiredTime": 1}}
        with patch.object(api, "_get_and_validate_qr", return_value=("a", "qr")), \
                patch.object(api, "check_qr", side_effect=[status] * 100) as check, \
                patch("gewechat_client.api.login_api.make_and_print_qr"), \
                patch("gewechat_client.api.login_api.print_yellow"), \
                patch("gewechat_client.api.login_api.time.sleep"):
            app_id, error = api.login("")
            self.assertEqual(app_id, "a")
            self.assertIn("超时", error)
            self.assertEqual(check.call_count, 100)

    def test_specific_readme_keeps_branch_and_file_path(self):
        session = MagicMock()
        session.__enter__.return_value = session
        session.get.return_value.text = "the requested chapter"
        url = "https://github.com/owner/repo/blob/dev/docs/README.md#intro"
        with patch("utils.readme_downloader.create_session", return_value=session):
            self.assertEqual(get_github_readme(url), "the requested chapter")
            call = session.get.call_args
            self.assertEqual(call.args[0], "https://api.github.com/repos/owner/repo/contents/docs/README.md")
            self.assertEqual(call.kwargs["params"], {"ref": "dev"})
            session.get.return_value.raise_for_status.side_effect = [requests.HTTPError(), None]
            self.assertEqual(get_github_readme(url), "the requested chapter")
            self.assertEqual(session.get.call_args.args[0],
                             "https://raw.githubusercontent.com/owner/repo/dev/docs/README.md")

    def test_empty_summary_is_never_sent(self):
        config = {"base_url": "unused", "token": "test", "app_id": "a", "chatroom_id": "g"}
        with patch.object(post_group_message, "extract_github_rankings", return_value={"content": " "}), \
                patch.object(post_group_message, "GewechatClient") as client:
            self.assertIsNone(post_group_message.send_group_message(config))
            client.return_value.post_text.assert_not_called()

    def test_explicit_test_recipient_receives_one_message(self):
        with patch.dict(os.environ, {"BASE_URL": "unused", "TOKEN": "t", "APP_ID": "a"}), \
                patch("sys.argv", ["login", "--test-recipient", "chosen"]), \
                patch.object(login, "GewechatClient") as client:
            client.return_value.login.return_value = ("a", "")
            client.return_value.post_text.return_value = {"ret": 200}
            self.assertEqual(login.main(), 0)
            client.return_value.post_text.assert_called_once_with("a", "chosen", "你好啊")


if __name__ == "__main__":
    unittest.main()
