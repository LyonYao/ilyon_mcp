# ilyon_mcp 项目说明

## 项目简介
本项目实现了基于MCP协议的多云资源管理服务，采用Python开发，支持自然语言驱动的云资源自动化操作。
- 支持AWS资源（EC2、S3）的创建与删除
- 集成spaCy意图识别模型，实现自然语言到结构化命令的转换
- 支持千问大模型智能参数补全与自动重试
- 采用分层架构，便于扩展多云和多资源类型

## 目录结构
```
ilyon_mcp/
├── mcp/                # 主服务代码
│   ├── api/            # FastAPI入口与路由
│   ├── adapters/       # 云平台适配器（如aws_adapter.py）
│   ├── orchestrator/   # 业务编排层
│   └── utils/          # 工具类（如意图识别）
├── train/              # 训练数据与spaCy模型训练脚本
├── verify/             # 验证与集成测试脚本（如千问大模型+MCP联动）
├── project-design.md   # 架构与设计文档
└── README.md           # 项目说明
```

## 快速开始
1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
2. 训练意图识别模型（可选，已提供示例模型）：
   ```bash
   cd train
   python train_spacy_intent.py
   ```
3. 启动MCP服务：
   ```bash
   uvicorn mcp.api.main:app --reload
   ```
4. 体验千问大模型+MCP自动化：
   ```bash
   # 先设置千问API Key
   set QWEN_API_KEY=你的千问API Key
   python verify/qwen_mcp_s3_demo.py
   ```

## AWS 认证配置
MCP服务依赖AWS官方SDK（boto3）访问云资源，需提前配置AWS凭证。常用方式如下：

1. 配置环境变量（推荐，适合开发/测试）：
   ```bash
   set AWS_ACCESS_KEY_ID=你的AWS Access Key
   set AWS_SECRET_ACCESS_KEY=你的AWS Secret Key
   set AWS_DEFAULT_REGION=us-west-2  # 可选，默认区域
   ```
   在Linux/macOS下用export替换set。

2. 使用AWS CLI配置（适合长期/多项目）：
   ```bash
   aws configure
   # 按提示输入Access Key、Secret Key和默认区域
   ```

3. 也可通过~/.aws/credentials文件配置，或使用IAM角色（如在EC2/云主机上部署时）。

### 如何获取AWS API Key（Access Key & Secret Key）
1. 登录 [AWS管理控制台](https://console.aws.amazon.com/)。
2. 右上角点击你的用户名，选择“安全凭证”。
3. 在“访问密钥（Access Keys）”区域，点击“创建访问密钥”。
4. 记录生成的 Access Key ID 和 Secret Access Key（只显示一次，务必保存好）。
5. 强烈建议为开发用途单独创建IAM用户，并授予最小权限。

> 切勿将密钥泄露到代码库或公开环境，建议用环境变量或凭证管理工具安全存储。

## 主要特性
- 支持自然语言驱动的云资源管理
- 智能参数补全与自动重试
- 分层结构，易于扩展

## 贡献与扩展
- 新增云平台：在adapters/下添加适配器即可
- 新增资源类型：在适配器和意图识别模型中扩展即可

---
如有问题或建议，欢迎提issue或PR！
