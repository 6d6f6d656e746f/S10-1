import boto3
import json

def lambda_handler(event, context):
    print(event)
    body = event.get('body', {})
    tenant_id = body.get('tenant_id') if isinstance(body, dict) else None
    producto_id = body.get('producto_id') if isinstance(body, dict) else None
    updates = body.get('updates') if isinstance(body, dict) else None

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

    if not tenant_id or not producto_id or not updates:
        return {
            'statusCode': 400,
            'body': 'Falta tenant_id, producto_id o updates'
        }

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('t_productos')

    # Construir UpdateExpression
    expr_parts = []
    expr_values = {}
    for i, (k, v) in enumerate(updates.items()):
        placeholder = ':v' + str(i)
        expr_parts.append(f"{k} = {placeholder}")
        expr_values[placeholder] = v

    update_expr = 'SET ' + ', '.join(expr_parts)

    key = {'producto_id': producto_id, 'tenant_id': tenant_id}
    response = table.update_item(
        Key=key,
        UpdateExpression=update_expr,
        ExpressionAttributeValues=expr_values,
        ReturnValues='ALL_NEW'
    )

    return {'statusCode':200, 'body': response.get('Attributes')}
