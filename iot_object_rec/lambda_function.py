import json
import boto3
import requests

bucket_name = os.environ['bucket_name']
access_key_id = os.environ['esIAM_access_key_id']
secret_access_key= os.environ['esIAM_secret_access_key']
region = "us-east-1"

rekognition = boto3.client('rekognition', aws_access_key_id=access_key_id, aws_secret_access_key = secret_access_key, region_name = region)
s3_client = boto3.client('s3', aws_access_key_id=access_key_id, aws_secret_access_key = secret_access_key, region_name=region)
s3_resource = boto3.resource('s3', aws_access_key_id=access_key_id, aws_secret_access_key = secret_access_key, region_name=region)




def get_image(eventId):
    project_id = os.environ['PROJECT_ID']
    device_id = os.environ['DEVICE_ID']
    #  example: /enterprises/project-id/devices/device-id:executeCommand
    uri = "/enterprises/" + project_id + "/devices/" + device_id + ":executeCommand"
    
    data = {
      "command" : "sdm.devices.commands.CameraEventImage.GenerateImage",
      "params" : {
        "eventId" : eventId
      }
    }
    
    r = requests.post(uri, json.dumps(data))
    return r
    
    
def process_image(post_return):
    url = post_return["results"]["url"]
    token = post_return["results"]["token"]
    context = ssl._create_unverified_context()
    fd = urlopen(str(url), context=context)
    f = io.BytesIO(fd.read())
    s3_resource.Object(bucket_name, url).upload_file(f)
    # return image object key
    return url
    


def detect_labels(bucket, key):
    label_list = []
    labels = rekognition.detect_labels(Image={"S3Object": {"Bucket": bucket, "Name": key}})
    labels = labels['Labels'] # extract just labels 
    for item in labels:
        label_list.append(item['Name'].lower())
    
    print("label list:", label_list)

    #head = s3.head_object(Image={"S3Object": {"Bucket": bucket, "Name": key}})
    head = s3.head_object(Bucket=bucket, Key=key)
    date = head["ResponseMetadata"]["HTTPHeaders"]["last-modified"]
    print("info:", head, "\n", date)

    # Process labels
    es_entry = {
        "objectKey": key,
        "bucket": bucket,
        "createdTimestamp": date,
        "labels": label_list
    }
    print("DL return:", es_entry)
    return es_entry


def lambda_handler(event, context):
    # Get the object from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    print("Event", event)
    print("Data", bucket, key)
    
    
    request_return = get_image(eventId)
    image_key = process_image(request_return)
    labels = detect_labels(bucket, image_key)
    
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }



    
