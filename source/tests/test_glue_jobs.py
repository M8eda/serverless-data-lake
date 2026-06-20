import sys
from unittest.mock import MagicMock

sys.modules['pyspark'] = MagicMock()
sys.modules['pyspark.context'] = MagicMock()
sys.modules['pyspark.sql'] = MagicMock()
sys.modules['pyspark.sql.types'] = MagicMock()
sys.modules['aws_glue'] = MagicMock()
sys.modules['aws_glue.utils'] = MagicMock()
sys.modules['aws_glue.context'] = MagicMock()
sys.modules['aws_glue.job'] = MagicMock()

from source.glue_jobs.transform_raw_to_parquet import transform_dataframe
from source.glue_jobs.aggregate_sales import compute_aggregations

def test_transform_dataframe_logic():
    """Verify that transformation handles schema configurations without exceptions."""
    mock_df = MagicMock()
    mock_df.columns = ["id", "region", "amount"]
    
    result_df = transform_dataframe(mock_df)
    assert result_df is not None
    assert mock_df.withColumnRenamed.called

def test_aggregate_logic():
    """Verify aggregation structuring sets up grouping parameters properly."""
    mock_df = MagicMock()
    mock_df.columns = ["region", "sales"]
    
    result_df = compute_aggregations(mock_df)
    assert result_df is not None
    assert mock_df.groupBy.called
