######################
# TransactWriteItems #
######################
https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_TransactWriteItems.html
https://awscli.amazonaws.com/v2/documentation/api/latest/reference/dynamodb/transact-write-items.html

----------------------------------
Business Logic - Standard discount 
----------------------------------
1. Decrease the Discount LeftCount   (UpdateItem)
2. Add an Item indicating that customer has already availed the discount  (PutItem)

Run test - v1
-------------
1. Get the CountLeft for the DISCOUNT#100 
aws dynamodb get-item --table-name FlashSaleDiscounts \
    --key '{
        "PK": {"S": "DISCOUNT#100"},
        "SK": {"S": "DISCOUNT#100"}
    }' \
    --projection-expression "CountLeft" \
    --endpoint-url http://localhost:8000

2. Apply DISCOUNT#100 for CUST#john
If you run this twice - first time it would succeed as the item with (PK=CUST#john and SK=DISCOUNT#100) does not exist. Second time it would fail.
aws dynamodb transact-write-items  \
    --transact-items '[ 
        {
                "Update": {
                    "TableName": "FlashSaleDiscounts",
                    "Key": {
                        "PK": {"S":"DISCOUNT#100"}, 
                        "SK": {"S":"DISCOUNT#100"}
                    },
                    "UpdateExpression": "SET #CountLeft = #CountLeft - :DecreaseBy",
                    "ConditionExpression": "#CountLeft > :MinCoupon",
                    "ExpressionAttributeNames": {"#CountLeft":"CountLeft"},
                    "ExpressionAttributeValues": {":DecreaseBy": {"N":"1"}, ":MinCoupon": {"N":"0"}}
                }
            },
            {
                "Put": {
                    "TableName": "FlashSaleDiscounts",
                    "Item": {
                        "PK": {"S":"CUST#john"}, 
                        "SK": {"S":"DISCOUNT#100"}
                    },
                    "ConditionExpression": "attribute_not_exists(#sk)",
                    "ExpressionAttributeNames": {"#sk":"SK"}
                }
            }
    ]'   \
    --endpoint-url http://localhost:8000

3. Get the CountLeft for the DISCOUNT#100 
aws dynamodb get-item --table-name FlashSaleDiscounts \
    --key '{
        "PK": {"S": "DISCOUNT#100"},
        "SK": {"S": "DISCOUNT#100"}
    }' \
    --projection-expression "CountLeft" \
    --endpoint-url http://localhost:8000


[For running a successfull test again]
---------------------------------------
- Delete the item PK=CUST#john and SK=DISCOUNT#100
aws dynamodb delete-item --table-name FlashSaleDiscounts \
  --key '{
    "PK": {"S": "CUST#john"},
    "SK": {"S": "DISCOUNT#100"}
  }' \
  --endpoint-url http://localhost:8000

Business Logic - Loyalty discount - v2
---------------------------------------
1. Decrease the Loyalty Discount LeftCount   (UpdateItem)
2. Check condition that customer has Loyalty points > MinimumLoyaltyPoints
3. Add an Item indicating that customer has availed the Loyalty discount  (PutItem)


1. Get the CountLeft for the LOYALTY#5000
aws dynamodb get-item --table-name FlashSaleDiscounts \
    --key '{
        "PK": {"S": "LOYALTY#5000"},
        "SK": {"S": "LOYALTY#5000"}
    }' \
    --projection-expression "CountLeft" \
    --endpoint-url http://localhost:8000

1. Apply LOYALTY#5000 discount that requires LoyaltyPoints > 5000

- Apply for John who has LoyaltyPoints = 1000

aws dynamodb transact-write-items  \
    --transact-items '[ 
        {
                "Update": {
                    "TableName": "FlashSaleDiscounts",
                    "Key": {
                        "PK": {"S":"LOYALTY#5000"}, 
                        "SK": {"S":"LOYALTY#5000"}
                    },
                    "UpdateExpression": "SET #CountLeft = #CountLeft - :DecreaseBy",
                    "ConditionExpression": "#CountLeft > :MinCoupon",
                    "ExpressionAttributeNames": {"#CountLeft":"CountLeft"},
                    "ExpressionAttributeValues": {":DecreaseBy": {"N":"1"}, ":MinCoupon": {"N":"0"}}
                }
            },
            {
                "ConditionCheck": {
                    "TableName": "FlashSaleDiscounts",
                    "Key": {
                        "PK": {"S":"CUST#john"}, 
                        "SK": {"S":"CUST#john"}
                    },
                    "ConditionExpression": "#LoyaltyPoints > :LoyaltyPoints",
                    "ExpressionAttributeNames": {"#LoyaltyPoints":"LoyaltyPoints"},
                    "ExpressionAttributeValues": {":LoyaltyPoints": {"N":"5000"}}
                }
            },
            {
                "Put": {
                    "TableName": "FlashSaleDiscounts",
                    "Item": {
                        "PK": {"S":"CUST#john"}, 
                        "SK": {"S":"LOYALTY#5000"}
                    },
                    "ConditionExpression": "attribute_not_exists(#sk)",
                    "ExpressionAttributeNames": {"#sk":"SK"}
                }
            }
    ]'   \
    --endpoint-url http://localhost:8000

1. Apply LOYALTY#5000 discount that requires LoyaltyPoints > 5000

- Apply for Anil who has LoyaltyPoints = 5001
aws dynamodb transact-write-items  \
    --transact-items '[ 
        {
                "Update": {
                    "TableName": "FlashSaleDiscounts",
                    "Key": {
                        "PK": {"S":"LOYALTY#5000"}, 
                        "SK": {"S":"LOYALTY#5000"}
                    },
                    "UpdateExpression": "SET #CountLeft = #CountLeft - :DecreaseBy",
                    "ConditionExpression": "#CountLeft > :MinCoupon",
                    "ExpressionAttributeNames": {"#CountLeft":"CountLeft"},
                    "ExpressionAttributeValues": {":DecreaseBy": {"N":"1"}, ":MinCoupon": {"N":"0"}}
                }
            },
            {
                "ConditionCheck": {
                    "TableName": "FlashSaleDiscounts",
                    "Key": {
                        "PK": {"S":"CUST#anil"}, 
                        "SK": {"S":"CUST#anil"}
                    },
                    "ConditionExpression": "#LoyaltyPoints > :LoyaltyPoints",
                    "ExpressionAttributeNames": {"#LoyaltyPoints":"LoyaltyPoints"},
                    "ExpressionAttributeValues": {":LoyaltyPoints": {"N":"5000"}}
                }
            },
            {
                "Put": {
                    "TableName": "FlashSaleDiscounts",
                    "Item": {
                        "PK": {"S":"CUST#anil"}, 
                        "SK": {"S":"LOYALTY#5000"}
                    },
                    "ConditionExpression": "attribute_not_exists(#sk)",
                    "ExpressionAttributeNames": {"#sk":"SK"}
                }
            }
    ]'   \
    --endpoint-url http://localhost:8000

--------------------------------------
TransactWriteItems support Idempotency
--------------------------------------

1. Check Loyalty points for John

aws dynamodb get-item --table-name FlashSaleDiscounts \
    --key '{
        "PK": {"S": "CUST#john"},
        "SK": {"S": "CUST#john"}
    }' \
    --projection-expression "LoyaltyPoints" \
    --endpoint-url http://localhost:8000

2. Increase loyalty points for customer
- For John increase Loyalty points by 500

aws dynamodb transact-write-items  \
    --client-request-token  1234567890,  \
    --transact-items '[
        { 
            "Update": {
                "TableName": "FlashSaleDiscounts",
                "Key": {
                    "PK": {"S":"CUST#john"}, 
                    "SK": {"S":"CUST#john"}
                },
                "UpdateExpression": "SET #LoyaltyPoints = #LoyaltyPoints + :LoyaltyPoints",
                "ExpressionAttributeNames": {"#LoyaltyPoints":"LoyaltyPoints"},
                "ExpressionAttributeValues": {":LoyaltyPoints": {"N":"500"}}
            }
        }
    ]'   \
    --endpoint-url http://localhost:8000