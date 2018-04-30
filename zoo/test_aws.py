import boto3

s3 = boto3.resource('s3')

for bucket in s3.buckets.all():
  print(bucket.name)

try:
    s3.Bucket('seer-model-zoo').download_file(KEY, 'my_local_image.jpg')
except botocore.exceptions.ClientError as e:
    if e.response['Error']['Code'] == "404":
        print("The object does not exist.")
    else:
        raise