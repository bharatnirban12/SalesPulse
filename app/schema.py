from pydantic import BaseModel

class PredictionInput(BaseModel):
    store_nbr: int
    family: str
    date: str

class ForecastInput(BaseModel):
    store_nbr: int
    family: str
    start_date: str
    weeks: int = 1

class BatchForecastInput(BaseModel):
    weeks: int = 1
    limit: int = 1000
    summary: bool = False