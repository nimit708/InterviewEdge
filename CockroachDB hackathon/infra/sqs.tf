# Amazon SQS — Payment event queue

# Main payment events queue (FIFO for ordering guarantees)
resource "aws_sqs_queue" "payment_events" {
  name                        = "${var.project_name}-${var.environment}-payment-events.fifo"
  fifo_queue                  = true
  content_based_deduplication = true
  visibility_timeout_seconds  = 120
  message_retention_seconds   = 345600 # 4 days
  receive_wait_time_seconds   = 20     # Long polling

  # Dead letter queue
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.payment_events_dlq.arn
    maxReceiveCount     = 3
  })

  tags = {
    Name = "${var.project_name}-${var.environment}-payment-events"
  }
}

# Dead Letter Queue for failed messages
resource "aws_sqs_queue" "payment_events_dlq" {
  name                      = "${var.project_name}-${var.environment}-payment-events-dlq.fifo"
  fifo_queue                = true
  message_retention_seconds = 1209600 # 14 days

  tags = {
    Name = "${var.project_name}-${var.environment}-payment-events-dlq"
  }
}

# Agent task queue (for async agent task dispatch)
resource "aws_sqs_queue" "agent_tasks" {
  name                        = "${var.project_name}-${var.environment}-agent-tasks.fifo"
  fifo_queue                  = true
  content_based_deduplication = true
  visibility_timeout_seconds  = 300 # 5 min — agent tasks take longer
  message_retention_seconds   = 86400

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.agent_tasks_dlq.arn
    maxReceiveCount     = 2
  })

  tags = {
    Name = "${var.project_name}-${var.environment}-agent-tasks"
  }
}

resource "aws_sqs_queue" "agent_tasks_dlq" {
  name                      = "${var.project_name}-${var.environment}-agent-tasks-dlq.fifo"
  fifo_queue                = true
  message_retention_seconds = 1209600

  tags = {
    Name = "${var.project_name}-${var.environment}-agent-tasks-dlq"
  }
}
