from mcp.aws_adapter import AWSAdapter
from mcp.intent import IntentRecognizer

ADAPTERS = {
    'aws': AWSAdapter(),
}

INTENT_METHOD_MAP = {
    'create_ec2': 'create_ec2',
    'delete_ec2': 'delete_ec2',
}

class Orchestrator:
    def __init__(self):
        self.intent_recognizer = IntentRecognizer()

    def handle(self, mcp_input, context, parameters):
        intent, intent_scores = self.intent_recognizer.recognize(mcp_input)
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
