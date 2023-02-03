Iteration#1
===========
- Define the table with *Customer* entity only

Thought exercise?
-----------------
1. How would you add the Account entity to this table?
2. What will be the name of PK for this table?

Iteration#2
===========
- Rename the PK and add SK to the table

Thought exercise?
-----------------
1. 

Iteration#3
===========
Analyze customer - account relationship and select the GSI pattern, that will address the access pattern for Account

Iteration#4
===========
Introduce a GSI to address the Account related access patterns

Iteration#5
===========
Add the transaction entity. Decide on whether the transaction entity should be modeled as top-level?

Make the changes and try out the queries.

* #9 Get last N transactions for an account

aws dynamodb query \
   --table-name acme-bank-v5 \
   --index-name  GSI_Inverted \
   --key-condition-expression 'SK = :pk' \
   --expression-attribute-values '{
      ":pk": {"S": "ACCT#501"}
   }' \
   --limit  2 \
   --endpoint-url   http://localhost:8000

* #10 Get txn information by txn number

aws dynamodb query \
   --table-name acme-bank-v5 \
   --key-condition-expression 'PK = :pk' \
   --expression-attribute-values '{
      ":pk": {"S": "TXN#1001"}
   }' \
   --endpoint-url   http://localhost:8000

=============
Iteration#6.1
=============

Analysis
Mark the access patterns that can take advantage of sparse index.

2. Get customer by phone#
--------------------------
* ACME bank has 3.2M customers
* Every customer is identified by their unique phone number

3. Get customers from a particular state in US
----------------------------------------------
* ACME bank has 3.2M customers
* Every customer MUST declare a single state as the state of residence. ACME bank uses this information for regulatory purposes. Bank runs reports to group customers on their state of residence.

4. Get customers numbers for customers with special status
-----------------------------------------------------------
* Customers can have a special status
* ACME bank recognizes [Veterans, Handicap, Student] as special status
* Only 0.15% of current customers have the special status

11. Get transactions on account within date range
-------------------------------------------------
* On average every customer carries out 8 transactions/month
* After 7 years customer's transactions are archived 
* Archived transactions are not accessible throuh this query

12. Create report on all transactions for a given date
------------------------------------------------------
* On an average there are 750K transactions/day
* Report is generated for reconcilliation on a daily basis
* Report generated for any day on ad-hoc basis as well

13. Create report on declined transactions for a given date range
-----------------------------------------------------------------
* Roughly 0.10% of daily transactions get declined
* Report needs to be generated for declined transactions. 
* This is used for fraud detection and other purposes.

###############
# Iteration#6 #
###############
Add the Sparse indexes.
1. GSI_Sparse_Customer_Special_Status
   PK = PK, SK = special_status_indicator

   Why did we add 2 attributes for special status?
   -----------------------------------------------
   * A customer can have multiple special status e.g., "a handicap veteran", "a student veteran"
   * That would require us to maintain the statuses in a string set
   * Since String Set type cannot be used as SK, we introduced the indicator attribute

   Application responsibility
   --------------------------
   * Application will maintain the consistency
   * Any time status is added to special_status the special_status_indicator = yes
   * When all special status removed for a customer, the special_status_indicator attribute will be REMOVED. If you set it to 'no', then the item will still appear in the index & that will defeat the purpose :(

2. GSI_Sparse_TXN_Declined
   PK = txn_declined_reason, SK = txn_date

   Why did we choose this key-schema?
   ----------------------------------
   * The index data will be partitioned on the decline-reason
   * SK is set to the txn date as data needs to be queried on date range
   * No additional attribute needed as the two attributes needed for this index are already part of the item

   Application responsibility
   --------------------------
   * Application must use all txn_declined_reason codes to pull & consolidate the declined txns
   * Pseudcode:
      FOR reason IN ["low_balance", "unauthorized","illegible_check"...]  
           result = Query(PK=reason,SK=date-range)
           Consolidated_List.append(result)
   
Deploy to local Dynamo & test
=============================

* Get customers with special status
* Use a filter expression with contains to get data for specific status

aws dynamodb scan \
   --table-name acme-bank-v6 \
   --index-name  GSI_Sparse_Customer_Special_Status \
   --filter-expression 'contains(special_status,:status)'  \
   --expression-attribute-values '{
      ":status": {"S": "veteran"}
   }' \
   --endpoint-url   http://localhost:8000

* Get declined txn by date

aws dynamodb query \
   --table-name acme-bank-v6 \
   --index-name  GSI_Sparse_TXN_Declined \
   --key-condition-expression 'txn_declined_reason = :reason AND txn_date=:dt' \
   --expression-attribute-values '{
      ":reason": {"S": "low_balance"},
      ":dt": {"S": "2022/06/19"}
   }' \
   --endpoint-url   http://localhost:8000

###############
# Iteration#7 #
###############
Look for opprtunity to use overloaded key-attributes

2. Get customer by phone#
Key schema { GSI1_PK = Phone#,  GSI1_SK = CUST#}

3. Get customers from a particular state in US
Key schema { GSI1_PK = State,  GSI1_SK = CUST#}

11. Get transactions on account within date range
Key schema { GSI1_PK = ACCT#,  GSI1_SK = txn_date}

12. Create report on all transactions for a given date
Key schema { GSI1_PK = txn_date#,  GSI1_SK = ACCT#}


###############
# Iteration#8 #
###############
ACME marketing team sends offers to customers from time to time.
These offers sent groups of customers based on some criteria e.g.,
special status of customer, balance over $10K 

Requirements:
   1. An Offer is identified by a date and number
      01022022-1 = Offer created on 01/02/2022 
      01022022-2 = Offer created on 01/02/2022 
      05262022-1 = Offer created on 05/26/2022
   2. Offer have an expiry date
   3. Offer has multiple details including terms and conditions
   4. Access patterns:
      * Get details of an offer based on OFFER#
      * Get offers for a CUST# (with optional OFFER#)
      * Get status of offer for a customer (CUST# & OFFER#)
         Offer status for a customer = PENDING, ACCEPTED, REJECTED
   5. Offer needs to be deleted for CUSTOMER 6 months after its expiry

Analysis (8.1)
==============
- How would you create the Offer entity?
- How would you manage the relationship between cust and offer?
- What data will be managed for the customer-offer relationship?
- How will you manage consistency between relationship & entity data?

Setup Offer-Customer many-to-many relationship (8.2)
====================================================
1. Add the attributes for OFFER entity
2. Add attributes for CUST-OFFER relationship
3. Checkout the Aggregate view : Table
4. Checkout the Aggregate view : GSI_Inverted


################
# Iteration# 9 #
################


#################
# Iteration# 10 #
#################


#################
# Iteration# 11 #
#################

1. Check condition that balance can cover the Debit
   This condition is NOT needed for Credit

2. Account balance is maintained in the item
   (PK=CUST#, SK=ACCT#)

3. Txn leads to an insertion of a unique txn
   (PK=TXN#, SK=ACCT#)

Processing steps:
-----------------
1. Get the CUST# for the ACCT#

aws dynamodb query --table-name acme-bank-v10 \
    --index-name  GSI_Inverted  \
    --key-condition-expression "SK=:sk AND begins_with(PK,:cust)" \
    --expression-attribute-values '{
      ":sk": {"S": "ACCT#510"},
      ":cust": {"S": "CUST#"}
    }' \
    --projection-expression "PK,acct_balance" \
    --endpoint-url  http://localhost:8000

Result: CUST#102

2. Transaction for a credit action (deposit $50)
This transaction does not require the balance to be checked

* Add a condition to ensure that Update does not create a CUST#/ACC# !!!
aws dynamodb transact-write-items \
    --transact-items '[
      {
         "Update": {
            "TableName": "acme-bank-v10",
            "Key": {
                  "PK": {"S":"CUST#102"}, 
                  "SK": {"S":"ACCT#510"}
            },
            "ConditionExpression": "attribute_exists(#sk)",
            "UpdateExpression": "SET #balance = #balance + :txn_amount",
            "ExpressionAttributeNames": {"#sk": "SK", "#balance":"acct_balance"},
            "ExpressionAttributeValues": {":txn_amount": {"N":"50"}}
         },
         "Put" : {
            "TableName": "acme-bank-v10",
            "Item": {
                  "PK": {"S":"TXN#1009"}, 
                  "SK": {"S":"ACCT#510"},
                  "txn_date": {"S": "2023/01/01"},
                  "txn_type": {"S": "atm"},
                  "txn_amount": {"N": "50"},
                  "GSI1_PK": {"S": "2023/01/01"},
                  "GSI1_SK": {"S":"ACCT#510"}
            },
            "ConditionExpression": "attribute_not_exists(#pk)",
            "ExpressionAttributeNames": {"#pk":"PK"}
         }
      }
      ]' \
    --endpoint-url http://localhost:8000

3. Transaction for a debit action (withdraw $50)

V1-PUT
=======


* Set the CUST# and acct_balance in this call otherwise condition expression will fail

aws dynamodb transact-write-items \
    --transact-items '[
      {
         "Update": {
            "TableName": "acme-bank-v10",
            "Key": {
                  "PK": {"S":"CUST#102"}, 
                  "SK": {"S":"ACCT#510"}
            },
            "UpdateExpression": "SET #balance = #balance + :txn_amount",
            "ConditionExpression": "attribute_exists(#sk) AND #balance = :current_balance",
            "ExpressionAttributeNames": {"#sk": "SK", "#balance":"acct_balance"},
            "ExpressionAttributeValues": {":txn_amount": {"N":"50"}, ":current_balance":{"N":"1150"}}
         },
         "Update" : {
            "TableName": "acme-bank-v10",
            "Key": {
                  "PK": {"S":"TXN#1009"}, 
                  "SK": {"S":"ACCT#510"}
            },
            "UpdateExpression": "SET #txn_amount = :txn_amount, #txn_date = :txn_date, #txn_type = :txn_type, #GSI1_PK = :GSI1_PK, #GSI1_SK = :GSI1_SK",
            "ConditionExpression": "attribute_not_exists(#pk) AND attribute_not_exists(#sk)",
            "ExpressionAttributeNames": {"#pk":"PK", "#sk":"SK", "#txn_amount":"txn_amount","#txn_date":"txn_date","#txn_type":"txn_type","#GSI1_PK":"GSI1_PK","#GSI1_SK":"GSI1_SK"},
            "ExpressionAttributeValues": {":txn_amount":{"N":"50"}, ":txn_date":{"S":"2023/01/01"}, ":txn_type":{"S":"atm"},":GSI1_PK": {"S": "2023/01/01"}, ":GSI1_SK": {"S":"ACCT#510"}}
         }
      }
      ]' \
    --endpoint-url http://localhost:8000

