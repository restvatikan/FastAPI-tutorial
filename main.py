from enum import Enum

from fastapi import FastAPI
#여긴 main branch의 파일
# str을 상속하면 ModelName의 멤버를 str처럼 사용 가능(.value 생략 가능)
# Enum을 상속하면 ModelName에 존재하지 않는 멤버 접근 시 에러 출력
class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

app = FastAPI()

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}

# :path 붙이면 /home/johndoe/myfile.txt와 같은 경로도 처리 가능
# http://127.0.0.1:8000/files//home/johndoe/myfile.txt
# 이중 슬래시
@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}

