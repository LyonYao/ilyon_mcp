from fastapi import APIRouter

router = APIRouter()

@router.get("/capabilities")
def get_capabilities():
    """
    返回MCP服务支持的所有资源类型、操作和参数说明，便于AI自动发现和集成。
    """
    return {
        "input_format": "input字段必须为{'action': 'create', 'resource': 'aws_s3_bucket'} 或 intent字符串如 create_s3。推荐结构化action+resource。",
        "resources": [
            {
                "type": "aws_s3_bucket",
                "desc": "AWS S3存储桶，用于对象存储。可用于存储和管理文件、图片、备份等。",
                "actions": [
                    {"name": "create", "desc": "创建一个新的S3存储桶"},
                    {"name": "delete", "desc": "删除指定的S3存储桶"}
                ],
                "parameters": [
                    {"name": "bucket_name", "type": "string", "required": True, "desc": "S3存储桶名称"},
                    {"name": "region", "type": "string", "required": False, "desc": "区域"}
                ],
                "example": {
                    "input": {"action": "create", "resource": "aws_s3_bucket"},
                    "parameters": {"bucket_name": "test-bucket", "region": "us-west-2"}
                }
            },
            {
                "type": "aws_ec2_instance",
                "desc": "AWS EC2云主机实例，用于弹性计算和运行应用。",
                "actions": [
                    {"name": "create", "desc": "创建一台新的EC2实例"},
                    {"name": "delete", "desc": "删除指定的EC2实例"}
                ],
                "parameters": [
                    {"name": "instance_type", "type": "string", "required": True, "desc": "实例类型"},
                    {"name": "region", "type": "string", "required": True, "desc": "区域"},
                    {"name": "image_id", "type": "string", "required": False, "desc": "AMI镜像ID"},
                    {"name": "instance_id", "type": "string", "required": False, "desc": "实例ID（删除时必需）"}
                ],
                "example": {
                    "input": {"action": "create", "resource": "aws_ec2_instance"},
                    "parameters": {"instance_type": "t2.micro", "region": "us-west-2", "image_id": "ami-xxx"}
                }
            }
        ]
    }
