import aws_cdk as cdk
from aws_cdk import aws_glue as glue
from aws_cdk import aws_iam as iam
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_s3_deployment as s3_deploy
from constructs import Construct

class GlueStack(cdk.Stack):

    def __init__(self, scope: Construct, id: str,
                 raw_bucket: s3.IBucket,
                 curated_bucket: s3.IBucket,
                 aggregated_bucket: s3.IBucket,
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # FIX 5: Dedicated bucket for Glue scripts — keeps infrastructure
        # assets completely separate from the data lake zones
        self.scripts_bucket = s3.Bucket(self, "GlueScriptsBucket",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            enforce_ssl=True,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        glue_role = iam.Role(self, "GlueRole",
            assumed_by=iam.ServicePrincipal("glue.amazonaws.com")
        )
        glue_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSGlueServiceRole")
        )

        raw_bucket.grant_read(glue_role)
        curated_bucket.grant_read_write(glue_role)
        aggregated_bucket.grant_read_write(glue_role)
        # FIX 5: Glue role must also read scripts from the scripts bucket
        self.scripts_bucket.grant_read(glue_role)

        # FIX 5: Scripts now deploy to the dedicated scripts bucket
        script_deployment = s3_deploy.BucketDeployment(self, "DeployGlueScripts",
            sources=[s3_deploy.Source.asset("source/glue_jobs")],
            destination_bucket=self.scripts_bucket,
            destination_key_prefix="scripts/"
        )

        raw_database = glue.CfnDatabase(self, "RawDatabase",
            catalog_id=cdk.Aws.ACCOUNT_ID,
            database_input=glue.CfnDatabase.DatabaseInputProperty(
                name="raw_db",
                description="Database for incoming raw JSON stream structures"
            )
        )

        curated_database = glue.CfnDatabase(self, "CuratedDatabase",
            catalog_id=cdk.Aws.ACCOUNT_ID,
            database_input=glue.CfnDatabase.DatabaseInputProperty(
                name="curated_db",
                description="Database for curated parquet tables and aggregated KPIs"
            )
        )

        raw_crawler = glue.CfnCrawler(self, "RawCrawler",
            role=glue_role.role_arn,
            database_name="raw_db",
            targets={"s3Targets": [{"path": f"s3://{raw_bucket.bucket_name}/"}]}
        )
        raw_crawler.add_depends_on(raw_database)

        curated_crawler = glue.CfnCrawler(self, "CuratedCrawler",
            role=glue_role.role_arn,
            database_name="curated_db",
            targets={"s3Targets": [{"path": f"s3://{curated_bucket.bucket_name}/sales/"}]}
        )
        curated_crawler.add_depends_on(curated_database)

        aggregated_crawler = glue.CfnCrawler(self, "AggregatedCrawler",
            role=glue_role.role_arn,
            database_name="curated_db",
            targets={"s3Targets": [{"path": f"s3://{aggregated_bucket.bucket_name}/daily_sales_summary/"}]}
        )
        aggregated_crawler.add_depends_on(curated_database)

        # FIX 11: WorkerType + NumberOfWorkers explicitly set to minimum
        # viable config — prevents defaulting to 10 DPUs and unexpected cost
        self.transform_job = glue.CfnJob(self, "TransformRawToParquet",
            role=glue_role.role_arn,
            worker_type="G.1X",
            number_of_workers=2,
            command=glue.CfnJob.JobCommandProperty(
                name="glueetl",
                script_location=f"s3://{self.scripts_bucket.bucket_name}/scripts/transform_raw_to_parquet.py"
            ),
            default_arguments={
                "--job-language": "python",
                "--enable-metrics": "true",
                "--RAW_BUCKET": raw_bucket.bucket_name,
                "--CURATED_BUCKET": curated_bucket.bucket_name
            }
        )
        self.transform_job.node.add_dependency(script_deployment)

        self.aggregate_job = glue.CfnJob(self, "AggregateSales",
            role=glue_role.role_arn,
            worker_type="G.1X",
            number_of_workers=2,
            command=glue.CfnJob.JobCommandProperty(
                name="glueetl",
                script_location=f"s3://{self.scripts_bucket.bucket_name}/scripts/aggregate_sales.py"
            ),
            default_arguments={
                "--job-language": "python",
                "--enable-metrics": "true",
                "--CURATED_BUCKET": curated_bucket.bucket_name,
                "--AGGREGATED_BUCKET": aggregated_bucket.bucket_name
            }
        )
        self.aggregate_job.node.add_dependency(script_deployment)

        # Expose glue_role ARN for LakeFormationStack to register permissions
        self.glue_role_arn = glue_role.role_arn

        cdk.CfnOutput(self, "GlueScriptsBucketName",   value=self.scripts_bucket.bucket_name)
        cdk.CfnOutput(self, "GlueCrawlerName",         value=raw_crawler.ref)
        cdk.CfnOutput(self, "CuratedCrawlerName",      value=curated_crawler.ref)
        cdk.CfnOutput(self, "AggregatedCrawlerName",   value=aggregated_crawler.ref)
        cdk.CfnOutput(self, "GlueTransformJobName",    value=self.transform_job.ref)
        cdk.CfnOutput(self, "GlueAggregateJobName",    value=self.aggregate_job.ref)