# 532-final 

--- System Configuration --- 

The main components and their configuraitons are explained within the cloudConfig.txt file and the hwConfig.txt file. 
The key steps are as follows:
- Build device
    - Connect ultrasonic sensor to ESP32
    - Offload code onto ESP32
    - Connect device to permanent power, mount to top of water drum, boot on

- Setup cloud services
    - Create things, attatch permissions to certificates. Use provided certficate and key and endpoint to connect device to AWS
    - Create DynamoDB table
    - Reroute distance messages published by devices to Iot Core to DynamooDB table, hash values given the device_id
    - Create Lambda function that returns distance of a certain deivce from the dynamooDB table, given the device_id
    - Create a API Gateway GET call that uses the lambda function, using the device_id as the parameter, to create a API call that will be used by the email script and the web app.
    - Create an EC2 server
        - Upload email notification script
            - give cron executabile rights
            - create cron job to run the script every 30 minutes
            - give cron boot persistance
        - Upload the flask web application
            - Create a systemmd service for gunicorn to host the app
            - configue the service given the python.config and requirments.txt (which also was in the virtual enviroment created for the app)
            - Start and enable the guniron service with boot. 
