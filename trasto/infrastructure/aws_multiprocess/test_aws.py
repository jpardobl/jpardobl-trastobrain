
import time

from trasto.infrastructure.aws_multiprocess.aws import (
    create_dynamodb_acciones_table, create_fifo_queue, delete_queue,
    delete_table, get_dynamodb_table, get_queue)


def test_create_or_get_fifo_queue():

    test_queue_name = 'testing_sqs_trastobrain'

    session = get_aws_session(profile_name=AWS_PROFILE)

    try:
        queue = session.resource('sqs').get_queue_by_name(QueueName=test_queue_name)
        if not queue is None:
            queue.delete()
            queue = None
    except Exception as ex:
        print(f"Escepcion preparando todo: {ex}")
    

    queue = create_or_get_fifo_queue(name=test_queue_name, session=session)
    assert not queue is None
    print(queue)

    queue = create_or_get_fifo_queue(name=test_queue_name, session=session)
    assert not queue is None
    print(queue)

    queue.delete()


    
def test_deploy():
    queue_name = "trasto_brain_test_queue"
    create_dynamodb_acciones_table()
    time.sleep(10)
    assert not get_dynamodb_table() is None

    delete_table()

    create_fifo_queue(queue_name)
    time.sleep(10)
    assert not get_queue(queue_name) is None

    delete_queue()
