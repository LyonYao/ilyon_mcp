# MCP 服务项目设计（Python实现，支持AWS云资源部署，后续可扩展）

## 1. MCP协议简介
MCP（Model Context Protocol）是一种标准化协议，旨在让客户端与后端服务进行结构化、可扩展的上下文交互。MCP常用于AI、云资源编排等场景，核心思想是通过标准化的消息格式和接口，简化不同系统间的集成。

### MCP协议核心要素
- **请求格式**：通常为JSON，包含`input`（输入）、`context`（上下文）、`parameters`（参数）等字段。
- **响应格式**：JSON，包含`output`（输出）、`status`（状态）、`error`（错误信息）等。
- **接口规范**：一般为RESTful API，也可支持gRPC等。

#### 示例请求
```json
{
  "input": "创建一个AWS EC2实例",
  "context": {
    "user": "alice",
    "cloud": "aws"
  },
  "parameters": {
    "instance_type": "t2.micro",
    "region": "us-west-2"
  }
}
```

#### 示例响应
```json
{
  "output": "EC2实例已创建，ID: i-1234567890abcdef0",
  "status": "success",
  "error": null
}
```

## 1.1 MCP服务如何理解 input 字段？
MCP协议的`input`字段通常是自然语言描述（如“创建一个AWS EC2实例”）。MCP服务需要对`input`进行解析，理解用户意图，然后根据意图和参数决定要执行的操作。

### 实现方式
1. **规则/关键字匹配**：
   - 适合初期开发。
   - 通过判断`input`中是否包含“创建”“EC2”等关键词，结合`context.cloud`和`parameters`，决定调用哪个云平台的哪个资源接口。
2. **意图识别（NLP）**：
   - 适合后期扩展。
   - 使用NLP模型（如意图分类器）自动识别用户意图，将自然语言转为结构化命令。

> 建议：项目初期可采用规则匹配，后续如需支持更复杂的自然语言输入，可引入NLP模型。

## 1.2 NLP模型说明
NLP（自然语言处理）模型用于理解和解析用户输入的自然语言。

### 常见NLP模型类型
1. **轻量级本地模型**：
   - 如 spaCy、NLTK、sklearn 等。
   - 可在本地训练简单的意图分类器，适合关键词提取、基础分类。
   - 部署简单，适合初期开发。
2. **大型预训练模型（大模型）**：
   - 如 OpenAI GPT、Azure OpenAI、AWS Bedrock 等。
   - 需要调用外部API，具备更强的自然语言理解能力，支持复杂语义和多轮对话。
   - 适合对智能化要求较高的场景。

> 建议：初期可用本地规则或轻量模型，后续如需更强理解能力，可集成外部大模型API（如OpenAI GPT-3/4、Azure OpenAI等）。

## 1.3 使用spaCy训练意图识别模型（示例）

### 步骤一：准备训练数据
每条数据包含用户输入文本和意图标签。例如：
```python
TRAIN_DATA = [
    ("创建一个EC2实例", {"cats": {"create_ec2": 1.0, "delete_ec2": 0.0}}),
    ("删除EC2", {"cats": {"create_ec2": 0.0, "delete_ec2": 1.0}}),
    ("新建S3存储桶", {"cats": {"create_s3": 1.0, "delete_s3": 0.0}}),
    ("销毁S3 bucket", {"cats": {"create_s3": 0.0, "delete_s3": 1.0}}),
    # ...更多样本
]
```

### 步骤二：训练spaCy文本分类模型
```python
import spacy
from spacy.util import minibatch, compounding

nlp = spacy.blank("zh")  # 中文模型
textcat = nlp.add_pipe("textcat")
textcat.add_label("create_ec2")
textcat.add_label("delete_ec2")
textcat.add_label("create_s3")
textcat.add_label("delete_s3")

# 训练
for epoch in range(10):
    losses = {{}}
    batches = minibatch(TRAIN_DATA, size=compounding(4.0, 32.0, 1.5))
    for batch in batches:
        texts, annotations = zip(*batch)
        nlp.update(texts, annotations, losses=losses)
    print(losses)

nlp.to_disk("intent_model")  # 保存模型
```

### 步骤三：推理/预测
```python
nlp = spacy.load("intent_model")
doc = nlp("我要创建一个EC2实例")
print(doc.cats)  # 输出各意图概率
```

> 你可以根据实际云资源类型和操作扩展标签和样本。

## 2. 架构设计

### 2.1 总体架构
- **API层**：接收MCP请求，解析参数，返回标准MCP响应。
- **云资源适配层**：根据请求中的`cloud`参数，调用对应云平台（如AWS、Azure、GCP等）的SDK或API。
- **资源编排模块**：负责资源的创建、查询、删除等操作的业务逻辑。
- **扩展性设计**：采用插件/适配器模式，便于后续支持更多云平台。
- **日志与错误处理**：标准化日志输出和错误响应，便于排查和维护。

### 2.2 目录结构建议
```
ilyon_mcp/
├── api/                # MCP协议API实现（如FastAPI）
├── adapters/           # 各云平台适配器（如aws_adapter.py、azure_adapter.py）
├── orchestrator/       # 资源编排逻辑
├── utils/              # 工具类、日志、异常处理
├── tests/              # 单元测试
├── main.py             # 启动入口
└── requirements.txt    # 依赖
```

### 2.3 主要模块说明
- **api/**：实现MCP协议的RESTful接口，负责请求/响应格式校验。
- **adapters/**：每个云平台一个适配器，封装具体SDK调用逻辑。
- **orchestrator/**：根据MCP请求，调用适配器完成资源操作。
- **utils/**：日志、异常、配置等通用工具。

## 3. MCP Client调用方式

### 3.1 HTTP调用
MCP Client通过HTTP POST请求调用服务，发送标准MCP请求体，接收标准MCP响应。

#### 示例Python Client
```python
import requests

url = "http://localhost:8000/mcp"
payload = {
    "input": "创建一个AWS EC2实例",
    "context": {"user": "alice", "cloud": "aws"},
    "parameters": {"instance_type": "t2.micro", "region": "us-west-2"}
}
response = requests.post(url, json=payload)
print(response.json())
```

### 3.2 扩展支持
- 支持多云：只需在`context.cloud`中指定目标云平台。
- 支持多种资源类型：通过`input`和`parameters`灵活描述。

## 4. 实现建议
- 推荐使用FastAPI实现API层，便于开发和文档生成。
- AWS适配器可用`boto3`库实现。
- 设计统一的异常和日志处理机制。
- 预留接口，便于后续扩展到Azure、GCP等。

---
如需更详细的MCP协议文档或具体实现示例，可随时补充。
