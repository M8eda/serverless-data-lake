import sys
from pyspark.context import SparkContext
from aws_glue.context import GlueContext
from aws_glue.job import Job
from aws_glue.utils import getResolvedOptions
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

    curated_path = f"s3://{args['CURATED_BUCKET']}/sales/"
    aggregated_path = f"s3://{args['AGGREGATED_BUCKET']}/daily_sales_summary/"

    df_curated = spark.read.parquet(curated_path)
    df_aggregated = compute_aggregations(df_curated)

    df_aggregated.write \
        .mode("overwrite") \
        .parquet(aggregated_path)

    job.commit()
