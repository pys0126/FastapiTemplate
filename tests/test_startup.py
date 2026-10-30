"""启动路径与配置加载测试，不连接外部服务。"""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class StartupTest(unittest.TestCase):
    """确保服务不依赖调用者的工作目录。"""

    def run_from_other_directory(
        self, code: str, config_path: Path, working_dir: Path
    ) -> subprocess.CompletedProcess[str]:
        """从隔离目录执行 Python，使用指定配置路径。"""
        environment = os.environ.copy()
        environment.pop("APP_SECRET_KEY", None)
        environment["APP_CONFIG"] = str(config_path)
        environment["PYTHONPATH"] = os.pathsep.join(
            filter(None, (str(PROJECT_ROOT), environment.get("PYTHONPATH")))
        )
        return subprocess.run(
            [sys.executable, "-c", code],
            cwd=working_dir,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_config_and_module_discovery_ignore_working_directory(self) -> None:
        """外部配置、日志路径和模块发现可在任意目录工作。"""
        with tempfile.TemporaryDirectory() as directory:
            temporary_dir = Path(directory)
            config_path = temporary_dir / "settings.yaml"
            config_path.write_text(
                "ProjectName: StartupTest\n"
                "ServerConfig:\n  log_dir: logs/startup-test\n"
                "  secret_key: test-secret\n",
                encoding="utf-8",
            )
            result = self.run_from_other_directory(
                "from application.config import PROJECT_NAME; "
                "from application.config.DatabaseConfig import MysqlConfig; "
                "from application.config.ServerConfig import ServerConfig; "
                "print(PROJECT_NAME, ServerConfig.log_dir, MysqlConfig.models)",
                config_path,
                temporary_dir,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("StartupTest", result.stdout)
            self.assertIn(str(PROJECT_ROOT / "logs" / "startup-test"), result.stdout)
            self.assertIn("application.service.user.Model", result.stdout)
            self.assertFalse((temporary_dir / "logs").exists())

    def test_missing_config_reports_path(self) -> None:
        """找不到配置时给出可操作的错误提示。"""
        with tempfile.TemporaryDirectory() as directory:
            temporary_dir = Path(directory)
            config_path = temporary_dir / "missing.yaml"
            result = self.run_from_other_directory(
                "import application.config", config_path, temporary_dir
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(str(config_path), result.stderr)
            self.assertIn("APP_CONFIG", result.stderr)

    def test_missing_secret_is_rejected(self) -> None:
        """避免多进程启动后各自生成不同的 Token 密钥。"""
        with tempfile.TemporaryDirectory() as directory:
            temporary_dir = Path(directory)
            config_path = temporary_dir / "settings.yaml"
            config_path.write_text("ServerConfig: {}\n", encoding="utf-8")
            result = self.run_from_other_directory(
                "import application.config.ServerConfig", config_path, temporary_dir
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("APP_SECRET_KEY", result.stderr)

    def test_dev_reload_watches_project_directory(self) -> None:
        """从其他目录启动开发模式时仍监听项目代码。"""
        with tempfile.TemporaryDirectory() as directory:
            temporary_dir = Path(directory)
            config_path = temporary_dir / "settings.yaml"
            config_path.write_text(
                "ServerConfig:\n  secret_key: test-secret\n", encoding="utf-8"
            )
            result = self.run_from_other_directory(
                "from unittest.mock import patch; "
                "from main import run_web; "
                "runner = patch('uvicorn.run').start(); "
                "run_web('dev'); "
                "print(runner.call_args.kwargs['reload_dirs'])",
                config_path,
                temporary_dir,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(str(PROJECT_ROOT), result.stdout)

    def test_command_help_does_not_need_config(self) -> None:
        """命令行帮助在尚未配置部署环境时仍可查看。"""
        with tempfile.TemporaryDirectory() as directory:
            temporary_dir = Path(directory)
            result = self.run_from_other_directory(
                f"import sys; sys.path.insert(0, {str(PROJECT_ROOT)!r}); "
                "from main import main; main(['--help'])",
                temporary_dir / "missing.yaml",
                temporary_dir,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("{pro,dev,debug,worker}", result.stdout)


if __name__ == "__main__":
    unittest.main()
