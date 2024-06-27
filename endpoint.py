from fastapi import FastAPI, APIRouter, HTTPException
from pydantic import BaseModel
from Exp_v2 import Experiment,exp
from Num_v2 import NumberGenerator
from Resp_v2 import process_response,df

from dotenv import main
import os
from typing import Optional


main.load_dotenv()

print(os.getcwd())

# exp=Experiment()

router = APIRouter()

class UserInfoRequest(BaseModel):
    avatar: str
    age: int
    _id: str

class NumberResponse(BaseModel):
    numeros: list[int]
    
class AnswerRequest(BaseModel):
    answer: str


    
trial=0
@router.post("/ado", response_model=NumberResponse)

def handleNumber(request: AnswerRequest,exp): 
    
    '''
    Elegi comentar la linea 16 donde se crea la instancia exp, la idea es inicializar la clase una vez sola,
    por las dudas cree la instancia en el script Exp_v2 y que aca solo se actualize esa instancia.
    '''
    user_resp=request.answer
    aux_list=[0,1,2,3,4,5,6,7,8,9]*2
    random.shuffle(aux_list)
    global trial
    
    if trial<20:
        d1=aux_list[trial]
        generator=NumberGenerator(exp)
        numbers=generator.generate_sequential(d1)
        
    '''
    La intención de esta parte es que los primeros 20 trials, es que primero muestre
    listas basadas en promedios predeterminados sin requerir de la funcion generate_numbers. 
    El problema es que necesito tener contabilizado los trials. Entiendo que de esta manera no va a funcionar porque 
    handle number es una funcion, no sé si definiendo como una variable global alcanza. 
    '''
    else:
        generator = NumberGenerator(exp)
        numbers, d1 = generator.generate_numbers()
        
    trial+=1
    
    process_response(exp, d1, user_resp, numbers)
    
    return NumberResponse(numeros=numbers)
@router.get("/ado-user", response_model=UserInfoRequest)


app = FastAPI()
app.include_router(router, prefix="/ado", tags=["ado"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
