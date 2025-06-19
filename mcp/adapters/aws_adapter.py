import boto3

class AWSAdapter:
    def create_ec2(self, params):
        ec2 = boto3.resource('ec2', region_name=params.get('region', 'us-west-2'))
        instances = ec2.create_instances(
            ImageId=params.get('image_id', 'ami-0c94855ba95c71c99'),
            MinCount=1,
            MaxCount=1,
            InstanceType=params.get('instance_type', 't2.micro')
        )
        return f"EC2实例已创建，ID: {instances[0].id}"

    def delete_ec2(self, params):
        ec2 = boto3.resource('ec2', region_name=params.get('region', 'us-west-2'))
        instance_id = params.get('instance_id')
        if not instance_id:
            return "缺少instance_id参数"
        instance = ec2.Instance(instance_id)
        instance.terminate()
        return f"EC2实例已销毁，ID: {instance_id}"

    def create_s3_bucket(self, params):
        s3 = boto3.client('s3', region_name=params.get('region', 'us-west-2'))
        bucket_name = params.get('bucket_name')
        if not bucket_name:
            return "缺少bucket_name参数"
        region = params.get('region', 'us-west-2')
        try:
            if region == 'us-east-1':
                s3.create_bucket(Bucket=bucket_name)
            else:
                s3.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': region}
                )
            return f"S3存储桶已创建，名称: {bucket_name}"
        except Exception as e:
            return f"创建S3存储桶失败: {str(e)}"

    def delete_s3_bucket(self, params):
        s3 = boto3.resource('s3', region_name=params.get('region', 'us-west-2'))
        bucket_name = params.get('bucket_name')
        if not bucket_name:
            return "缺少bucket_name参数"
        try:
            bucket = s3.Bucket(bucket_name)
            # 先清空bucket内容
            bucket.objects.all().delete()
            bucket.delete()
            return f"S3存储桶已删除，名称: {bucket_name}"
        except Exception as e:
            return f"删除S3存储桶失败: {str(e)}"
