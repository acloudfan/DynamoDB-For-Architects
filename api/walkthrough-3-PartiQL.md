###########
# PartiQL #
###########
https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/ql-reference.html

########################################
# API to execute the PartiQL statement #
########################################
https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_ExecuteStatement.html

https://awscli.amazonaws.com/v2/documentation/api/latest/reference/dynamodb/execute-statement.html

aws dynamodb execute-statement \
    --statement  "SELECT FirstName, LastName FROM Employee WHERE LoginAlias='johns'" \
    --return-consumed-capacity TOTAL \
    --endpoint-url   http://localhost:8000









##########
# SELECT #
##########

SELECT LoginAlias,FirstName, Designation 
FROM Employee
WHERE LoginAlias IN ['rajs','johns']
ORDER BY LoginAlias DESC



##########
# Insert #
##########

INSERT INTO Employee
VALUE {
    'LoginAlias': 'katek', 
    'FirstName': 'Kate', 
    'LastName': 'Kilmer',
    'Designation': 'Manager',
    'ManagerLoginAlias': 'johns',
    'Skills': <<'administration'>>
}


##########
# Update #
##########
- Add a new skill to katek

UPDATE Employee
SET Skills = SET_ADD(Skills, <<'hiring'>>)
WHERE LoginAlias = 'katek'

##########
# Delete #
##########
- Delete the employee with LoginAlias = katek

DELETE FROM Employee
WHERE LoginAlias='katek'

#############
# Functions #
#############
https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/ql-functions.contains.html

- Find all employees who have 'java' in their skills

SELECT * 
FROM Employee
WHERE Skill Contains(Skills, 'java')

- Find all employees with first name begining with J

SELECT FirstName FROM Employee
WHERE begins_with(FirstName,'J')

