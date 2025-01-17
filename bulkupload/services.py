from bulkupload.models import UsersModel
from pydantic import BaseModel
import pandas as pd
from pandas import DataFrame


class Users(BaseModel):
    user_id: str
    user_name: str
    email: str
    business_unit: str
    department: str
    date_of_joining: str
    mobile_number: str


def save_bulk_data(data_frame: DataFrame | None) -> list[Users]:
    if data_frame is not None:
        data_frame.columns = [col.lower().replace(' ', '_') for col in data_frame.columns]

        column_mapping: dict[str, str] = {
            'user_id': 'user_id',
            'user_name': 'user_name',
            'email': 'email',
            'business_unit': 'business_unit',
            'department': 'department',
            'date_of_joining': 'date_of_joining',
            'mobile_number': 'mobile_number'
        }
        data_frame.rename(columns=column_mapping, inplace=True, errors='ignore')

        if 'date_of_joining' in data_frame.columns:
            data_frame['date_of_joining'] = pd.to_datetime(data_frame['date_of_joining'], errors='coerce').dt.strftime(
                '%Y-%m-%d')

        existing_user_ids: set[str] = set(UsersModel.objects.values_list('user_id', flat=True))
        data_frame = data_frame[~data_frame['user_id'].isin(existing_user_ids)]

        users_to_create: list[UsersModel] = [UsersModel(**row) for row in data_frame.to_dict(orient='records')]
        UsersModel.objects.bulk_create(users_to_create)

        return [Users(**user) for user in UsersModel.objects.values()]
    return [Users(**user) for user in UsersModel.objects.values()]
