import aws_cdk as cdk
from aws_cdk import aws_lakeformation as lakeformation
from aws_cdk import aws_iam as iam
from constructs import Construct

class LakeFormationStack(cdk.Stack):

    def __init__(self, scope: Construct, id: str,
                 glue_role_arn: str,
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Admin role for Lake Formation console / human access
        admin_role = iam.Role(self, "LakeFormationAdminRole",
            assumed_by=iam.AccountRootPrincipal()
        )

        # Bootstraps the account context with required administrative principal definitions
        lakeformation.CfnDataLakeSettings(self, "DataLakeSettings",
            admins=[lakeformation.CfnDataLakeSettings.DataLakePrincipalProperty(
                data_lake_principal_identifier=admin_role.role_arn
            )]
        )

        # FIX 6: Grant the ACTUAL Glue ETL role access to curated_db.
        # Previously this was granting the admin_role which nothing assumes
        # during ETL — Glue jobs would get Access Denied even with IAM allowing it.
        glue_db_permissions = lakeformation.CfnPermissions(self, "GlueRoleDBPermissions",
            data_lake_principal=lakeformation.CfnPermissions.DataLakePrincipalProperty(
                data_lake_principal_identifier=glue_role_arn
            ),
            resource=lakeformation.CfnPermissions.ResourceProperty(
                database_resource=lakeformation.CfnPermissions.DatabaseResourceProperty(
                    name="curated_db"
                )
            ),
            permissions=["SELECT", "DESCRIBE", "ALTER", "CREATE_TABLE"]
        )

        # Also grant admin role for console/manual queries
        admin_db_permissions = lakeformation.CfnPermissions(self, "AdminRoleDBPermissions",
            data_lake_principal=lakeformation.CfnPermissions.DataLakePrincipalProperty(
                data_lake_principal_identifier=admin_role.role_arn
            ),
            resource=lakeformation.CfnPermissions.ResourceProperty(
                database_resource=lakeformation.CfnPermissions.DatabaseResourceProperty(
                    name="curated_db"
                )
            ),
            permissions=["SELECT", "DESCRIBE"]
        )

        cdk.CfnOutput(self, "LakeFormationAdminRoleArn", value=admin_role.role_arn)