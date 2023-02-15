
###############
# Try out TTL #
###############

# 1. Create a table with TTL attribute
aws dynamodb create-table \
    --table-name TTLTest  \
    --attribute-definitions '[
       {
          "AttributeName": "PK",
          "AttributeType": "S"
       }
    ]' \
    --key-schema '[
        {
            "AttributeName": "PK",
            "KeyType": "HASH"
        }
    ]' \
    --billing-mode PAY_PER_REQUEST \
    --endpoint-url  http://localhost:8000

# 2. Enable TTL on the table
aws dynamodb update-time-to-live \
    --table-name TTLTest \
    --time-to-live-specification 'Enabled=true,AttributeName=ttl' \
    --endpoint-url  http://localhost:8000

# 3. Add data & wait for expiry
python ./ttl/put-and-wait-for-expiry.py 

######################
# Try out TTL/Stream #
######################

# 1. Follow the steaps above to setup table with TTL enabled

# 2. Enable DynamoDb stream

aws dynamodb update-table \
    --table-name TTLTest \
    --stream-specification StreamEnabled=true,StreamViewType=OLD_IMAGE \
    --endpoint-url http://localhost:8000

# 3. Run the archive-simulator

python ttl/archive-simulator.py 

# 4. Try out auto expiry by running the python code a few times
* Open another terminal 
* You should see message in the other terminal
* You should see files in the ./temp folder

python ttl/put-and-wait-for-expiry.py

# 5. Now add an item without expiry attribute
* User initiated deletes will not lead to archival

aws dynamodb  put-item \
    --table-name    TTLTest  \
    --item '{
        "PK": {"S": "test"},
        "text": {"S": "sample text"}
    }' \
    --endpoint-url http://localhost:8000

# 6. Delete item added in #5

aws dynamodb  delete-item \
    --table-name    TTLTest  \
    --key '{
        "PK": {"S": "test"}
    }' \
    --endpoint-url http://localhost:8000


Cleanup
-------
# 4. Delete table
aws dynamodb delete-table \
    --table-name TTLTest  \
    --endpoint-url http://localhost:8000