from pymongo import MongoClient
uri = "mongodb+srv://hanpinilla_db_user:Admin_2026@cluster0.71rjuur.mongodb.net/"
client = MongoClient(uri)
try:
    client.admin.command("ping")
    print("Connected successfully")
    client.close()

except Exception as e:
    raise Exception(
        "The following error occurred: ", e)