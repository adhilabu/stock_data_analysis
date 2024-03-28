from datetime import date, time as time_only
from pydantic import BaseModel, Field, validator

def convert_time_to_hh_mm_ss(dt: time_only) -> str:
    return dt.strftime('%H:%M:%S')

def convert_date_to_iso_format(dt: date) -> str:
    return dt.isoformat()

def to_camel(string: str):
    return string.title().replace("_", "")

class RootModel(BaseModel):
    pass

class CamelModel(RootModel):
    class Config:
        alias_generator = to_camel
        populate_by_name = True
        json_encoders = {
            time_only: convert_time_to_hh_mm_ss,
            date: convert_date_to_iso_format
        }
