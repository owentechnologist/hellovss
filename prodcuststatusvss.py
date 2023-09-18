from redisvl.index import SearchIndex
from redisvl.query import VectorQuery
from redisvl.query.filter import Tag,Text,Num
from redisvl.index import SearchIndex
import yaml,sys,getopt,random 
import numpy as np

def load_schema_definition():
    #Get the schema definition loaded from the yaml file:
    with open('prodcuststat_schema.yaml', 'r') as file:
        search_schema = yaml.safe_load(file)
    print()
    print(type(search_schema))
    return search_schema

def initialize_redis_index(host,port,search_schema):
    # initialize the connection to Redis
    #connection_string = "redis://"+host+":"+port
    connection_string = "rediss://default:Tw6ILWm45CnQ36Iuu9HeGkmLuNm96vEOz8e818yd4Mw=@redisDB.southcentralus.redisenterprise.cache.azure.net:10000"    
    index = SearchIndex.from_dict(search_schema)
    index.connect(connection_string)
    return index

def create_index(index):
    index.create(overwrite=True)
    
def create_data():
# create some dummy data: (can be called repeatedly to generate more data)
    # a strict matching between product category IDs and human values (utensils,hats) should exist:
    # for now, let's assume they just get numbers limited to 10k variants:
    prodCatID = (random.randint(1,10000)/100000)
    # custIDs are numbers limited to 100K variants
    custID = (random.randint(1,100000)/1000000)
    #statuses: 011 == new, 021 == accepted, 031 ==  processing, 041 == shipped, 051 == delivered,061 == damaged, 071 == cancelled
    # to create a status randomly generate value 1-7 divide by 100
    status = (random.randint(1,7)/100)
    datatimestamp = 1633955921695+(100*(random.randint(1,100000000))) 
    data = [
        {
            "datetimes": str(datatimestamp),
            "prodcuststat_embed": np.array([prodCatID, custID, status], dtype=np.float32).tobytes(),
        },
    ]

    print("Dummy Data created! - here is a sample of one of the elements and it's length:")
    print([value for value in data[0].values()][1])
    print()
    print(len([value for value in data[0].values()][1]))
    print()
    return data

# load data into the index in Redis (list of dicts)
def load_data(index,data):
    index.load(data)

def do_search_query(index,status):
    prodcatid = (random.randint(1,10000)/100000)
    custid = (random.randint(1,100000)/1000000)
    status= (int(status)/100)
    dts = 1633956000000+(100*(random.randint(1,100000000))) 

    filterexpres = Num("datetimes") >= dts
    print(f'query is--> productCategoryID: {prodcatid*100000}, status: {status*100}, custID is {custid*1000000}')
    query = VectorQuery(
        vector=[prodcatid,custid,status],
        vector_field_name="prodcuststat_embed",
        return_fields=["orderid", "datetimes"],
        filter_expression=filterexpres,
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
                orderStatus = input("enter a status from 1 to 7 :   ")
                qresults = do_search_query(rindex,orderStatus)
                for r in qresults:
                    print(f'\nRESULT:\n {r}')
                print('\n\nexiting ...')
        except Exception as e:
            print(f'You may need more data loaded,\n or... You may need to provide different command line arguments for your host and port, etc')
            print(e)
