import base64
import json

def handler(event, context):
    """AWS Lambda handler for Kinesis Firehose processing."""
    output = []
    
    for record in event.get('records', []):
        record_id = record['recordId']
        
        # 1. Decode the base64 data from Firehose
        payload = base64.b64decode(record['data']).decode('utf-8')
        data = json.loads(payload)
        
        # 2. Perform a transformation (e.g., uppercase the region)
        if 'region' in data:
            data['region'] = data['region'].upper()
            
        # 3. Re-encode the data back to base64
        transformed_data = base64.b64encode(json.dumps(data).encode('utf-8')).decode('utf-8')
        
        # 4. Construct the required Firehose response structure
        output.append({
            'recordId': record_id,
            'result': 'Ok',
            'data': transformed_data
        })
        
    return {'records': output}
