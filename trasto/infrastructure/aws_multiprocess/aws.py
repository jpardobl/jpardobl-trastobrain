
import boto3
                
AWS_REGION='eu-west-1'
AWS_PROFILE='jpardo'

TAREAS_NORMALES_QUEUE_NAME = "trastobrain_tareas_normales"
TAREAS_PRIORITARIAS_QUEUE_NAME = "trastobrain_tareas_prioritarias"
COMANDOS_QUEUE_NAME = "trastobrain_comandos"
EVENTOS_QUEUE_NAME = "trastobrain_eventos"

TABLE_ACCIONES_NAME="trastobrain_accionews"
KEY_SCHEMA_ACCIONES=[
    {
        'AttributeName': 'idd',
        'KeyType': 'HASH'  #Partition key
    },
    {
        'AttributeName': 'tipo',
        'KeyType': 'RANGE'  #Sort key
    }]
ATTRIBUTES_ACCIONES=[
    {
        'AttributeName': 'idd',
        'AttributeType': 'S'
    },
    {
        'AttributeName': 'tipo',
        'AttributeType': 'S'
    }]
READ_CAPACITY_UNITS=5
PROVISIONED_THROUGHTPUT=5


def get_aws_session(profile_name=AWS_PROFILE, region_name=AWS_REGION):
    return boto3.session.Session(profile_name=profile_name, region_name=region_name)


def create_fifo_queue(name):
    sqs = get_aws_session().resource("sqs")
    return sqs.create_queue(
        QueueName=f"{name}.fifo", 
        Attributes={'FifoQueue':'true', 'ContentBasedDeduplication': 'false'})


def delete_queue(queue_name):
    get_aws_session().resource("sqs").get_queue_by_name(QueueName=f"{queue_name}.fifo").delete()


def get_queue(queue_name):
    return get_aws_session().resource("sqs").get_queue_by_name(QueueName=f"{queue_name}.fifo")


def create_dynamodb_acciones_table():
    dynamodb = get_aws_session().resource('dynamodb')

    return dynamodb.create_table(
        TableName=TABLE_ACCIONES_NAME,
        KeySchema=KEY_SCHEMA_ACCIONES,
        AttributeDefinitions=ATTRIBUTES_ACCIONES,
        ProvisionedThroughput={
            'ReadCapacityUnits': READ_CAPACITY_UNITS,
            'WriteCapacityUnits': PROVISIONED_THROUGHTPUT
        }
    )


def delete_acciones_table():
    get_aws_session().resource('dynamodb').Table(TABLE_ACCIONES_NAME).delete()


def get_dynamodb_acciones_table():
    table = get_aws_session().resource('dynamodb').Table(TABLE_ACCIONES_NAME)
    table.load()
    return table


def create_queues():
    create_fifo_queue(EVENTOS_QUEUE_NAME)
    create_fifo_queue(TAREAS_NORMALES_QUEUE_NAME)
    create_fifo_queue(TAREAS_PRIORITARIAS_QUEUE_NAME)
    create_fifo_queue(COMANDOS_QUEUE_NAME)

if __name__ == "__main__":
    create_queues()
    create_dynamodb_acciones_table()