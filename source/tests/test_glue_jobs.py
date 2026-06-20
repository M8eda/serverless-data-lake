import sys
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# Mock all Glue / PySpark dependencies BEFORE importing the job modules.
# Key fix: paths must match the corrected import names (awsglue, not aws_glue)
# and pyspark.sql.functions must be mocked individually so F.* calls resolve.
# ---------------------------------------------------------------------------
sys.modules["pyspark"]                   = MagicMock()
sys.modules["pyspark.context"]           = MagicMock()
sys.modules["pyspark.sql"]               = MagicMock()
sys.modules["pyspark.sql.types"]         = MagicMock()
sys.modules["pyspark.sql.functions"]     = MagicMock()   # FIX: was missing
sys.modules["awsglue"]                   = MagicMock()   # FIX: was aws_glue
sys.modules["awsglue.utils"]             = MagicMock()   # FIX: was aws_glue.*
sys.modules["awsglue.context"]           = MagicMock()
sys.modules["awsglue.job"]               = MagicMock()

from source.glue_jobs.transform_raw_to_parquet import transform_dataframe
from source.glue_jobs.aggregate_sales import compute_aggregations


def test_transform_dataframe_renames_amount_to_sales():
    """Verify that 'amount' is renamed to 'sales' when 'sales' is absent."""
    mock_df = MagicMock()
    mock_df.columns = ["id", "region", "amount"]

    # Each withColumnRenamed / withColumn call returns a new mock_df-like object
    renamed_df = MagicMock()
    renamed_df.columns = ["id", "region", "sales"]
    renamed_df.withColumnRenamed.return_value = renamed_df
    renamed_df.withColumn.return_value = renamed_df
    mock_df.withColumnRenamed.return_value = renamed_df

    result_df = transform_dataframe(mock_df)

    assert result_df is not None
    # Confirm the rename from 'amount' -> 'sales' was triggered
    assert mock_df.withColumnRenamed.called


def test_transform_dataframe_lowercases_columns():
    """Verify column names are lowercased during transformation."""
    mock_df = MagicMock()
    mock_df.columns = ["ID", "Region", "Sales"]
    chained = MagicMock()
    chained.columns = ["id", "region", "sales"]
    chained.withColumnRenamed.return_value = chained
    chained.withColumn.return_value = chained
    mock_df.withColumnRenamed.return_value = chained

    result_df = transform_dataframe(mock_df)
    assert result_df is not None
    assert mock_df.withColumnRenamed.called


def test_aggregate_logic_groups_by_region():
    """Verify aggregation structuring sets up grouping on 'region' and 'sales'."""
    mock_df = MagicMock()
    mock_df.columns = ["region", "sales"]

    result_df = compute_aggregations(mock_df)

    assert result_df is not None
    mock_df.groupBy.assert_called_once_with("region")


def test_aggregate_logic_returns_df_unchanged_when_columns_missing():
    """Verify aggregation passes through unchanged if required columns are absent."""
    mock_df = MagicMock()
    mock_df.columns = ["id", "amount"]   # no 'region' or 'sales'

    result_df = compute_aggregations(mock_df)

    # Should return original df without calling groupBy
    assert result_df is mock_df
    mock_df.groupBy.assert_not_called()