
from trasto.infrastructure.aws_sqs.aws import delete_queue, get_aws_session, AWS_PROFILE, create_or_get_fifo_queue


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

    