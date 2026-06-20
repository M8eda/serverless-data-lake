import sys
import pytest
from unittest.mock import MagicMock

# Import route fixed to look inside 'source.lambdas'
from source.lambdas.firehose_transform import handler

@pytest.fixture
def mock_context():
    return MagicMock()

def test_handler_successful_transformation(mock_context):
    raw_payload = '{"id": "101", "region": "North", "Amount": 450.50}'
    import base64
    encoded_payload = base64.b64encode(raw_payload.encode('utf-8')).decode('utf-8')
    
    mock_event = {
        "records": [
            {
                "recordId": "record1",
                "data": encoded_payload
            }
        ]
    }
    
    response = handler(mock_event, mock_context)
    
    assert "records" in response
    assert len(response["records"]) == 1
    assert response["records"][0]["result"] == "Ok"
    
    decoded_output = base64.b64decode(response["records"][0]["data"]).decode('utf-8')
    assert "amount" in decoded_output  # Verifies downcasing normalization
