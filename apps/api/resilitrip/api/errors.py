from __future__ import annotations
from uuid import uuid4
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

class ApiProblem(Exception):
    def __init__(self,status_code:int,code:str,message:str,*,retryable:bool=False,field_errors=(),current_trip_version=None,current_catalog_version=None):
        self.status_code=status_code; self.code=code; self.message=message; self.retryable=retryable
        self.field_errors=field_errors
        self.current_trip_version=current_trip_version; self.current_catalog_version=current_catalog_version

def problem_body(request: Request, code: str, message: str, retryable=False, field_errors=(), current_trip_version=None,current_catalog_version=None):
    return {"error":{"code":code,"message":message,"request_id":getattr(request.state,"request_id",f"req_{uuid4().hex}"),
        "retryable":retryable,"field_errors":list(field_errors),"current_trip_version":current_trip_version,"current_catalog_version":current_catalog_version}}

async def api_problem_handler(request:Request,exc:ApiProblem):
    return JSONResponse(status_code=exc.status_code,content=problem_body(request,exc.code,exc.message,exc.retryable,
        field_errors=exc.field_errors,current_trip_version=exc.current_trip_version,current_catalog_version=exc.current_catalog_version))

async def validation_handler(request:Request,exc:RequestValidationError):
    if any(error["type"] == "json_invalid" for error in exc.errors()):
        return JSONResponse(status_code=422, content=problem_body(request, "INVALID_JSON", "The request body is not valid JSON."))
    fields=[]
    for error in exc.errors():
        loc=tuple(item for item in error["loc"] if item not in ("body",))
        error_type=error["type"]
        path="/"+"/".join(map(str,loc))
        code=("MISSING_FIELD" if error_type=="missing" else
              "UNKNOWN_FIELD" if error_type=="extra_forbidden" else
              "INVALID_DISCRIMINATOR" if error_type in {"union_tag_invalid","union_tag_not_found"} else
              "INVALID_MONEY" if "paise" in path and error_type in {"int_type","int_parsing"} else
              "INVALID_TIMEZONE" if error_type=="value_error" and "timezone" in str(error.get("ctx",{})).lower() else
              "VALIDATION_ERROR")
        fields.append({"path":path,"code":code,"message":"Invalid request field.","rejected_value":None})
    return JSONResponse(status_code=422,content=problem_body(request,"VALIDATION_ERROR","The request did not satisfy the API contract.",field_errors=fields))

async def internal_error_handler(request:Request,exc:Exception):
    code="INTERNAL_DATA_INTEGRITY_ERROR" if isinstance(exc,RuntimeError) and str(exc)=="INTERNAL_DATA_INTEGRITY_ERROR" else "INTERNAL_ERROR"
    return JSONResponse(status_code=500,content=problem_body(request,code,"The request could not be completed safely."))
