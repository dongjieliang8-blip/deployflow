"""
部署验证 Agent - 在部署完成后进行健康检查和功能验证
"""

import json
from ..utils import call_llm


def analyze(data):
    """
    对部署结果进行全面验证，包括健康检查、功能测试和性能指标

    Args:
        data: dict
            - execution_report: dict, rollout_executor 的输出结果
            - health_check_config: dict, 健康检查配置
            - validation_level: str, 验证级别 (basic/standard/comprehensive)
    Returns:
        dict: JSON 格式的验证结果
    """
    execution_report = data.get("execution_report", {})
    health_check_config = data.get("health_check_config", {})
    validation_level = data.get("validation_level", "standard")

    system_prompt = """你是一个部署验证专家。
请对部署结果进行全面验证分析，评估部署质量和潜在问题。始终以 JSON 格式返回结果。"""

    prompt = f"""请对以下部署执行结果进行验证分析:

执行报告:
{json.dumps(execution_report, ensure_ascii=False, indent=2)}

健康检查配置:
{json.dumps(health_check_config, ensure_ascii=False, indent=2)}

验证级别: {validation_level}

请返回 JSON 格式的验证结果:
{{
    "validation_level": "使用的验证级别",
    "overall_health": "healthy/degraded/unhealthy",
    "health_checks": [
        {{
            "check_name": "检查项名称",
            "status": "pass/fail/warning",
            "details": "详细信息",
            "metrics": {{}},
            "threshold": "阈值说明",
            "actual_value": "实际值"
        }}
    ],
    "service_status": [
        {{
            "service_name": "服务名称",
            "status": "healthy/unhealthy/degraded",
            "readiness": true/false,
            "liveness": true/false,
            "response_time_ms": 响应时间,
            "error_rate": 错误率
        }}
    ],
    "functional_tests": [
        {{
            "test_name": "测试名称",
            "description": "测试描述",
            "status": "pass/fail/skip",
            "duration_ms": 耗时,
            "details": "详细信息"
        }}
    ],
    "performance_metrics": {{
        "avg_response_time_ms": 平均响应时间,
        "p99_response_time_ms": P99 响应时间,
        "throughput_rps": 吞吐量,
        "error_rate_percent": 错误率百分比
    }},
    "issues_found": [
        {{
            "severity": "critical/high/medium/low",
            "category": "分类",
            "description": "问题描述",
            "affected_service": "受影响的服务",
            "remediation": "修复建议"
        }}
    ],
    "verification_summary": {{
        "total_checks": 总检查数,
        "passed": 通过数,
        "failed": 失败数,
        "warnings": 警告数,
        "recommendation": "deploy_rollback/continue_monitoring/deployment_approved"
    }},
    "rollback_recommended": false,
    "rollback_reason": null 或 "回滚原因"
}}"""

    result = call_llm(prompt, system_prompt=system_prompt)

    try:
        parsed = json.loads(result)
        return {
            "agent": "post_deploy_validator",
            "status": "success",
            "validation_level": validation_level,
            "validation_result": parsed
        }
    except json.JSONDecodeError:
        return {
            "agent": "post_deploy_validator",
            "status": "partial",
            "raw_output": result,
            "validation_result": None
        }
