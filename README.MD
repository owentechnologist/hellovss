
1. Create a virtual environment:

```
python3 -m venv redisvl
```

2. Activate it:  [This step is repeated anytime you want this venv back]

```
source redisvl/bin/activate
```

On windows you would do:

```
venv\Scripts\activate
```

3. Python will utilize this requirements.txt in the project:

```
redis>=4.3.4
redisvl>=0.0.3
```

4. Run: [this step is repeated anytime you want this venv]

```
pip3 install -r requirements.txt
```

5. Execute the redisvl_1.py code (or another example) from the project directory:

#### You should probably run with all the available options enabled the first time you run the program

```
python3 redisvl_1.py -h redis-10400.homelab.local -p 10400 -c y -l y -t y
```

#### but no need to recreate the index, or load more data if you don't want to, for consecutive runs


* This example run -t tries just a Search Query:

```
python3 redisvl_1.py -h redis-10400.homelab.local -p 10400 -t y
```

* This example run -l loads data into Redis and then -t tries the query:  
(note that if you run this program more than once with the -l argument the data will grow in size and query results will shift)

```
python3 redisvl_1.py -h redis-10400.homelab.local -p 10400 -l y -t y
```

* This example run -c creates a new Search Index and then -t tries the query:

```
python3 redisvl_1.py -h redis-10400.homelab.local -p 10400 -c y -t y
```


6. If you get errors it is most likely because you haven't configured the host and port to your redis server

7. If you get no results from your query - try again  - the program flips a coin and is more generous with the results every other time - also, you can make more data for more results by running the program a few times with this argument/flag: 

```
-l y
``````

8. when you are done exploring this set of examples you can deactivate the virtual environment:

```
deactivate
```

useful link to python docs for redis:
https://redis.readthedocs.io/en/stable/redismodules.html 

useful links for redisvl:
https://github.com/RedisVentures/redisvl/tree/main 
https://github.com/RedisVentures/redisvl 


#### Here is a sample run with results:
``` 
(redisvl) owentaylor@Owens-MacBook-Pro hellovss % python3 redisvl_1.py -h redis-10400.homelab.local -p 10400 -c n -l y -t y
user_choice for -c == n
user_choice for -l == y
user_choice for -t == y

<class 'dict'>
search_schema loaded

connecting to: host=redis-10400.homelab.local port=10400 ...
loading data into redis...
Dummy Data created! - here is a sample of one of the elements and it's length:
b'\xcd\xccL>\xcd\xccL>\xe8\xb4\x01>'

12

Executing a test query against the redis search index...
        RESULT:


        ISSUING THIS QUERY: 
(@age:[40 +inf] @age:[-inf 45])=>[KNN 200 @user_embedding $vector AS vector_distance] RETURN 5 user age job credit_score vector_distance SORTBY vector_distance ASC DIALECT 2 LIMIT 0 200


Query Results have a length of 2

RESULT:
 {'id': 'users:0e4b96bcf8d64eb5a5b4f9bbd30bd89d', 'vector_distance': '0.177916705608', 'user': 'joe', 'age': '40', 'job': 'dentist', 'credit_score': 'medium'}

RESULT:
 {'id': 'users:aa04263d6a7a4c1b8c6e11618d64c920', 'vector_distance': '0.311962246895', 'user': 'mary', 'age': '45', 'job': 'doctor', 'credit_score': 'low'}


exiting ...
```
