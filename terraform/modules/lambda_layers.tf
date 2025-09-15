data "aws_s3_object" "packages_package" {
  bucket = aws_s3_bucket.code_store.id
  key    = "lambda_layers/packages.zip"

  depends_on = [aws_s3_object.layers_folder]
}

data "aws_s3_object" "packages_package_sha256" {
  bucket = aws_s3_bucket.code_store.id
  key    = "lambda_layers/packages.zip.sha256"

  depends_on = [aws_s3_object.layers_folder]
}

resource "aws_lambda_layer_version" "packages_layer" {
  s3_bucket           = data.aws_s3_object.packages_package.bucket
  s3_key              = data.aws_s3_object.packages_package.key
  source_code_hash    = chomp(data.aws_s3_object.packages_package_sha256.body)
  layer_name          = var.lambda_packages_layer_name
  compatible_runtimes = [var.lambda_runtime]
}
