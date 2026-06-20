import aws_cdk as cdk
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_kms as kms
from constructs import Construct

class S3DataLakeStack(cdk.Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Dedicated KMS Customer Managed Key (CMK) for data-lake compliance
        self.lake_key = kms.Key(self, "DataLakeKey",
            enable_key_rotation=True,
            description="KMS Encryption Key for Serverless Data Lake Storage",
            # FIX 12: Allow key to be deleted when stack is destroyed in dev
            removal_policy=cdk.RemovalPolicy.DESTROY
        )

        # Raw Zone bucket
        self.raw_bucket = s3.Bucket(self, "RawDataBucket",
            versioned=True,
            encryption=s3.BucketEncryption.KMS,
            encryption_key=self.lake_key,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            enforce_ssl=True,
            # FIX 12: DESTROY + auto_delete_objects lets cdk destroy succeed
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            lifecycle_rules=[s3.LifecycleRule(
                transitions=[s3.Transition(
                    storage_class=s3.StorageClass.INTELLIGENT_TIERING,
                    transition_after=cdk.Duration.days(30)
                )]
            )]
        )

        # Curated Zone bucket
        self.curated_bucket = s3.Bucket(self, "CuratedDataBucket",
            versioned=True,
            encryption=s3.BucketEncryption.KMS,
            encryption_key=self.lake_key,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            enforce_ssl=True,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        # Aggregated Zone bucket
        self.aggregated_bucket = s3.Bucket(self, "AggregatedDataBucket",
            versioned=True,
            encryption=s3.BucketEncryption.KMS,
            encryption_key=self.lake_key,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            enforce_ssl=True,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        cdk.CfnOutput(self, "RawBucketName",        value=self.raw_bucket.bucket_name)
        cdk.CfnOutput(self, "CuratedBucketName",    value=self.curated_bucket.bucket_name)
        cdk.CfnOutput(self, "AggregatedBucketName", value=self.aggregated_bucket.bucket_name)