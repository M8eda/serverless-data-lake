import aws_cdk as cdk
from aws_cdk import aws_athena as athena
from aws_cdk import aws_s3 as s3
from constructs import Construct

class AthenaStack(cdk.Stack):

    def __init__(self, scope: Construct, id: str, curated_bucket: s3.IBucket, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Isolated query-results prefix prevents metadata logs from polluting production parquet layers
        workgroup = athena.CfnWorkGroup(self, "AthenaWorkGroup",
            name="CuratedAnalyticsWG",
            work_group_configuration=athena.CfnWorkGroup.WorkGroupConfigurationProperty(
                # FIX 3: enforce_workgroup_configuration ensures clients cannot
                # override the output location and write results elsewhere
                enforce_workgroup_configuration=True,
                result_configuration=athena.CfnWorkGroup.ResultConfigurationProperty(
                    output_location=f"s3://{curated_bucket.bucket_name}/athena-query-results/"
                )
            )
        )

        query = athena.CfnNamedQuery(self, "SalesAggregationQuery",
            database="curated_db",
            query_string="SELECT region, SUM(sales) as total_sales FROM sales GROUP BY region;",
            work_group=workgroup.name,
            name="AggregateSalesByRegion"
        )

        cdk.CfnOutput(self, "AthenaWorkGroupName", value=workgroup.name)
        # FIX 3: query.ref resolves to the CloudFormation physical resource ID,
        # which is the correct cross-stack token for a CfnNamedQuery
        cdk.CfnOutput(self, "AthenaQueryRef", value=query.ref)