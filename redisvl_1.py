from redisvl.index import SearchIndex
from redisvl.query import VectorQuery
import yaml
import numpy as np

#Get the schema definition loaded from the yaml file:
with open('schema.yaml', 'r') as file:
    search_schema = yaml.safe_load(file)

print()
print(type(search_schema))
print()
print(search_schema)
print()
# initialize the index and connect to Redis
index = SearchIndex.from_dict(search_schema)
index.connect("redis://192.168.1.20:10400")

# create the index in Redis
#index.create(overwrite=True)

# create some dummy data:
data = [
    {
        "id": 1,
        "user": "john",
        "age": 1,
        "job": "engineer",
        "credit_score": "high",
        "user_embedding": np.array([0.1, 0.1, 0.5], dtype=np.float32).tobytes(),
    },
    {
        "id": 2,
        "user": "mary",
        "age": 2,
        "job": "doctor",
        "credit_score": "low",
        "user_embedding": np.array([0.1, 0.1, 0.5], dtype=np.float32).tobytes(),
    },
    {
        "id": 3,
        "user": "joe",
        "age": 3,
        "job": "dentist",
        "credit_score": "medium",
        "user_embedding": np.array([0.9, 0.9, 0.1], dtype=np.float32).tobytes(),
    },
]

print()
print([value for value in data[1].values()][5])
print()
print(len([value for value in data[1].values()][5]))

print()
# load data into the index in Redis (list of dicts)
#index.load(data)

query = VectorQuery(
    vector=[0.1, 0.1, 0.5],
    vector_field_name="user_embedding",
    return_fields=["user", "age", "job", "credit_score"],
    num_results=1,
)
results = index.query(query)
print(results)
