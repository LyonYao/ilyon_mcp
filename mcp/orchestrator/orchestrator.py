from mcp.adapters.aws_adapter import AWSAdapter
from mcp.utils.intent import IntentRecognizer
import json

ADAPTERS = {
    'aws': AWSAdapter(),
}

INTENT_METHOD_MAP = {
    'create_ec2': 'create_ec2',
    'delete_ec2': 'delete_ec2',
    'create_s3': 'create_s3',
    'delete_s3': 'delete_s3',
    'create_s3_bucket': 'create_s3',
    'delete_s3_bucket': 'delete_s3',
    'create_bucket': 'create_s3',
    'delete_bucket': 'delete_s3',
}

class Orchestrator:
    def __init__(self):
        self.intent_recognizer = IntentRecognizer()

    def handle(self, mcp_input, context, parameters):
        print(f"[DEBUG] mcp_input: {mcp_input}")
        # 只支持结构化/标准intent，不再调用spaCy
        intent = None
        # 1. dict结构
        if isinstance(mcp_input, dict):
            intent = mcp_input.get("intent")
            if not intent:
                action = mcp_input.get("action")
                # 兼容 resource_type 字段
                resource = mcp_input.get("resource") or mcp_input.get("resource_type")
                if action and resource:
                    resource_short = resource.split("_")[-1]
                    intent = f"{action}_{resource_short}"
        # 2. str结构
        elif isinstance(mcp_input, str):
            # 2.1 尝试json解析
            try:
                mcp_dict = json.loads(mcp_input)
                intent = mcp_dict.get("intent")
                if not intent:
                    action = mcp_dict.get("action")
                    resource = mcp_dict.get("resource") or mcp_dict.get("resource_type")
                    if action and resource:
                        resource_short = resource.split("_")[-1]
                        intent = f"{action}_{resource_short}"
            except Exception:
                # 2.2 如果是已知intent字符串，直接用
                if mcp_input in INTENT_METHOD_MAP:
                    intent = mcp_input
        # 兜底：不再调用spaCy

        # 自动补全通用intent（如create/delete），支持parameters中type字段
        if intent in ("create", "delete"):
            resource_type = parameters.get("type")
            if resource_type == "aws_s3_bucket":
                intent = f"{intent}_s3"
            elif resource_type == "aws_ec2_instance":
                intent = f"{intent}_ec2"
            elif "bucket_name" in parameters:
                intent = f"{intent}_s3"
            elif "instance_type" in parameters:
                intent = f"{intent}_ec2"

        # intent归一化，兼容大模型/AI常见输出
        intent_map_alias = {
            'create_bucket': 'create_s3',
            'delete_bucket': 'delete_s3',
            'create_s3_bucket': 'create_s3',
            'delete_s3_bucket': 'delete_s3',
        }
        if intent in intent_map_alias:
            intent = intent_map_alias[intent]

        # intent兜底校验
        if not intent:
            return {"output": None, "status": "error", "error": "未能识别意图，请检查AI返回内容或输入格式"}

        cloud = context.get('cloud', 'aws')
        adapter = ADAPTERS.get(cloud)
        if not adapter:
            return {"output": None, "status": "error", "error": f"不支持的云平台: {cloud}"}
        method_name = INTENT_METHOD_MAP.get(intent)
        if not method_name or not hasattr(adapter, method_name):
            return {"output": None, "status": "error", "error": f"不支持的操作: {intent}"}
        try:
            result = getattr(adapter, method_name)(parameters)
            return {"output": result, "status": "success", "error": None}
        except Exception as e:
            return {"output": None, "status": "error", "error": str(e)}
