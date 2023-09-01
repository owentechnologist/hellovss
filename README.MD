
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

python3 redisvl_1.py -h redis-10400.homelab.local -p 10400 -c y -t y
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

* This example run -c creates a new Search Index and then -t tries the query:

```
python3 redisvl_1.py -h redis-10400.homelab.local -p 10400 -c y -t y
```

* This example run -l loads data into Redis and then -t tries the query:  
(note that if you run this program more than once with the -l argument the data will grow in size and query results will shift)

```
python3 redisvl_1.py -h redis-10400.homelab.local -p 10400 -l y -t y
```


6. If you get errors it is most likely because you haven't configured the host and port and or username and password to your redis server (each example expects you to modify the code to provide these things)

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
