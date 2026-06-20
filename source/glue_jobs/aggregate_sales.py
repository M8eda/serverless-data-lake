import sys
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.sql import functions as F

def compute_aggregations(df):
    """
    Aggregates metrics by region.
    Separated out to allow fast mock testing without cluster dependencies.
    """
    if "region" in df.columns and "sales" in df.columns:
        return df.groupBy("region").agg(F.sum("sales").alias("total_sales"))
    return df

if __name__ == "__main__":
    args = getResolvedOptions(sys.argv, ['JOB_NAME', 'CURATED_BUCKET', 'AGGREGATED_BUCKET'])

    sc = SparkContext()
    glueContext = GlueContext(sc)
    spark = glueContext.spark_session
    job = Job(glueContext)
    job.init(args['JOB_NAME'], args)

    curated_path    = f"s3://{args['CURATED_BUCKET']}/sales/"
    aggregated_path = f"s3://{args['AGGREGATED_BUCKET']}/daily_sales_summary/"

    df_curated = spark.read.parquet(curated_path)

    # FIX 10: Guard against empty curated data (e.g. first run or failed transform)
    if df_curated.rdd.isEmpty():
        print("No records found in curated bucket. Exiting gracefully.")
        job.commit()
        sys.exit(0)

    df_aggregated = compute_aggregations(df_curated)

    df_aggregated.write \
        .mode("overwrite") \
        .parquet(aggregated_path)

    job.commit()