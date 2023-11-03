This project has several examples of using Redis, RediSearch + VSS and LLM technologies with Python

useful link to python docs for redis:
https://redis.readthedocs.io/en/stable/redismodules.html 

useful links for redisvl:
https://github.com/RedisVentures/redisvl/tree/main 
https://github.com/RedisVentures/redisvl 

SETUP:

If you intend to utilize the local language models you need to install https://gpt4all.io/index.html (do this before you do anything else)

To run the Battleship example, which utilizes only Vector Similarity Search, you do not need anything but a connection to Redis running Search 2.6 or higher.  

You can create a free Redis Enterprise instance for this purpose by going to https://redis.com/try-free/   (Just be sure to select Redis Stack as the type of database you create)


## Python-preparation Steps for running the samples on your dev machine:


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
etc ...
```

4. Install the libraries: [only necesary to do this one time per environment]

```
pip3 install -r requirements.txt
```

5. And for the local LLM demos --> Download one of the LLM libraries needed to test the generative examples:  (make sure you already installed gpt4all  https://gpt4all.io/index.html )

```
wget --no-check-certificate https://huggingface.co/nomic-ai/gpt4all-falcon-ggml/resolve/main/ggml-model-gpt4all-falcon-q4_0.bin
```

6. For a non-LLM Vector Similarity Search example:  Execute the vss_battleship.py code from the project directory.

The vss_battlehip.py code generates a vector that represents the position of a ship on a 10 x 10 grid.  You take shots at the ship targetting its anchor point.  The similiarity of the vector you generate from your anchor point is compared to the similarity of the available ships's vectors - if you are close enough or have an exact match - you hit!
Note: to make it more challenging, there are 10 quadrants and the ships are scattered across them as well.  Your search will, therefore be a hybrid query - where you select the target quadrant as well as generate a vector that represents the ships occupation of that quadrant.

You should run with all the available options enabled the first time you run the program:  (use your redis -h host and -p port and -s password)

``` 
(redisvl) owentaylor@Owens-MacBook-Pro hellovss % python3 vss_battleship.py -h e5.southcentralus.redisenterprise.cache.azure.net -p 10000 -s RmOBOd4kOXO5czNWeDPac3EJY+ZNGFEmV7hgC2EtiD7o1= -c y -l y -t y -e y
```

After the first time you run the program you should set the index creation flag -c to n  (you can also choose to turn off the -e explanation)

``` 
(redisvl) owentaylor@Owens-MacBook-Pro hellovss % python3 vss_battleship.py -h e5.southcentralus.redisenterprise.cache.azure.net -p 10000 -s RmOBOd4kOXO5czNWeDPac3EJY+ZNGFEmV7hgC2EtiD7o1= -c n -l y -t y -e n
MAIN FUNCTION CALLED
user_choice for -c == n
user_choice for -l == y
user_choice for -t == y

<class 'dict'>
search_schema loaded

connecting to: host=e5.southcentralus.redisenterprise.cache.azure.net port=10000 ...
loading data into redis...
 Target generated battleship has anchor_point of 27
| *  *  *  *  *  *  *  *  *  *  |
| *  *  *  *  *  *  *  *  *  *  |
| *  *  *  *  *  * [ ] *  *  *  |
| *  *  *  *  *  * [ ] *  *  *  |
| *  *  *  *  * [ ][ ][ ] *  *  |
| *  *  *  *  * [ ][ ][ ] *  *  |
| *  *  *  *  * [ ][ ][ ] *  *  |
| *  *  *  *  *  * [ ] *  *  *  |
| *  *  *  *  *  * [ ] *  *  *  |
| *  *  *  *  *  *  *  *  *  *  |
Ship shape_and_coordinates created! - here is a sample of one of the elements:
Submarine

        You are playing BATTLESHIP! 
(executing queries against the redis search index)...
We have spotted 10 ships:
Spotted: 1 Aircraft_Carrier in qudrant 7
Spotted: 1 Submarine in qudrant 7
Spotted: 1 Aircraft_Carrier in qudrant 1
Spotted: 1 Submarine in qudrant 5
Spotted: 1 Skiff in qudrant 3
Spotted: 1 Destroyer in qudrant 3
Spotted: 1 Destroyer in qudrant 1
Spotted: 1 Submarine in qudrant 9
Spotted: 1 Destroyer in qudrant 2
Spotted: 1 Submarine in qudrant 1

        Enter an integer between 2 and 8 for target X coordinate :   7
        Enter an integer between 1 and 4 for target Y coordinate :   4
        Enter an integer between 1 and 10 for target quadrant :   3
query is--> 
quadrant is 3
anchorX == 7  anchorY == 4 
 Target generated battleship has anchor_point of 47
| *  *  *  *  *  *  *  *  *  *  |
| *  *  *  *  *  *  *  *  *  *  |
| *  *  *  *  *  *  *  *  *  *  |
| *  *  *  *  *  *  *  *  *  *  |
| *  *  *  *  *  * [ ] *  *  *  |
| *  *  *  *  *  * [ ] *  *  *  |
| *  *  *  *  * [ ][ ][ ] *  *  |
| *  *  *  *  * [ ][ ][ ] *  *  |
| *  *  *  *  * [ ][ ][ ] *  *  |
| *  *  *  *  *  * [ ] *  *  *  |

Query Results have a length of 1

You HIT Something! ...:
 Document {'id': 'battleship:5dc84ae8476d4069b2c117a41e969276', 'payload': None, 'knn_dist': '5', 'battleship_class': 'Skiff', 'quadrant': '3', 'battleship_id': '753455348152000'}

Should we blast that ship out of the water (remove it from Redis)? Y/N :Y
                !!KABLOOEY!!

exiting ...
```

6. If you get errors it is most likely because you haven't configured the host and port to your redis server

7. If you get no results from your query - try again and load more battleships using this argument/flag: 

```
-l y
``````

8. when you are done exploring this set of examples you can deactivate the virtual environment:

```
deactivate
```


#### Another example offers a taste of an expert system or simple chat bot
 (This example does not use the RedisVL library and manages key names deliberately rather than having a library generate a unique key for each embedding)

The example: localCMDLineChat.py showcases the following flow where:
* user submits prompt text
* script uses huggingFace library to create embedding of prompt
* script stores embedding in RedisVSS as part of a Hash object 
* RedisVSS adds the Hash object to its search index
* script searches RedisVSS for similar prompts and their responses
* if similar prompt and cached response exists, the cached response is sent to UI/User
* if no cached response exists, script calls LLM to generate new one
* new response is cached in Redis along with prompt
* new response is sent to user via UI

![Sequence](./Python_LLM_VSS_CACH.png)

To start this example you will need to download and remember the path to a LLM model binary to your local machine - the default one (the one in the code) is: 

ggml-model-gpt4all-falcon-q4_0.bin

Which is around 4 GB in size, requires 8GB of RAM, and can be downloaded from huggingface:

https://huggingface.co/nomic-ai/gpt4all-falcon-ggml/tree/main 

Another option which I find produces slower, less predictable results due to it being more 'social' and inclined to repond as a chat or long text with emojis is:

llama-2-7b-chat.ggmlv3.q4_0.bin

Which is a few GB in size, also requires 8GB of ram and can be downloaded from gpt4all:

https://gpt4all.io/index.html

Once you have downloaded one of the generative models above, edit the code in localCMDLineChat.py around line 130 to point to the path on your system that holds the binary file for that model.

NB: The template code for the model which guides it as to how to respond, may need tweaking if you use llama-2-7b-chat.ggmlv3.q4_0.bin  A different template is provided (rename the variable name in your code to assign its value to the template to be used)

You will also need to ensure you are able to access an instance of Redis that includes the Vector Similarity Search Capable RediSearch 2.4 or better Redis module.


Provide arguments to the runtime when you start it like this:

```
python3 localCMDLineChat.py redis-12134.c309.us-east-2-1.ec2.cloud.redislabs.com 12134 WxdzS2orEF4Dh0baBeaRqo16srYYxzIo1
```

Note that the LLM model is lazy-loaded so that the cached response can come back quicky when the Vector Similarity search identifies a close enough answer in the cache to warrant using that instead of generating a new query.  

Below, you can see the falcon LLM generating an answer takes ~30 seconds, whereas the next query which is slighly different, but shares enough meaning that it uses the cache, takes only ~131 milliseconds to provide the response.

(Note that both executions require the SentenceTransformer to create the embedding for use as the argument to the VSS search.)

```
(redisvl) owentaylor@Owens-MacBook-Pro hellovss % python3 localCMDLineChat.py redis-12134.c309.us-east-2-1.ec2.cloud.redislabs.com 12134 WxdzS2orEF4Dh0baBeaRqo16srYYxzIo1

**********************************************

        Type: END   and hit enter to exit the program...

        Commandline Instructions: 
Type in your prompt/question as a single statement with no return characters... 
(only hit enter for the purpose of submitting your question)

**********************************************


        What is your question? (prompt):        tell me about sun spots

 No suitable response has been cached.  Generating new Response...

Found model file at  ./ggml-model-gpt4all-falcon-q4_0.bin
falcon_model_load: loading model from './ggml-model-gpt4all-falcon-q4_0.bin' - please wait ...
falcon_model_load: n_vocab   = 65024
falcon_model_load: n_embd    = 4544
falcon_model_load: n_head    = 71
falcon_model_load: n_head_kv = 1
falcon_model_load: n_layer   = 32
falcon_model_load: ftype     = 2
falcon_model_load: qntvr     = 0
falcon_model_load: ggml ctx size = 3872.64 MB
falcon_model_load: memory_size =    32.00 MB, n_mem = 65536
falcon_model_load: ........................ done
falcon_model_load: model size =  3872.59 MB / num tensors = 196

**********************************************

Sunspots are dark, circular regions on the surface of our star, the Sun. They appear during periods of high solar activity and can vary in size from just a few miles across to hundreds of thousands of miles wide.

Scientists believe that sunspots form when magnetic fields within the Sun's atmosphere become unstable due to changes in temperature or pressure. This instability causes material on the surface of the Sun to be ejected into space, creating a dark region known as a "coronal hole." The expelled matter cools and solidifies rapidly once it reaches Earth's upper atmosphere, forming sunspots.

Sunspots are not always visible from Earth due to their location within our star's magnetic field lines. However, they can be seen during periods of high solar activity when the Sun's surface becomes more active with prominences and flares.

Scientists use observations of sunspots to study various aspects of our star's behavior, including its internal workings and interactions with other celestial bodies in space. By studying these regions on the Sun's surface, we can gain a better understanding of how our star generates energy and interacts with Earth and other planets within our solar system.
**********************************************


         ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ 
        Elapsed Time to respond to user prompt was: 73.84711904602591 seconds


**********************************************

        Type: END   and hit enter to exit the program...

        Commandline Instructions: 
Type in your prompt/question as a single statement with no return characters... 
(only hit enter for the purpose of submitting your question)

**********************************************


        What is your question? (prompt):        what are sun spots?

Found a match! -->
 Document {'id': 'prompt:tllmbtsnspts:2093', 'payload': None, 'knn_dist': '0.0604999661446', 'response_key': 'prompt:response:7'}

keyname of cached response: prompt:response:7

**********************************************

Sunspots are dark, circular regions on the surface of our star, the Sun. They appear during periods of high solar activity and can vary in size from just a few miles across to hundreds of thousands of miles wide.

Scientists believe that sunspots form when magnetic fields within the Sun's atmosphere become unstable due to changes in temperature or pressure. This instability causes material on the surface of the Sun to be ejected into space, creating a dark region known as a "coronal hole." The expelled matter cools and solidifies rapidly once it reaches Earth's upper atmosphere, forming sunspots.

Sunspots are not always visible from Earth due to their location within our star's magnetic field lines. However, they can be seen during periods of high solar activity when the Sun's surface becomes more active with prominences and flares.

Scientists use observations of sunspots to study various aspects of our star's behavior, including its internal workings and interactions with other celestial bodies in space. By studying these regions on the Sun's surface, we can gain a better understanding of how our star generates energy and interacts with Earth and other planets within our solar system.
**********************************************


         ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ 
        Elapsed Time to respond to user prompt was: 0.01595835798070766 seconds


**********************************************

        Type: END   and hit enter to exit the program...

        Commandline Instructions: 
Type in your prompt/question as a single statement with no return characters... 
(only hit enter for the purpose of submitting your question)

**********************************************
```



#### Other less interesting - yet hopefully useful examples are in the same directory
#### Here is a sample run of redisvl_1.py with results:
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
