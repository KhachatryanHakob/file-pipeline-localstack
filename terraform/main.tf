resource "aws_sqs_queue" "upload_queue" {
    name = "file-upload-event"
}

resource "aws_s3_bucket" "bucket" {
    bucket = "localstack-bucket"
}

resource "aws_s3_bucket_notification" "bucket_notification" {
    bucket = aws_s3_bucket.bucket.id

    queue {
        queue_arn = aws_sqs_queue.upload_queue.arn
        events    = ["s3:ObjectCreated:*"]
    }

    depends_on = [aws_sqs_queue.upload_queue]
}
