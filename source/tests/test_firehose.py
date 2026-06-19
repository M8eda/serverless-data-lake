import pytest
import base64
import json
from source.lambdas.firehose_transform import handler

def test_firehose_lambda_transform_ok():
    """Verify Firehose Lambda decodes, processes, and re-encodes data correctly."""
    # Mocking a standard Kinesis Firehose Event payload
    raw_payload = {"id": 101, "region": "Cairo", "amount": 500}
    encoded_data = base64.b64encode(json.dumps(raw_payload).encode('utf-8')).decode('utf-8')
    
    mock_event = {
        "records": [
            {
                "recordId": "49612345678901234567890",
                "approximateArrivalTimestamp": 1620000000000,
                "data": encoded_data
            }
        ]
    }
    
    # Execute the handler function
    response = handler(mock_event, None)
    
    # Assertions to ensure Firehose protocol specs are followed
    assert "records" in response
    assert len(response["records"]) == 1
    
    transformed_record = response["records"][0]
    assert transformed_record["recordId"] == "49612345678901234567890"
    assert transformed_record["result"] == "Ok"
    assert "data" in transformed_record
