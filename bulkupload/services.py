from pydantic import ValidationError
from pandas import DataFrame
from typing import List
import pandas as pd

from bulkupload.models import UsersModel
from bulkupload.schema import Users, ValidationFailure, BulkUploadResult  # Pydantic schema


def get_empty_result_payload(users_list: List[Users],  # For total_users_after_upload
                             file_duplicates_count: int = 0,
                             input_empty_after_clean: bool = True) -> BulkUploadResult:
    return {
        "successful_users": [],
        "failed_rows": [],
        "newly_created_count": 0,
        "total_users_after_upload": users_list,
        "attempted_new_rows_count": 0,
        "all_users_in_file_existed": False,
        "input_data_was_empty_after_cleaning": input_empty_after_clean,
        "file_internal_duplicates_removed_count": file_duplicates_count
    }


def save_bulk_data(data_frame: DataFrame | None) -> BulkUploadResult:
    file_internal_duplicates_removed_count = 0  # Initialize

    if data_frame is None:
        all_users_from_db_qs = UsersModel.objects.all()
        pydantic_users = [Users.model_validate(
            user) for user in all_users_from_db_qs]
        payload = get_empty_result_payload(
            pydantic_users, input_empty_after_clean=False)
        return payload

    column_mapping: dict[str, str] = {
        'User ID': 'user_id', 'User Name': 'user_name', 'Email': 'email',
        'Business Unit': 'business_unit', 'Department': 'department',
        'Date of Joining': 'date_of_joining', 'Mobile Number': 'mobile_number'
    }

    # --- Validate and clean columns ---
    missing_source_columns = [src_col for src_col in column_mapping.keys(
    ) if src_col not in data_frame.columns]
    if missing_source_columns:
        raise ValueError(
            f"Missing columns in Excel file: {', '.join(missing_source_columns)}. Expected: {', '.join(column_mapping.keys())}")

    data_frame.rename(columns=column_mapping, inplace=True)

    for field_name in Users.model_fields.keys():
        if field_name in data_frame.columns:
            if field_name == 'date_of_joining':
                def convert_excel_date(val):
                    if isinstance(val, (int, float)) and not pd.isna(val):
                        try:
                            return pd.to_datetime('1899-12-30') + pd.to_timedelta(val, 'D')
                        except:
                            return val
                    return val
                data_frame[field_name] = data_frame[field_name].apply(
                    convert_excel_date)
            else:
                data_frame[field_name] = data_frame[field_name].astype(str).str.strip(
                ).replace('nan', '', regex=False).replace('None', '', regex=False)

    if 'user_id' in data_frame.columns:
        data_frame['user_id'] = data_frame['user_id'].astype(str).str.strip().replace(
            'nan', '', regex=False).replace('None', '', regex=False)
        data_frame.dropna(subset=['user_id'], inplace=True)
        data_frame = data_frame[data_frame['user_id'] != '']
    else:
        raise ValueError(
            "Critical error: 'user_id' column not found after renaming and cleaning.")

    if data_frame.empty:
        all_users_from_db_qs = UsersModel.objects.all()
        pydantic_users = [Users.model_validate(
            user) for user in all_users_from_db_qs]
        return get_empty_result_payload(pydantic_users, input_empty_after_clean=True)

    # --- Deduplicate rows within the uploaded file based on 'user_id' ---
    if 'user_id' in data_frame.columns and not data_frame.empty:  # Check again as user_id column is critical
        original_row_count_before_file_dedup = len(data_frame)
        data_frame.drop_duplicates(
            subset=['user_id'], keep='first', inplace=True)
        file_internal_duplicates_removed_count = original_row_count_before_file_dedup - \
            len(data_frame)

    if data_frame.empty:  # If empty after file-internal deduplication
        all_users_from_db_qs = UsersModel.objects.all()
        pydantic_users = [Users.model_validate(
            user) for user in all_users_from_db_qs]
        return get_empty_result_payload(pydantic_users,
                                        file_duplicates_count=file_internal_duplicates_removed_count,
                                        input_empty_after_clean=True)  # Technically became empty after deduplication

    # --- Filter Existing Users (from DB) ---
    existing_user_ids: set[str] = set(
        UsersModel.objects.values_list('user_id', flat=True))
    new_users_df = data_frame[~data_frame['user_id'].isin(
        existing_user_ids)].copy()

    attempted_new_rows_count = len(new_users_df)
    all_users_in_file_existed_flag = (not data_frame.empty) and (
        attempted_new_rows_count == 0)  # data_frame here is after file dedup

    if attempted_new_rows_count == 0:
        all_users_from_db_qs = UsersModel.objects.all()
        pydantic_users = [Users.model_validate(
            user) for user in all_users_from_db_qs]
        return {
            "successful_users": [], "failed_rows": [], "newly_created_count": 0,
            "total_users_after_upload": pydantic_users,
            "attempted_new_rows_count": 0,
            "all_users_in_file_existed": all_users_in_file_existed_flag,
            # Data was not empty, just all existed or was already unique in file
            "input_data_was_empty_after_cleaning": False,
            "file_internal_duplicates_removed_count": file_internal_duplicates_removed_count
        }

    users_to_create_django_instances: list[UsersModel] = []
    successfully_validated_pydantic_users: List[Users] = []
    failed_validation_rows: List[ValidationFailure] = []

    for index, row in new_users_df.iterrows():  # new_users_df is now de-duplicated from file and DB
        row_data = row.to_dict()
        if 'date_of_joining' in row_data and pd.isna(row_data['date_of_joining']):
            row_data['date_of_joining'] = None
        try:
            validated_pydantic_user = Users.model_validate(row_data)
            django_model_data = validated_pydantic_user.model_dump()
            users_to_create_django_instances.append(
                UsersModel(**django_model_data))
            successfully_validated_pydantic_users.append(
                validated_pydantic_user)
        except ValidationError as e:
            failed_validation_rows.append({
                "row_index": index + 2,
                "data": {k: str(v)[:50] for k, v in row_data.items()},
                "errors": e.errors()
            })
        except Exception as e:
            failed_validation_rows.append({
                "row_index": index + 2, "data": {k: str(v)[:50] for k, v in row_data.items()},
                "errors": [{"loc": ["general"], "msg": str(e), "type": "runtime_error"}]
            })

    if failed_validation_rows:
        return {
            "successful_users": [],
            "failed_rows": failed_validation_rows,
            "newly_created_count": 0,
            "total_users_after_upload": [],
            "attempted_new_rows_count": attempted_new_rows_count,
            "all_users_in_file_existed": False,
            "input_data_was_empty_after_cleaning": False,
            "file_internal_duplicates_removed_count": file_internal_duplicates_removed_count
        }

    newly_created_django_users_count = 0
    if users_to_create_django_instances:
        # Using ignore_conflicts=True can be helpful for race conditions if user_id has a unique constraint.
        # It means the count of created_objects might be less than len(users_to_create_django_instances)
        # if a conflict is silently ignored by the database.
        created_objects = UsersModel.objects.bulk_create(
            users_to_create_django_instances, ignore_conflicts=True)
        newly_created_django_users_count = len(created_objects)

    all_users_from_db_after_upload_qs = UsersModel.objects.all()
    final_pydantic_user_list = [Users.model_validate(
        user) for user in all_users_from_db_after_upload_qs]

    # Filter successfully_validated_pydantic_users to only those that were likely created
    # This is an approximation if IDs are not easily matched back from 'created_objects' to 'successfully_validated_pydantic_users'
    # For simplicity, we'll keep 'successfully_validated_pydantic_users' as those that passed validation and were attempted.
    # The 'newly_created_count' reflects actual DB inserts.

    return {
        "successful_users": successfully_validated_pydantic_users if newly_created_django_users_count > 0 else [],
        "failed_rows": failed_validation_rows,
        "newly_created_count": newly_created_django_users_count,
        "total_users_after_upload": final_pydantic_user_list,
        "attempted_new_rows_count": attempted_new_rows_count,
        "all_users_in_file_existed": False,
        "input_data_was_empty_after_cleaning": False,
        "file_internal_duplicates_removed_count": file_internal_duplicates_removed_count
    }
