import pymongo
import certifi



mongo_url = "mongodb+srv://carrapril:<Jelisa09>@cluster0.lhcli.mongodb.net/TheFashionOutfits?retryWrites=true&w=majority"

client = pymongo.MongoClient(mongo_url, tlsCAFile=certifi.where())

db = client.get_database("TheFashionOutfits")

