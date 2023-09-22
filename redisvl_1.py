from redisvl.index import SearchIndex
from redisvl.query import VectorQuery
from redisvl.query.filter import Tag,Num
from redisvl.index import SearchIndex
import yaml,sys,getopt,random 
import numpy as np

def load_schema_definition():
    #Get the schema definition loaded from the yaml file:
    with open('schema.yaml', 'r') as file:
        search_schema = yaml.safe_load(file)
    print()
    print(type(search_schema))
    return search_schema

def initialize_redis_index(host,port,search_schema):
    # initialize the connection to Redis
    connection_string = "redis://"+host+":"+port
    index = SearchIndex.from_dict(search_schema)
    index.connect(connection_string)
    return index

def create_index(index):
    index.create(overwrite=True)
    
def create_data():
# create some dummy data: (can be called repeatedly to generate more data)
    sm=random.randint(1,5)
    a=random.randint(3,4)
    b=random.randint(7,21)
    c=random.randint(3,4)
    d=random.randint(8,21)
    e=random.randint(3,4)
    f=random.randint(10,21)
    sc1=(a+b)/(25*a)
    sc2=(c+d)/(30*a)
    sc3=(e+f)/(30*sm)
    sc4=(a+b)/(30*c)
    sc5=(c+d)/(30*c)
    sc6=(e+f)/(30*sm)
    sc7=(a+b)/(40*a)
    sc8=(c+d)/(25*e)
    sc9=(e+f)/(25*sm)
    data = [
        {
            "id": 1,
            "user": "john",
            "age": a*b,
            "job": "engineer",
            "credit_score": "high",
            "user_embedding": np.array([sc1, sc2, sc3], dtype=np.float32).tobytes(),
        },
        {
            "id": 2,
            "user": "mary",
            "age": c*d,
            "job": "doctor",
            "credit_score": "low",
            "user_embedding": np.array([sc4, sc5, sc6], dtype=np.float32).tobytes(),
        },
        {
            "id": 3,
            "user": "joe",
            "age": e*f,
            "job": "dentist",
            "credit_score": "medium",
            "user_embedding": np.array([sc7, sc8, sc9], dtype=np.float32).tobytes(),
        },
    ]

    print("Dummy Data created! - here is a sample of one of the elements and it's length:")
    print([value for value in data[1].values()][5])
    print()
    print(len([value for value in data[1].values()][5]))
    print()
    return data

# load data into the index in Redis (list of dicts)
def load_data(index,data):
    index.load(data)

def do_search_query(index):
    coin=random.randint(1,2)
    t_low = Tag("credit_score") == "low"
    t_high = Tag("credit_score") == "high"
    low = Num("age") >= 40
    high = Num("age") <= 45
    if(coin==1):
        combined = t_low | t_high
    elif(coin==2):
        combined = low & high 
    query = VectorQuery(
        vector=[0.1, 0.15, 0.5],
        vector_field_name="user_embedding",
        return_fields=["user", "age", "job", "credit_score"],
        filter_expression=combined,
        num_results=200,
    )
    print(f'\n\tISSUING THIS QUERY: \n{query}\n')
    results = index.query(query)
    print(f'\nQuery Results have a length of {len(results)}')
    return results

if __name__ == "__main__":
    # TODO: edit or supply as args the host and port to match your redis database endpoint:
    host="localhost"
    port="6379"
    createNewIndex = False
    loadData = False
    testQuery = False
    user_choice ='n'
    argv = sys.argv[1:] # skip the name of this script
    opts,args = getopt.getopt(argv,"h:p:c:l:t:", 
                                   ["host =",
                                    "port =",
                                    "create_new_index =",
                                    "load_data =",
                                    "test_query ="
                                    ]) 
    for opt,arg in opts:
        if opt in ['-h','-host']:
            host = arg
        elif opt in ['-p','-port']:
            port = arg
        elif opt in ['-c','--create_new_index']:
            user_choice = arg
            print(f'user_choice for {opt} == {user_choice}')                 
            if user_choice == 'y':
                 print(f'user_choice for {opt} == {user_choice}')
                 createNewIndex = True
        elif opt in ['-l','--load_data']:
            user_choice = arg
            if user_choice == 'y':
                 print(f'user_choice for {opt} == {user_choice}')
                 loadData = True
        elif opt in ['-t','--test_query']:
            user_choice = arg
            if user_choice =='y':
                print(f'user_choice for {opt} == {user_choice}')
                testQuery = True            
    if len(sys.argv)<6:
        print('\nPlease supply a hostname & port for your target Redis instance:\n')
        print('\n\tYour options are: ')
        print('-h <host> -p <port> -create_new_index y/n -load_data y/n -test_query y/n')
        print('(unassigned options default to not being enabled)')
        exit(0)
    if len(sys.argv)>5:
        try:
            search_schema = load_schema_definition()
            print("search_schema loaded")
            print(f"\nconnecting to: host={host} port={port} ...")
            rindex = initialize_redis_index(host,port,search_schema)
            if createNewIndex:
                print('creating a new index in redis...')
                create_index(rindex)
            if loadData:
                print('loading data into redis...')
                load_data(rindex,create_data())
            if testQuery:
                print('Executing a test query against the redis search index...\n\tRESULT:\n')
                qresults = do_search_query(rindex)
                for r in qresults:
                    print(f'\nRESULT:\n {r}')
                print('\n\nexiting ...')
        except Exception as e:
            print(f'You may need more data loaded,\n or... You may need to provide different command line arguments for your host and port, etc')
            print(e)
