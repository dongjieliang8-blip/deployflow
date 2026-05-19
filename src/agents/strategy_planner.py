"""
策略规划 Agent - 根据配置分析结果规划部署策略
"""

import json
from ..utils import call_llm


def analyze(data):
    """
    根据配置分析和上下文信息规划部署策略

    Args:
        data: dict
            - config_analysis: dict, config_analyzer 的输出结果
            - target_env: str, 目标环境 (dev/staging/production)
            - deploy_type: str, 部署类型 (rolling/blue_green/canary)
            - constraints: dict, 可选约束条件
    Returns:
        dict: JSON 格式的策略规划结果
    """
    config_analysis = data.get("config_analysis", {})
    target_env = data.get("target_env", "staging")
    deploy_type = data.get("deploy_type", "rolling")
    constraints = data.get("constraints", {})

    system_prompt = """你是一个经验丰富的部署策略规划师。
请根据配置分析结果和目标环境，规划最合适的部署策略。始终以 JSON 格式返回结果。"""

    prompt = f"""请根据以下信息规划部署策略:

部署配置分析:
{json.dumps(config_analysis, ensure_ascii=False, indent=2)}

目标环境: {target_env}
部署类型: {deploy_type}
约束条件: {json.dumps(constraints, ensure_ascii=False, indent=2)}

请返回 JSON 格式的策略规划结果:
{{
    "deploy_type": "实际采用的部署类型",
    "strategy_name": "策略名称",
    "pre_deploy_checks": [
        {{
            "check_name": "检查项名称",
            "command": "执行命令",
            "timeout_seconds": 超时时间,
            "critical": true/false
        }}
    ],
    "deploy_steps": [
        {{
            "step": 1,
            "name": "步骤名称",
            "action": "执行动作",
            "command": "具体命令",
            "rollback_command": "回滚命令",
            "estimated_duration_seconds": 预计耗时,
            "can_parallel": false
        }}
    ],
    "rollback_strategy": {{
        "trigger_conditions": ["触发回滚的条件"],
        "rollback_steps": ["回滚步骤"],
        "max_rollback_window_seconds": 回滚窗口时间
    }},
    "health_check": {{
        "endpoint": "健康检查端点",
        "expected_status": 200,
        "timeout_seconds": 超时时间,
        "retry_count": 重试次数
    }},
    "notification": {{
        "on_success": ["通知渠道和内容"],
        "on_failure": ["通知渠道和内容"]
    }},
    "estimated_total_duration_seconds": 预计总耗时,
    "risk_assessment": {{
        "overall_risk": "low/medium/high",
        "risk_factors": ["风险因素"],
        "mitigation_steps": ["缓解措施"]
    }}
}}"""

    result = call_llm(prompt, system_prompt=system_prompt)

    try:
        parsed = json.loads(result)
        return {
            "agent": "strategy_planner",
            "status": "success",
            "target_env": target_env,
            "deploy_type": deploy_type,
            "strategy": parsed
        }
    except json.JSONDecodeError:
        return {
            "agent": "strategy_planner",
            "status": "partial",
            "target_env": target_env,
            "raw_output": result,
            "strategy": None
        }
