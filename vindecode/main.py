from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Welcome to the Vin Decode Application!"}


@app.get("/lookup/{vin}")
async def lookup(vin: str):
    return {"vin": vin}


@app.get("/remove/{vin}")
async def remove(vin: str):
    return {"remove vin": vin}


@app.get("/export/")
async def export():
    return {"export": "complete"}
