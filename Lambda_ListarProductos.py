import boto3
import json

def lambda_handler(event, context):
    print(event)
    # Entrada
    body = event.get('body', {})
    tenant_id = body.get('tenant_id') if isinstance(body, dict) else None

    # Inicio - Proteger el Lambda
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
    # Fin - Proteger el Lambda

    if not tenant_id:
        return {
            'statusCode': 400,
            'body': 'Falta tenant_id'
        }

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('t_productos')
    # Asumimos que los items tienen atributo tenant_id
    response = table.scan(
        FilterExpression='tenant_id = :t',
        ExpressionAttributeValues={':t': tenant_id}
    )

    return {
        'statusCode': 200,
        'body': response.get('Items', [])
    }
