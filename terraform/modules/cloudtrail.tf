# CloudTrail
resource "aws_cloudtrail" "anomaly_trail" {
  name                          = "cloud-anomaly-trail"
  s3_bucket_name                = aws_s3_bucket.cloudtrail_logs.bucket
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_logging                = true

  event_selector {
    read_write_type           = "All"
    include_management_events = true

    # Optional: S3 object-level events if needed
    data_resource {
      type   = "AWS::S3::Object"
      values = ["arn:aws:s3:::"]
    }
  }

  tags = {
    Name = "CloudAnomalyTrail"
  }
}
