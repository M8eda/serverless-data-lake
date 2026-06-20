import aws_cdk as cdk
from aws_cdk import aws_kinesisfirehose as firehose
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_iam as iam
from aws_cdk import aws_s3 as s3
from constructs import Construct

class KinesisFirehoseStack(cdk.Stack):

    def __init__(self, scope: Construct, id: str, raw_bucket: s3.IBucket, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        firehose_lambda = lambda_.Function(self, "FirehoseTransformLambda",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="firehose_transform.handler",
            code=lambda_.Code.from_asset("source/lambdas"),
            timeout=cdk.Duration.minutes(3)
        )

        firehose_role = iam.Role(self, "FirehoseDeliveryRole",
            assumed_by=iam.ServicePrincipal("firehose.amazonaws.com")
        )

        raw_bucket.grant_read_write(firehose_role)
        firehose_lambda.grant_invoke(firehose_role)

        self.delivery_stream = firehose.CfnDeliveryStream(self, "RawJsonDeliveryStream",
            delivery_stream_name="RawJsonDeliveryStream",
            delivery_stream_type="DirectPut",
            extended_s3_destination_configuration=firehose.CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty(
                bucket_arn=raw_bucket.bucket_arn,
                role_arn=firehose_role.role_arn,
                buffering_hints=firehose.CfnDeliveryStream.BufferingHintsProperty(
                    interval_in_seconds=60,
                    size_in_mbs=1
                ),
                compression_format="UNCOMPRESSED",
                processing_configuration=firehose.CfnDeliveryStream.ProcessingConfigurationProperty(
                    enabled=True,
                    processors=[
                        firehose.CfnDeliveryStream.ProcessorProperty(
                            type="Lambda",
                            parameters=[
                                firehose.CfnDeliveryStream.ProcessorParameterProperty(
                                    parameter_name="LambdaArn",
                                    parameter_value=firehose_lambda.function_arn
                                ),
                                firehose.CfnDeliveryStream.ProcessorParameterProperty(
                                    parameter_name="NumberOfRetries",
                                    parameter_value="3"
                                )
                            ]
                        )
                    ]
                )
            )
        )

        cdk.CfnOutput(self, "FirehoseStreamName", value=self.delivery_stream.ref)
