"""
DeployFlowPipeline - 智能部署流水线编排
按顺序执行配置分析 -> 策略规划 -> 部署执行 -> 部署验证 四个 Agent
"""

import json
import os
import yaml
from datetime import datetime

from .agents.config_analyzer import analyze as config_analyze
from .agents.strategy_planner import analyze as strategy_analyze
from .agents.rollout_executor import analyze as rollout_analyze
from .agents.post_deploy_validator import analyze as validator_analyze


class DeployFlowPipeline:
    """智能部署流水线，编排四个 Agent 完成端到端的部署流程"""

    def __init__(self, target_env="staging", deploy_type="rolling",
                 dry_run=True, validation_level="standard"):
        """
        初始化部署流水线

        Args:
            target_env: 目标环境 (dev/staging/production)
            deploy_type: 部署类型 (rolling/blue_green/canary)
            dry_run: 是否为模拟执行
            validation_level: 验证级别 (basic/standard/comprehensive)
        """
        self.target_env = target_env
        self.deploy_type = deploy_type
        self.dry_run = dry_run
        self.validation_level = validation_level
        self.results = {}
        self.start_time = None
        self.end_time = None

    def run(self, input_path):
        """
        按顺序执行部署流水线的四个 Agent

        Args:
            input_path: str, 部署配置文件路径 (YAML 格式)
        Returns:
            dict: 汇总结果，包含所有 Agent 的输出
        """
        self.start_time = datetime.now()

        # 1. 读取配置文件
        config_data = self._load_config(input_path)
        if config_data is None:
            return self._build_error_result("无法加载配置文件")

        project_name = config_data.get("project_name", os.path.basename(input_path))

        print(f"[DeployFlow] 开始部署流水线 - 项目: {project_name}")
        print(f"[DeployFlow] 目标环境: {self.target_env}, 部署类型: {self.deploy_type}")
        print(f"[DeployFlow] 模拟执行: {'是' if self.dry_run else '否'}")

        # 2. Agent 1: 配置分析
        print("\n[Step 1/4] 配置分析...")
        config_result = config_analyze({
            "config": config_data.get("config", ""),
            "project_name": project_name
        })
        self.results["config_analysis"] = config_result
        print(f"  状态: {config_result['status']}")

        # 3. Agent 2: 策略规划
        print("\n[Step 2/4] 策略规划...")
        strategy_result = strategy_analyze({
            "config_analysis": config_result.get("analysis", {}),
            "target_env": self.target_env,
            "deploy_type": self.deploy_type,
            "constraints": config_data.get("constraints", {})
        })
        self.results["strategy_planning"] = strategy_result
        print(f"  状态: {strategy_result['status']}")

        # 4. Agent 3: 部署执行
        print("\n[Step 3/4] 部署执行...")
        rollout_result = rollout_analyze({
            "strategy": strategy_result.get("strategy", {}),
            "config": config_data.get("config", ""),
            "project_name": project_name,
            "dry_run": self.dry_run
        })
        self.results["rollout_execution"] = rollout_result
        print(f"  状态: {rollout_result['status']}")

        # 5. Agent 4: 部署验证
        print("\n[Step 4/4] 部署验证...")
        validation_result = validator_analyze({
            "execution_report": rollout_result.get("execution_report", {}),
            "health_check_config": config_data.get("health_check", {}),
            "validation_level": self.validation_level
        })
        self.results["post_deploy_validation"] = validation_result
        print(f"  状态: {validation_result['status']}")

        # 6. 汇总结果
        self.end_time = datetime.now()
        summary = self._build_summary(project_name)

        print(f"\n[DeployFlow] 流水线执行完成 - 总耗时: {summary['total_duration_seconds']}秒")

        return summary

    def _load_config(self, input_path):
        """加载 YAML 配置文件"""
        try:
            with open(input_path, "r", encoding="utf-8") as f:
                raw = f.read()
            data = yaml.safe_load(raw)
            if data is None:
                data = {}
            data["config"] = raw
            return data
        except FileNotFoundError:
            print(f"[错误] 配置文件不存在: {input_path}")
            return None
        except Exception as e:
            print(f"[错误] 加载配置文件失败: {e}")
            return None

    def _build_summary(self, project_name):
        """构建汇总结果"""
        duration = (self.end_time - self.start_time).total_seconds()

        all_success = all(
            r.get("status") == "success"
            for r in self.results.values()
        )

        return {
            "pipeline": "DeployFlow",
            "project_name": project_name,
            "target_env": self.target_env,
            "deploy_type": self.deploy_type,
            "dry_run": self.dry_run,
            "validation_level": self.validation_level,
            "overall_status": "success" if all_success else "partial",
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "total_duration_seconds": round(duration, 2),
            "agent_results": self.results
        }

    def _build_error_result(self, error_message):
        """构建错误结果"""
        self.end_time = datetime.now()
        return {
            "pipeline": "DeployFlow",
            "overall_status": "error",
            "error": error_message,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat(),
            "agent_results": self.results
        }
