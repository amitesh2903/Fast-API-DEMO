from fastapi import APIRouter 
import logging
entry_root = APIRouter()

@entry_root.get("/")
def apiRunning():
    logging.info("Api is running")
    res = {
        "status" : "ok" ,
        "message" : "Api is runinng"
    }
    return res