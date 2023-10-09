from redisvl.index import SearchIndex
import time,redis 
from redis.commands.search.query import Query
import yaml,sys,getopt,random 
import numpy as np

def load_schema_definition():
    #Get the schema definition loaded from the yaml file:
    with open('business.yaml', 'r') as file:
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

def initialize_redis_index_with_password(host,port,search_schema,password):
    # initialize the connection to Redis
    #redis://user123:pass123@my-web.cache.amazonaws.com:6379
    connection_string = "redis://default:"+password+"@"+host+":"+port
    #connection_string = "rediss://default:Tw6ILWm45CnQ36Iuu9HeGkmLuNm96vEOz8e818yd4Mw=@redisDB.southcentralus.redisenterprise.cache.azure.net:10000"    
    index = SearchIndex.from_dict(search_schema)
    index.connect(connection_string)
    return index

def create_index(index):
    index.create(overwrite=True)

def delete_business_record(business_key,host,port):
    business_store = redis.from_url("redis://"+host+":"+port)
    business_store.delete(business_key)
    print('\t\t!!Business Record Removed From Redis!!')

def delete_business_record_with_password(business_key,host,port,password):
    business_store = redis.from_url("redis://default:"+password+"@"+host+":"+port)
    business_store.delete(business_key)
    print('\t\t!!Business Record Removed From Redis!!')

def make_business_embedding_from_attributes(anchorX,anchorY):
    anchorX=int(anchorX)
    anchorY=int(anchorY)
    # make sure business fits in our small grid 10x10:
    if anchorX<2:
        anchorX = 2
    if anchorX>8:
        anchorX = 8
    if anchorY<1:
        anchorY = 1
    if anchorY>4:
        anchorY = 4
    anchor_point=anchorX+(anchorY*10)
    print(f' Target generated business has anchor_point of {anchorX+(anchorY*10)}')
    # picture a grid w/ 100 squares (10x10) <-- this is a quadrant
    # each business stored in redis belongs to a quadrant (this is the expected context)
    # for each square, place a zero if the business does not overlap it
    # ^ place a 1 if the business overlaps that square
    # the grid is flattened to a single array of 100 elements
    # x=2, y=2 would live at element (x)+(y*10)  or: 12
    # x=9, y=4 would live at element (x)+(y*10)  or: 49
    # starting from that anchor point - mark other occupied squares 
    # All businesses must fit in a quadrant
    # anchor values for y must be lower than 4
    # anchor values for x must be between 2 and 8
    # 1 square wide at their anchor point and 2 more on the Y axis 
    # 3 squares wide from the 3rd through the 5th on the y axis
    # 1 square wide for 2 more squares on the y axis
    #           []        <-- anchor_point + 60
    #           []        <-- anchor_point + 50
    #         [][][]      <-- anchor_point + 39,40,41
    #         [][][]      <-- anchor_point + 29,30,31
    #         [][][]      <-- anchor_point + 19,20,21
    #           []        <-- anchor_point + 10
    #           []        <-- anchor_point
    business_points=[anchor_point,anchor_point+10,anchor_point+19,
                 anchor_point+20,anchor_point+21,anchor_point+29,
                 anchor_point+30,anchor_point+31,anchor_point+39,
                 anchor_point+40,anchor_point+41,anchor_point+50,
                 anchor_point+60]
    business_list=[]

    for point in range(1,101):
        if point in business_points:
            business_list.append(1.0)
        else:
            business_list.append(0.0)

    for y in range(0,10):
        print("|",end="")
        for x in range(0,10):
            if business_list[x+(y*10)]>0:
                print('[ ]',end="")
            else:
                print(' * ',end="")
        print(" |")
    thing = np.array(business_list, dtype=np.float32).tobytes()
    return (thing)

# the user provides the anchor points and 
# quadrant: from 1 to 10 in this simple model when looking for a match

# this function generates a business for a random quadrant with a random anchor
def create_data():
# create some dummy data: (can be called repeatedly to generate more data)
    # Each business takes up some portion of 100 points in a 2d matrix 
    # the grid and business within it has an assigned quadrant 
    # there are 10 possible quadrants for now
    # (that could someday become a Lat/Long and use Redis geospatial query)
    business_id = time.clock_gettime_ns(time.CLOCK_MONOTONIC)
    business_category =['restaurant','fastfood','manicure','haircut','beauty','grocery','automotive','collectibles','crafts','decor','toys','bags','belts','wallets','hats','jewellry','scarves','sunglasses','lingerie','pants','skirts','cellphones','cameras','food','bath','medicine','vitamins','tools','supplies','furniture','gardening','kitchen','pets','rugs','linens','adult','orthotics','prosthetics','office','football','snowboarding','swimming','household']
    name_prefix = ['LUCKY ','DAVE PRESENTS ','DISCOUNT ','QUALITY ','LUXURY ','FANTASTIC ']
    anchorX = (random.randint(2,8))
    anchorY = (random.randint(1,4))
    quadrant = (random.randint(1,10))
    anchorpoint = anchorX+(10*anchorY)
    random_category = random.randint(0,42)
    data = [
        {
            "expected_location": f'117.1{random.randint(100,1000)},32.7{random.randint(0,900)}',
            "anchorpoint": anchorpoint,
            "business_name": f'{name_prefix[random.randint(0,5)]}{business_category[random_category]}',
            "quadrant": quadrant,
            "business_id": business_id,
            "business_category": business_category[random_category],
            "coordinates_embedding": make_business_embedding_from_attributes(anchorX,anchorY),
        },
    ]

    print("business shape_and_attributes created! - here is a visualization of one of the business embeddings:")
    print([value for value in data[0].values()][3])
    print()
    return data

# load data into the index in Redis (list of dicts)
def load_data(index,data):
    index.load(data)

# this function executes the VSS search call against Redis
# it accepts a redis index (generated by calling connection)
def vec_search(index,quadrant,query_vector_as_bytes):
    # KNN 10 specifies to return only up to 10 nearest results (could be unrelated)
    # VECTOR_RANGE specifies the prompts must be similar
    #.sort_by(f'knn_dist') #asc is default order
    query =(
        Query(f'(@quadrant:[{quadrant},{quadrant}] @business_embedding:[VECTOR_RANGE .09 $vec_param]=>{{$yield_distance_as: range_dist}})=>[KNN 10 @business_embedding $knn_vec]=>{{$yield_distance_as: knn_dist}}')
        .sort_by(f'knn_dist') #asc is default order
        .return_fields("business_name","expected_location","quadrant","business_category","business_id","knn_dist")
        .dialect(2)
    )
    res = index.search(query, query_params = {'vec_param': query_vector_as_bytes, 'knn_vec': query_vector_as_bytes})
    return res.docs

# start with an anchor point for each business
# anchor values fall between 200,501 and 500,1100
def do_search_query(index,anchorX,anchorY,quadrant):
    print(f'query is--> \nquadrant is {quadrant}')
    print(f'anchorX == {anchorX}  anchorY == {anchorY} ')
    vector=make_business_embedding_from_attributes(anchorX,anchorY)
    results = vec_search(index=index,quadrant=quadrant,query_vector_as_bytes=vector)
    print(f'\nQuery Results have a length of {len(results)}')
    return results

# python3 Business_Search.py -h redis-12144.c309.us-east-2-1.ec2.cloud.redislabs.com -p 12144 -s WqedzS2orEF4Dh0baBeaRqo16DrYYxzIo1 -c y -l y -t y
# python3 Business_Search.py -h redis-12000.homelab.local -p 12000 -c y -l y -t y
# python3 Business_Search.py -h e10mods.centralus.redisenterprise.cache.azure.net -p 10000 -s zCRAJicy3XtEp1YfACM+P3kodoSqviXFeVFhwy1gSP0o1= -c n -l n -t y
if __name__ == "__main__":
    print(f'MAIN FUNCTION CALLED')
    # TODO: edit or supply as args the host and port to match your redis database endpoint:
    host="localhost"
    port="6379"
    password = ""
    username ="default"
    createNewIndex = False
    loadData = False
    testQuery = False
    user_choice ='n'
    argv = sys.argv[1:] # skip the name of this script
    opts,args = getopt.getopt(argv,"h:p:s:u:c:l:t:e:", 
                                   ["host =",
                                    "port =",
                                    "password =",
                                    "username =",
                                    "create_new_index =",
                                    "load_data =",
                                    "test_query =",
                                    "explain_gameplay ="
                                    ]) 
    for opt,arg in opts:
        if opt in ['-h','-host']:
            host = arg
        elif opt in ['-p','-port']:
            port = arg
        elif opt in ['-s','-secret_password']:
            password = arg
        elif opt in ['-u','-username']:
            username = arg
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
        #try:
            search_schema = load_schema_definition()
            print("search_schema loaded")
            print(f"\nconnecting to: host={host} port={port} ...")
            if password=="":
                rindex = initialize_redis_index(host,port,search_schema)
            else:
                rindex = initialize_redis_index_with_password(host,port,search_schema,password)    
            if createNewIndex:
                print('creating a new index in redis...')
                create_index(rindex)
            if loadData:
                print('loading data into redis...')
                load_data(rindex,create_data())
            if testQuery:
                print('Executing a test query against the redis search index...\n\tRESULT:\n')
                anchorX = input("enter an integer between 2 and 8 for target X coordinate :   ")
                anchorY = input("enter an integer between 1 and 4 for target Y coordinate :   ")
                quadrant = input("enter an integer between 1 and 10 for target quadrant :   ")
                qresults = do_search_query(index=rindex,anchorX=anchorX,anchorY=anchorY,quadrant=quadrant)
                hit_counter = 0
                for r in qresults:
                    print(f'\nYou found a business! ...:\n {r}')
                    removeit = input(f'\nShould we delete that business record (remove it from Redis)? Y/N :')
                    if removeit=="Y" and password=="":
                        delete_business_record(business_key=r.id,host=host,port=port)
                    elif removeit=="Y" and password!="":
                         delete_business_record_with_password(business_key=r.id,host=host,port=port,password=password)
                    hit_counter=hit_counter+1
                if hit_counter == 0:
                    print("You have not found a match for that business")
                print('\n\nexiting ...')
        #except Exception as e:
         #   print(f'You may need more data loaded,\n or... You may need to provide different command line arguments for your host and port, etc')
          #  print(e)
