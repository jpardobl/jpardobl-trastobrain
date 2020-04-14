
import boto3
                

AWS_PROFILE='jpardo'
def get_aws_session(profile_name=None, region_name='eu-west-1'):
    return boto3.session.Session(
        profile_name=profile_name,
        region_name=region_name)
        
        
def create_or_get_fifo_queue(name, session):

    name = f"{name}.fifo"
    sqs = session.resource("sqs")
    queue = None
    try:
        queue = sqs.get_queue_by_name(QueueName=name)
    except Exception as ex:
        queue = sqs.create_queue(
            QueueName=name, 
            Attributes={'FifoQueue':'true', 'ContentBasedDeduplication': 'false'})
    finally:
        return queue

def delete_queue(queue_name, session):
    session.resource("sqs").sqs.get_queue_by_name(QueueName=queue_name).delete()

        