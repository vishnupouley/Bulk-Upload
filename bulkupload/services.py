from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from typing import List, Tuple, Set, Dict
from pydantic import ValidationError
from pandas import DataFrame
import pandas as pd

from bulkupload.schema import Users, ValidationFailure, BulkUploadResult
from bulkupload.models import UsersModel


class BulkUploadService:
    @staticmethod
    def get_empty_result_payload(users_list: List[Users], file_duplicates_count: int = 0, input_empty_after_clean: bool = True) -> BulkUploadResult:
        """Return an empty result payload with the current list of all users."""
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

    @staticmethod
    def clean_dataframe(data_frame: DataFrame) -> DataFrame:
        """Clean and standardize the DataFrame by renaming columns and formatting data."""
        column_mapping = {
            'User ID': 'user_id', 'User Name': 'user_name', 'Email': 'email',
            'Business Unit': 'business_unit', 'Department': 'department',
            'Date of Joining': 'date_of_joining', 'Mobile Number': 'mobile_number'
        }
        missing_columns = [col for col in column_mapping.keys() if col not in data_frame.columns]
        if missing_columns:
            raise ValueError(f"Missing columns: {', '.join(missing_columns)}")

        df = data_frame.rename(columns=column_mapping)
        for field in Users.model_fields.keys():
            if field in df.columns:
                if field == 'date_of_joining':
                    df[field] = df[field].apply(lambda x: pd.to_datetime('1899-12-30') + pd.to_timedelta(x, 'D') 
                        if isinstance(x, (int, float)) and not pd.isna(x) else x)
                else:
                    df[field] = df[field].astype(str).str.strip().replace('nan', '').replace('None', '')

        df['user_id'] = df['user_id'].astype(str).str.strip().replace('nan', '').replace('None', '')
        df = df.dropna(subset=['user_id']).query("user_id != ''")
        return df

    @staticmethod
    def deduplicate_dataframe(df: DataFrame) -> Tuple[DataFrame, int]:
        """Remove duplicates within the DataFrame based on 'user_id' and return the count of removed duplicates."""
        if df.empty:
            return df, 0
        original_count = len(df)
        df_dedup = df.drop_duplicates(subset=['user_id'], keep='first')
        return df_dedup, original_count - len(df_dedup)

    @staticmethod
    def get_existing_user_ids() -> Set[str]:
        """Fetch all existing user IDs from the database."""
        return set(UsersModel.objects.values_list('user_id', flat=True))

    @staticmethod
    def validate_new_users(new_users_df: DataFrame) -> Tuple[List[Users], List[UsersModel], List[ValidationFailure]]:
        """Validate new user data against the Pydantic schema and prepare Django model instances."""
        validated_users = []
        model_instances = []
        failed_rows = []

        for index, row in new_users_df.iterrows():
            row_data = row.to_dict()
            if 'date_of_joining' in row_data and pd.isna(row_data['date_of_joining']):
                row_data['date_of_joining'] = None
            try:
                user = Users.model_validate(row_data)
                validated_users.append(user)
                model_instances.append(UsersModel(**user.model_dump()))
            except ValidationError as e:
                failed_rows.append({
                    "row_index": index + 2,
                    "data": {k: str(v)[:50] for k, v in row_data.items()},
                    "errors": e.errors()
                })
            except Exception as e:
                failed_rows.append({
                    "row_index": index + 2,
                    "data": {k: str(v)[:50] for k, v in row_data.items()},
                    "errors": [{"loc": ["general"], "msg": str(e), "type": "runtime_error"}]
                })

        return validated_users, model_instances, failed_rows

    @staticmethod
    def save_new_users(model_instances: List[UsersModel]) -> int:
        """Bulk create new users in the database and return the count of created users."""
        if not model_instances:
            return 0
        created_objects = UsersModel.objects.bulk_create(model_instances, ignore_conflicts=True)
        return len(created_objects)

    @staticmethod
    def save_bulk_data(data_frame: DataFrame | None) -> BulkUploadResult:
        """Process a DataFrame to bulk upload new users, handling cleaning, deduplication, validation, and saving."""
        if data_frame is None:
            all_users = [Users.model_validate(user) for user in UsersModel.objects.all()]
            return BulkUploadService.get_empty_result_payload(all_users, input_empty_after_clean=False)

        # Clean the input data
        cleaned_df = BulkUploadService.clean_dataframe(data_frame)
        if cleaned_df.empty:
            all_users = [Users.model_validate(user) for user in UsersModel.objects.all()]
            return BulkUploadService.get_empty_result_payload(all_users, input_empty_after_clean=True)

        # Deduplicate within the file
        dedup_df, duplicates_removed = BulkUploadService.deduplicate_dataframe(cleaned_df)
        if dedup_df.empty:
            all_users = [Users.model_validate(user) for user in UsersModel.objects.all()]
            return BulkUploadService.get_empty_result_payload(all_users, file_duplicates_count=duplicates_removed, input_empty_after_clean=True)

        # Filter out existing users
        existing_user_ids = BulkUploadService.get_existing_user_ids()
        new_users_df = dedup_df[~dedup_df['user_id'].isin(existing_user_ids)]
        attempted_new_rows_count = len(new_users_df)
        all_users_in_file_existed = len(dedup_df) > 0 and attempted_new_rows_count == 0

        if attempted_new_rows_count == 0:
            all_users = [Users.model_validate(user) for user in UsersModel.objects.all()]
            return {
                "successful_users": [],
                "failed_rows": [],
                "newly_created_count": 0,
                "total_users_after_upload": all_users,
                "attempted_new_rows_count": 0,
                "all_users_in_file_existed": all_users_in_file_existed,
                "input_data_was_empty_after_cleaning": False,
                "file_internal_duplicates_removed_count": duplicates_removed
            }

        # Validate new users
        validated_users, model_instances, failed_rows = BulkUploadService.validate_new_users(new_users_df)
        if failed_rows:
            return {
                "successful_users": [],
                "failed_rows": failed_rows,
                "newly_created_count": 0,
                "total_users_after_upload": [],
                "attempted_new_rows_count": attempted_new_rows_count,
                "all_users_in_file_existed": False,
                "input_data_was_empty_after_cleaning": False,
                "file_internal_duplicates_removed_count": duplicates_removed
            }

        # Save new users
        newly_created_count = BulkUploadService.save_new_users(model_instances)
        all_users_after_upload = [Users.model_validate(user) for user in UsersModel.objects.all()]

        return {
            "successful_users": validated_users if newly_created_count > 0 else [],
            "failed_rows": [],
            "newly_created_count": newly_created_count,
            "total_users_after_upload": all_users_after_upload,
            "attempted_new_rows_count": attempted_new_rows_count,
            "all_users_in_file_existed": False,
            "input_data_was_empty_after_cleaning": False,
            "file_internal_duplicates_removed_count": duplicates_removed
        }

    @staticmethod
    def get_paginated_users(page_number: int, per_page: int) -> Dict:
        """Fetch and paginate users from the database."""
        user_queryset = UsersModel.objects.all().order_by('user_id')
        paginator = Paginator(user_queryset, per_page)
        try:
            users_page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            users_page_obj = paginator.page(1)
        except EmptyPage:
            users_page_obj = paginator.page(paginator.num_pages)

        pydantic_users_list = [Users.model_validate(user) for user in users_page_obj.object_list]

        return {
            'users': pydantic_users_list,
            'page': users_page_obj,
            'per_page': per_page,
            'total_users': paginator.count,
            'has_previous': users_page_obj.has_previous(),
            'previous_page_number': users_page_obj.previous_page_number() if users_page_obj.has_previous() else users_page_obj.number,
            'has_next': users_page_obj.has_next(),
            'next_page_number': users_page_obj.next_page_number() if users_page_obj.has_next() else users_page_obj.number,
        }
