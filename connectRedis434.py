from langchain.vectorstores import Redis
from langchain.embeddings import OpenAIEmbeddings
# export REDIS_URL="rediss://<USER>:<PASSWORD>@<HOST>:<PORT>?ssl_ca_certs=<redis_ca.pem>&ssl_certfile=<redis_user.crt>&ssl_keyfile=<redis_user_private.key>&ssl_cert_reqs=required"
# make sure to use the absolute paths to the three required files (assuming client auth enabled)
#url_connection = Redis.from_url("redis://localhost:6379?ssl_cert_reqs=none&decode_responses=True&health_check_interval=2")

REDIS_URL="rediss://default:Tw6ILWm45CnQ36Iuu9HeGkmLuNm96vEOz8e818yd4Mw=@redisDB.southcentralus.redisenterprise.cache.azure.net:10000"
url_connection = Redis.from_url(REDIS_URL)
url_connection.set("test","popquiz")


