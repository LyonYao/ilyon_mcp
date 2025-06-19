# MCP 目录结构说明

- api/         # API层，FastAPI入口和路由
- adapters/    # 云平台适配器（如aws_adapter.py）
- orchestrator/# 业务编排层
- utils/       # 工具类（如意图识别）

所有业务代码分层清晰，便于扩展和维护。
