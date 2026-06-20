import aws_cdk as cdk
from aws_cdk import aws_quicksight as quicksight
from constructs import Construct

class QuickSightStack(cdk.Stack):

    def __init__(self, scope: Construct, id: str,
                 athena_workgroup_name: str,
                 quicksight_user_arn: str,
                 **kwargs) -> None:
        """
        Parameters
        ----------
        athena_workgroup_name : str
            Name of the Athena workgroup to connect to.
        quicksight_user_arn : str
            ARN of the QuickSight user who will own the data source and dataset.
            Format: arn:aws:quicksight:<region>:<account-id>:user/default/<username>
            Find yours in the QuickSight console under Manage QuickSight > Users,
            or run: aws quicksight list-users --aws-account-id <id> --namespace default
        """
        super().__init__(scope, id, **kwargs)

        # FIX 7: permissions is REQUIRED — without it the resources deploy but
        # are invisible to every user in the QuickSight console
        datasource_permissions = [
            quicksight.CfnDataSource.ResourcePermissionProperty(
                principal=quicksight_user_arn,
                actions=[
                    "quicksight:DescribeDataSource",
                    "quicksight:DescribeDataSourcePermissions",
                    "quicksight:PassDataSource",
                    "quicksight:UpdateDataSource",
                    "quicksight:DeleteDataSource",
                    "quicksight:UpdateDataSourcePermissions"
                ]
            )
        ]

        dataset_permissions = [
            quicksight.CfnDataSet.ResourcePermissionProperty(
                principal=quicksight_user_arn,
                actions=[
                    "quicksight:DescribeDataSet",
                    "quicksight:DescribeDataSetPermissions",
                    "quicksight:PassDataSet",
                    "quicksight:DescribeIngestion",
                    "quicksight:ListIngestions",
                    "quicksight:UpdateDataSet",
                    "quicksight:DeleteDataSet",
                    "quicksight:CreateIngestion",
                    "quicksight:CancelIngestion",
                    "quicksight:UpdateDataSetPermissions"
                ]
            )
        ]

        datasource = quicksight.CfnDataSource(self, "AthenaDataSource",
            aws_account_id=cdk.Aws.ACCOUNT_ID,
            data_source_id="athena-sales-source",
            name="AthenaSalesSource",
            type="ATHENA",
            permissions=datasource_permissions,
            data_source_parameters=quicksight.CfnDataSource.DataSourceParametersProperty(
                athena_parameters=quicksight.CfnDataSource.AthenaParametersProperty(
                    work_group=athena_workgroup_name
                )
            )
        )

        dataset = quicksight.CfnDataSet(self, "SalesDataSet",
            aws_account_id=cdk.Aws.ACCOUNT_ID,
            data_set_id="athena-sales-dataset",
            name="AthenaSalesDataSet",
            import_mode="DIRECT_QUERY",
            permissions=dataset_permissions,
            physical_table_map={
                "SalesTable": quicksight.CfnDataSet.PhysicalTableProperty(
                    relational_table=quicksight.CfnDataSet.RelationalTableProperty(
                        data_source_arn=datasource.attr_arn,
                        catalog="AWSDataCatalog",
                        schema="curated_db",
                        name="sales",
                        input_columns=[
                            quicksight.CfnDataSet.InputColumnProperty(name="id",     type="STRING"),
                            quicksight.CfnDataSet.InputColumnProperty(name="region", type="STRING"),
                            quicksight.CfnDataSet.InputColumnProperty(name="sales",  type="DECIMAL")
                        ]
                    )
                )
            },
            logical_table_map={
                "SalesTableLogical": quicksight.CfnDataSet.LogicalTableProperty(
                    alias="SalesData",
                    source=quicksight.CfnDataSet.LogicalTableSourceProperty(
                        physical_table_id="SalesTable"
                    )
                )
            }
        )
        dataset.add_depends_on(datasource)

        cdk.CfnOutput(self, "QuickSightDataSourceArn", value=datasource.attr_arn)
        cdk.CfnOutput(self, "QuickSightDataSetArn",    value=dataset.attr_arn)