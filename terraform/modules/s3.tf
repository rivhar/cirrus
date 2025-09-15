resource "aws_s3_bucket" "code_store" {
  bucket = var.code_store_bucket
}

resource "aws_s3_bucket_public_access_block" "code_store_pba" {
  bucket = aws_s3_bucket.code_store.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true

  depends_on = [aws_s3_bucket.code_store]
}

resource "aws_s3_bucket_versioning" "code_store_versioning" {
  bucket = aws_s3_bucket.code_store.id
  versioning_configuration {
    status = "Enabled"
  }

  depends_on = [aws_s3_bucket.code_store]
}

resource "aws_s3_bucket_lifecycle_configuration" "code_store_lifecycle" {
  bucket = aws_s3_bucket.code_store.id

  rule {
    id     = "ExpireOldVersions"
    status = "Enabled"

    noncurrent_version_expiration {
      noncurrent_days = 7
    }
  }
  depends_on = [aws_s3_bucket.code_store]
}

resource "aws_s3_bucket_server_side_encryption_configuration" "code_store_sse" {
  bucket = aws_s3_bucket.code_store.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }

  depends_on = [aws_s3_bucket.code_store]
}

resource "aws_s3_object" "layers_folder" {
  bucket  = aws_s3_bucket.code_store.id
  key     = "lambda_layers/"
  acl     = "private"
  content = "application/x-directory"

  depends_on = [aws_s3_bucket.code_store]
}

# data "aws_s3_object" "usecase_code_folder" {
#   for_each = toset(local.usecase_names)
#   bucket   = aws_s3_bucket.code_store.id
#   key      = "${each.key}_lambda_package/"

#   depends_on = [aws_s3_bucket.code_store]
# }

resource "aws_s3_bucket" "cloudtrail_logs" {
  bucket = var.cloudtrail_logs_bucket_name

}

resource "aws_s3_bucket_public_access_block" "cloudtrail_logs_pba" {
  bucket = aws_s3_bucket.cloudtrail_logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true

  depends_on = [aws_s3_bucket.cloudtrail_logs]
}

resource "aws_s3_bucket_versioning" "cloudtrail_logs_versioning" {
  bucket = aws_s3_bucket.cloudtrail_logs.id
  versioning_configuration {
    status = "Enabled"
  }

  depends_on = [aws_s3_bucket.cloudtrail_logs]
}

resource "aws_s3_bucket_lifecycle_configuration" "cloudtrail_logs_lifecycle" {
  bucket = aws_s3_bucket.cloudtrail_logs.id

  rule {
    id     = "ExpireOldVersions"
    status = "Enabled"

    noncurrent_version_expiration {
      noncurrent_days = 7
    }
  }
  depends_on = [aws_s3_bucket.cloudtrail_logs]
}

resource "aws_s3_bucket_server_side_encryption_configuration" "cloudtrail_logs_sse" {
  bucket = aws_s3_bucket.cloudtrail_logs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }

  depends_on = [aws_s3_bucket.cloudtrail_logs]
}
