# foottraffic 
## (in progress)

* Google Nest Cameras trigger a motion detection event (using the Google developer API)
* Images from the event are captured and retrieved
* These images are then processed using AWS Recognition in a serverless Lambda function (accessed through AWS API Gateway)
* Resulting image labels are then emailed to the user 
