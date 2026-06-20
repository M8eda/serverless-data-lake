import sys
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.sql.types import DecimalType
from pyspark.sql import functions as F

def transform_dataframe(df):
    """
    Standardizes schema structure by converting 'amount' keys to 'sales'.
    Enforces unified decimal specifications for accurate transactional metrics.
    """
    # Cast all schema properties to lowercase to prevent casing mismatches
    for col_name in df.columns:
        df = df.withColumnRenamed(col_name, col_name.lower())

    # Standardize column naming variations across raw files
    if "amount" in df.columns and "sales" not in df.columns:
        df = df.withColumnRenamed("amount", "sales")

    # Enforce safe data fallback defaults for missing metrics
    if "sales" in df.columns:
        df = df.withColumn("sales", F.coalesce(df["sales"].cast(DecimalType(12, 2)), F.lit(0.00)))
    else:
        df = df.withColumn("sales", F.lit(0.00).cast(DecimalType(12, 2)))

    return df

if __name__ == "__main__":
    args = getResolvedOptions(sys.argv, ['JOB_NAME', 'RAW_BUCKET', 'CURATED_BUCKET'])

    sc = SparkContext()
    glueContext = GlueContext(sc)
    spark = glueContext.spark_session
    job = Job(glueContext)
    job.init(args['JOB_NAME'], args)

    raw_path     = f"s3://{args['RAW_BUCKET']}/"
    curated_path = f"s3://{args['CURATED_BUCKET']}/sales/"

    datasource = glueContext.create_dynamic_frame.from_options(
        connection_type="s3",
        connection_options={"paths": [raw_path]},
        format="json"
    )

    df = datasource.toDF()
    if df.rdd.isEmpty():
        print("No records found in raw bucket. Exiting gracefully.")
        job.commit()
        sys.exit(0)

    transformed_df = transform_dataframe(df)

    transformed_df.write \
        .mode("append") \
        .partitionBy("region") \
        .parquet(curated_path)

    job.commit()