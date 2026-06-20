import base64
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    """
    Decodes, transforms, and normalizes incoming real-time JSON events.
    Guarantees structural safety by handling null inputs and malformed payload events.
    """
    output_records = []
    
    for record in event.get('records', []):
        record_id = record['recordId']
        try:
            # Decode payload safely from Base64
            payload_bytes = base64.b64decode(record['data'])
            payload_str = payload_bytes.decode('utf-8').strip()
            
            if not payload_str:
                logger.warning(f"Record {record_id} contains an empty payload. Skipping.")
                output_records.append({
                    'recordId': record_id,
                    'result': 'Dropped',
                    'data': record['data']
                })
                continue
                
            data = json.loads(payload_str)
            
            # Normalize core schema parameters to lowercase keys
            normalized_data = {k.lower(): v for k, v in data.items()}
            
            # Re-encode clean payload back to base64 with a clean newline delimiter
            output_data_str = json.dumps(normalized_data) + "\n"
            output_data_bytes = output_data_str.encode('utf-8')
            output_data_base64 = base64.b64encode(output_data_bytes).decode('utf-8')
            
            output_records.append({
                'recordId': record_id,
                'result': 'Ok',
                'data': output_data_base64
            })
            
        except (json.JSONDecodeError, KeyError, Exception) as err:
            logger.error(f"Failed to transform stream record {record_id}. Error: {str(err)}")
            # Route broken data records to error state without halting pipeline execution
            output_records.append({
                'recordId': record_id,
                'result': 'ProcessingFailed',
                'data': record['data']
            })
            
    logger.info(f"Successfully processed {len(output_records)} records for Firehose delivery.")
    return {'records': output_records}
