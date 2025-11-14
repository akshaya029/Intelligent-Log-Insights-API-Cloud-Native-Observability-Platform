from azure.servicebus import ServiceBusClient, ServiceBusMessage

conn_str = "Endpoint=sb://loginsights-namespace.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=FyWy1qFnzBkusdqDAcwTqDnS6IFw32S7Q+ASbCZ2ysw="
queue_name = "critical-alerts-queue"

with ServiceBusClient.from_connection_string(conn_str) as client:
    sender = client.get_queue_sender(queue_name)
    with sender:
        msg = ServiceBusMessage('{"id": "log_test_001", "level": "CRITICAL", "message": "Manual test message"}')
        sender.send_messages(msg)
        print(" Test message sent to Service Bus!")
