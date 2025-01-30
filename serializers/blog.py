# one document
def DecodeBlog(doc) -> dict:
    return {
        "_id" : str(doc["_id"]) ,
        "title" : doc["title"] ,
        "sub_title" : doc["sub_title"] ,
        "content" : doc["content"] ,
        "author" : doc["author"] ,
        "date" : doc["date"] ,
    }

# all blogs in list
def DecodeBlogs(docs) -> list:
    return [DecodeBlog(doc) for doc in docs]


