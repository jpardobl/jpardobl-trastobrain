
import time

from trasto.infrastructure.aws_multiprocess.aws import (
    create_dynamodb_acciones_table, create_fifo_queue, delete_queue,
    delete_acciones_table, get_dynamodb_acciones_table, get_queue)


def test_create_dynamodb_acciones_table():
    assert not create_dynamodb_acciones_table() is None

    
def test_deploy():
    queue_name = "trasto_brain_test_queue"
    create_dynamodb_acciones_table()
    time.sleep(10)
    assert not get_dynamodb_acciones_table() is None

    delete_acciones_table()

    create_fifo_queue(queue_name)
    time.sleep(10)
    assert not get_queue(queue_name) is None

    delete_queue(queue_name)
