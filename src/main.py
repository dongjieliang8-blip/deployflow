"""
DeployFlow CLI 入口 - 使用 click 定义命令行接口
"""

import json
import click
from .pipeline import DeployFlowPipeline


@click.group()
@click.version_option(version="1.0.0", prog_name="DeployFlow")
def cli():
    """DeployFlow - 智能部署流水线工具"""
    pass


@cli.command()
@click.argument("config_path", type=click.Path(exists=True))
@click.option("--env", "-e", default="staging", type=click.Choice(["dev", "staging", "production"]),
              help="目标部署环境")
@click.option("--type", "-t", "deploy_type", default="rolling",
              type=click.Choice(["rolling", "blue_green", "canary"]),
              help="部署类型")
@click.option("--dry-run", is_flag=True, default=True, help="模拟执行模式 (默认开启)")
@click.option("--no-dry-run", "dry_run", flag_value=False, help="实际执行部署")
@click.option("--validation", "-v", default="standard",
              type=click.Choice(["basic", "standard", "comprehensive"]),
              help="验证级别")
@click.option("--output", "-o", type=click.Path(), help="输出结果 JSON 文件路径")
def deploy(config_path, env, deploy_type, dry_run, validation, output):
    """运行部署流水线

    CONFIG_PATH: 部署配置文件路径 (YAML 格式)
    """
    click.echo("=" * 60)
    click.echo("  DeployFlow - 智能部署流水线")
    click.echo("=" * 60)
    click.echo(f"  配置文件: {config_path}")
    click.echo(f"  目标环境: {env}")
    click.echo(f"  部署类型: {deploy_type}")
    click.echo(f"  模拟执行: {'是' if dry_run else '否'}")
    click.echo(f"  验证级别: {validation}")
    click.echo("=" * 60)

    pipeline = DeployFlowPipeline(
        target_env=env,
        deploy_type=deploy_type,
        dry_run=dry_run,
        validation_level=validation
    )

    result = pipeline.run(config_path)

    # 输出结果
    click.echo("\n" + "=" * 60)
    click.echo("  部署流水线执行结果")
    click.echo("=" * 60)
    click.echo(f"  总状态: {result.get('overall_status', 'unknown')}")
    click.echo(f"  总耗时: {result.get('total_duration_seconds', 0)}秒")

    # 显示各 Agent 状态
    for agent_name, agent_result in result.get("agent_results", {}).items():
        status = agent_result.get("status", "unknown")
        status_icon = {"success": "[OK]", "partial": "[!!]", "error": "[XX]"}.get(status, "[??]")
        click.echo(f"  {status_icon} {agent_name}: {status}")

    click.echo("=" * 60)

    # 保存结果到文件
    if output:
        with open(output, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        click.echo(f"\n结果已保存到: {output}")

    return result


@cli.command()
@click.argument("report_path", type=click.Path(exists=True))
@click.option("--format", "-f", "fmt", default="summary", type=click.Choice(["summary", "full"]),
              help="报告格式: summary=摘要, full=完整")
def report(report_path, fmt):
    """查看部署报告

    REPORT_PATH: 部署结果 JSON 文件路径
    """
    with open(report_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    click.echo("=" * 60)
    click.echo("  DeployFlow 部署报告")
    click.echo("=" * 60)

    click.echo(f"  项目名称: {data.get('project_name', 'N/A')}")
    click.echo(f"  目标环境: {data.get('target_env', 'N/A')}")
    click.echo(f"  部署类型: {data.get('deploy_type', 'N/A')}")
    click.echo(f"  总体状态: {data.get('overall_status', 'N/A')}")
    click.echo(f"  执行时间: {data.get('start_time', 'N/A')} -> {data.get('end_time', 'N/A')}")
    click.echo(f"  总耗时: {data.get('total_duration_seconds', 0)}秒")

    click.echo("\n--- Agent 执行状态 ---")
    for agent_name, agent_result in data.get("agent_results", {}).items():
        status = agent_result.get("status", "unknown")
        click.echo(f"  [{status}] {agent_name}")

    if fmt == "full":
        click.echo("\n--- 完整结果 ---")
        click.echo(json.dumps(data, ensure_ascii=False, indent=2))

    click.echo("=" * 60)


@cli.command()
def agents():
    """列出所有可用的 Agent"""
    click.echo("DeployFlow Agents:")
    click.echo("  1. config_analyzer    - 配置分析 Agent")
    click.echo("  2. strategy_planner   - 策略规划 Agent")
    click.echo("  3. rollout_executor   - 部署执行 Agent")
    click.echo("  4. post_deploy_validator - 部署验证 Agent")


if __name__ == "__main__":
    cli()
