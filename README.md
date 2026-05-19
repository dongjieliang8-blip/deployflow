# DeployFlow — 智能部署流水线

基于多 Agent 长链推理的智能部署系统。

## 安装

```bash
pip install -r requirements.txt
```

## 配置

在项目根目录创建 `.env` 文件：

```
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_BASE_URL=https://token-plan-cn.xiaomimimo.com/v1
DEEPSEEK_MODEL=mimo-v2.5
```

## 使用

```bash
# 运行部署分析
python -m src.main deploy --input ./demo/sample_data/sample_deploy.yaml

# 查看报告
python -m src.main report --input ./output/deployflow_report.json
```

## 项目结构

```
deployflow/
├── src/
│   ├── main.py
│   ├── pipeline.py
│   ├── utils.py
│   └── agents/
│       ├── config_analyzer.py
│       ├── strategy_planner.py
│       ├── rollout_executor.py
│       └── post_deploy_validator.py
├── demo/sample_data/
├── tests/
├── requirements.txt
└── APPLICATION.md
```
