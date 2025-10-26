import boto3
import json

def lambda_handler(event, context):
    print(event)
    body = event.get('body', {})
    tenant_id = body.get('tenant_id') if isinstance(body, dict) else None
    producto_id = body.get('producto_id') if isinstance(body, dict) else None

    # Proteger
    token = event.get('headers', {}).get('Authorization')
    lambda_client = boto3.client('lambda')
    payload_string = '{ "token": "' + (token or '') + '" }'
    invoke_response = lambda_client.invoke(FunctionName="ValidarTokenAcceso",
                                           InvocationType='RequestResponse',
                                           Payload = payload_string)
    response = json.loads(invoke_response['Payload'].read())
    print(response)
    if response.get('statusCode') == 403:
        return {
            'statusCode' : 403,
            'status' : 'Forbidden - Acceso No Autorizado'
        }

    if not tenant_id or not producto_id:
        return {
            'statusCode': 400,
            'body': 'Falta tenant_id o producto_id'
        }

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('t_productos')
    key = {'producto_id': producto_id, 'tenant_id': tenant_id}
    response = table.delete_item(Key=key)

    return {'statusCode':200, 'body': response}
