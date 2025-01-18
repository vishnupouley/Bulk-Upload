from datetime import date
from pydantic import BaseModel
from pandas import DataFrame

from bulkupload.models import UsersModel


class Users(BaseModel):
    user_id: str
    user_name: str
    email: str
    business_unit: str
    department: str
    date_of_joining: date
    mobile_number: str


def save_bulk_data(data_frame: DataFrame | None) -> list[Users]:
    if data_frame is not None:
        # Standardize column names

        # Map DataFrame columns to model fields
        column_mapping: dict[str, str] = {
            'User ID': 'user_id',
            'User Name': 'user_name',
            'Email': 'email',
            'Business Unit': 'business_unit',
            'Department': 'department',
            'Date of Joining': 'date_of_joining',
            'Mobile Number': 'mobile_number'
        }
        data_frame.rename(columns=column_mapping, inplace=True, errors='ignore')

        # Filter out existing users
        existing_user_ids: set[str] = set(UsersModel.objects.values_list('user_id', flat=True))
        data_frame = data_frame[~data_frame['user_id'].isin(existing_user_ids)]

        # Create user instances
        users_to_create: list[UsersModel] = [UsersModel(**row) for row in data_frame.to_dict(orient='records')]
        UsersModel.objects.bulk_create(users_to_create)

        return [Users(**user) for user in UsersModel.objects.values()]
    return [Users(**user) for user in UsersModel.objects.values()]
