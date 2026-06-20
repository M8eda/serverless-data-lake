import os
import sys
import aws_cdk as cdk

# Dynamically append deployment directory to sys.path to support root execution smoothly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from s3_stack          import S3DataLakeStack
from kinesis_stack     import KinesisFirehoseStack
from glue_stack        import GlueStack
from athena_stack      import AthenaStack
from lakeformation_stack import LakeFormationStack
from quicksight_stack  import QuickSightStack
from eventbridge_stack import EventBridgeStack

app = cdk.App()

# ---------------------------------------------------------------------------
# QuickSight user ARN — set this before deploying QuickSightStack.
# Option A (recommended): pass via CDK context:
#   cdk deploy --context quicksight_user_arn=arn:aws:quicksight:...
# Option B: set the QUICKSIGHT_USER_ARN environment variable.
# Find your ARN:
#   aws quicksight list-users --aws-account-id <id> --namespace default
# ---------------------------------------------------------------------------
quicksight_user_arn = (
    app.node.try_get_context("quicksight_user_arn")
    or os.environ.get("QUICKSIGHT_USER_ARN", "")
)

# 1. Storage Layer
s3_stack = S3DataLakeStack(app, "S3DataLakeStack")

# 2. Ingestion Layer
kinesis_stack = KinesisFirehoseStack(app, "KinesisFirehoseStack",
    raw_bucket=s3_stack.raw_bucket
)
# FIX 8: Kinesis depends on S3 being ready
kinesis_stack.add_dependency(s3_stack)

# 3. Glue ETL Layer
glue_stack = GlueStack(app, "GlueStack",
    raw_bucket=s3_stack.raw_bucket,
    curated_bucket=s3_stack.curated_bucket,
    aggregated_bucket=s3_stack.aggregated_bucket
)
# FIX 8: Glue depends on S3 buckets existing
glue_stack.add_dependency(s3_stack)

# 4. Analytics Query Layer
athena_stack = AthenaStack(app, "AthenaStack",
    curated_bucket=s3_stack.curated_bucket
)
# FIX 8: Athena depends on Glue catalog being populated
athena_stack.add_dependency(glue_stack)

# 5. Governance Layer
# FIX 6 + FIX 8: Pass glue_role_arn so Lake Formation registers the right principal
lakeformation_stack = LakeFormationStack(app, "LakeFormationStack",
    glue_role_arn=glue_stack.glue_role_arn
)
lakeformation_stack.add_dependency(glue_stack)

# 6. BI Visualization Layer
# FIX 7: Pass quicksight_user_arn (required for permissions on data source/set)
quicksight_stack = QuickSightStack(app, "QuickSightStack",
    athena_workgroup_name="CuratedAnalyticsWG",
    quicksight_user_arn=quicksight_user_arn
)
# FIX 8: QuickSight depends on Athena workgroup existing
quicksight_stack.add_dependency(athena_stack)

# 7. Orchestration Automation Layer
EventBridgeStack(app, "EventBridgeStack",
    transform_job_name=glue_stack.transform_job.ref,
    aggregate_job_name=glue_stack.aggregate_job.ref
)

app.synth()