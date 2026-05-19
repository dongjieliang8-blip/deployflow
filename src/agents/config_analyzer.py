"""
配置分析 Agent - 分析部署配置文件，提取关键信息和潜在风险
"""

import json
from ..utils import call_llm


def analyze(data):
    """
    分析部署配置，返回结构化的配置分析结果

    Args:
        data: dict, 包含部署配置内容
            - config: str, YAML 格式的部署配置内容
            - project_name: str, 项目名称
    Returns:
        dict: JSON 格式的分析结果
    """
    config_content = data.get("config", "")
    project_name = data.get("project_name", "unknown")

    system_prompt = """你是一个资深的 DevOps 配置分析专家。请分析用户提供的部署配置文件，
提取关键信息并评估潜在风险。始终以 JSON 格式返回结果，不要包含其他文本。"""

    prompt = f"""请分析以下部署配置文件（项目: {project_name}）:

```yaml
{config_content}
```

请返回 JSON 格式的分析结果，包含以下字段：
{{
    "project_name": "项目名称",
    "services_count": 服务数量,
    "service_list": ["服务名称列表"],
    "has_database": 是否包含数据库服务,
    "has_cache": 是否包含缓存服务,
    "has_load_balancer": 是否包含负载均衡,
    "total_replicas": 总副本数,
    "exposed_ports": ["对外暴露的端口列表"],
    "environment_vars_count": 环境变量数量,
    "resource_limits": {{
        "has_cpu_limits": true/false,
        "has_memory_limits": true/false
    }},
    "risky_configs": [
        {{
            "field": "配置字段路径",
            "risk_level": "high/medium/low",
            "description": "风险描述",
            "suggestion": "改进建议"
        }}
    ],
    "recommendations": ["优化建议列表"]
}}"""

    result = call_llm(prompt, system_prompt=system_prompt)

    try:
        parsed = json.loads(result)
        return {
            "agent": "config_analyzer",
            "status": "success",
            "project_name": project_name,
            "analysis": parsed
        }
    except json.JSONDecodeError:
        return {
            "agent": "config_analyzer",
            "status": "partial",
            "project_name": project_name,
            "raw_output": result,
            "analysis": None
        }
