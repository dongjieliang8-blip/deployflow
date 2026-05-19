"""
部署执行 Agent - 按照策略执行部署操作并生成执行报告
"""

import json
from ..utils import call_llm


def analyze(data):
    """
    模拟执行部署流程，生成执行报告和状态信息

    Args:
        data: dict
            - strategy: dict, strategy_planner 的输出结果
            - config: str, 原始部署配置
            - project_name: str, 项目名称
            - dry_run: bool, 是否为模拟执行 (默认 True)
    Returns:
        dict: JSON 格式的执行结果
    """
    strategy = data.get("strategy", {})
    config = data.get("config", "")
    project_name = data.get("project_name", "unknown")
    dry_run = data.get("dry_run", True)

    system_prompt = """你是一个部署执行专家。
请模拟执行部署流程，记录每个步骤的执行状态和输出。始终以 JSON 格式返回结果。"""

    prompt = f"""请模拟执行以下部署任务:

项目名称: {project_name}
部署策略:
{json.dumps(strategy, ensure_ascii=False, indent=2)}

部署配置:
```yaml
{config}
```

模拟执行模式: {'是' if dry_run else '否'}

请返回 JSON 格式的执行报告:
{{
    "project_name": "项目名称",
    "execution_id": "执行唯一标识 (用 uuid 格式)",
    "start_time": "模拟开始时间 (ISO 格式)",
    "end_time": "模拟结束时间 (ISO 格式)",
    "dry_run": true/false,
    "overall_status": "success/failed/partial",
    "step_results": [
        {{
            "step": 1,
            "name": "步骤名称",
            "status": "success/failed/skipped",
            "output": "步骤输出信息",
            "duration_seconds": 实际耗时,
            "error": null 或 "错误信息"
        }}
    ],
    "deployed_services": [
        {{
            "service_name": "服务名称",
            "version": "部署版本",
            "replicas": 副本数,
            "status": "running/pending/failed",
            "endpoint": "服务访问地址"
        }}
    ],
    "summary": {{
        "total_steps": 总步骤数,
        "success_steps": 成功步骤数,
        "failed_steps": 失败步骤数,
        "skipped_steps": 跳过步骤数,
        "total_duration_seconds": 总耗时,
        "deployed_successfully": true/false
    }},
    "warnings": ["警告信息列表"],
    "next_actions": ["后续操作建议"]
}}"""

    result = call_llm(prompt, system_prompt=system_prompt)

    try:
        parsed = json.loads(result)
        return {
            "agent": "rollout_executor",
            "status": "success",
            "project_name": project_name,
            "dry_run": dry_run,
            "execution_report": parsed
        }
    except json.JSONDecodeError:
        return {
            "agent": "rollout_executor",
            "status": "partial",
            "project_name": project_name,
            "raw_output": result,
            "execution_report": None
        }
