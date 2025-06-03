from datetime import date
from enum import Enum
from pydantic import BaseModel, EmailStr, field_validator
from typing import Any, List, TypedDict
import re
import pandas as pd  # For pd.isna

# Assuming bulkupload.models is in the same Django app 'bulkupload'
from bulkupload.models import BusinessUnitChoices, DepartmentChoices

# Create Pydantic Enums from Django TextChoices


class BusinessUnitEnum(str, Enum):
    CHENNAI = BusinessUnitChoices.chennai
    COIMBATORE = BusinessUnitChoices.coimbatore
    MADURAI = BusinessUnitChoices.madurai
    UK_OFFICE = BusinessUnitChoices.uk_office
    US_OFFICE = BusinessUnitChoices.us_office


class DepartmentEnum(str, Enum):
    WEB_DEVELOPMENT = DepartmentChoices.web_development
    MOBILE_DEVELOPMENT = DepartmentChoices.mobile_development
    SOFTWARE = DepartmentChoices.software
    HR = DepartmentChoices.hr
    WEB_DESIGN = DepartmentChoices.web_design
    TESTING = DepartmentChoices.testing
    QA = DepartmentChoices.qa
    SALES = DepartmentChoices.sales
    MARKETING = DepartmentChoices.marketing
    ADMIN = DepartmentChoices.admin


class ValidationFailure(TypedDict):
    row_index: int  # Excel row number
    data: dict[str, Any]
    errors: List[Any]


class Users(BaseModel):
    user_id: str
    user_name: str
    email: EmailStr
    business_unit: BusinessUnitEnum
    department: DepartmentEnum
    date_of_joining: date
    mobile_number: str

    @field_validator('mobile_number', mode='before')
    @classmethod
    def validate_mobile_number(cls, v: Any) -> str:
        if pd.isna(v) or v is None:  # Handle NaN from pandas or explicit None
            raise ValueError('Mobile number is required.')

        s = str(v).strip()  # Ensure string, strip whitespace

        if not s:  # Empty string after strip
            raise ValueError('Mobile number is required.')

        if s.startswith('+'):
            s = s[1:]  # Strip leading +

        if not s:  # Empty string after stripping + (e.g. input was just "+")
            raise ValueError('Mobile number is required after stripping "+".')

        # Validate characters: only digits, or digits with specific punctuation if allowed.
        # Allows digits, spaces, hyphens, parentheses.
        if not re.fullmatch(r'[\d\s\-\(\)]+', s):
            raise ValueError(
                'Mobile number contains invalid characters. Allowed: digits, spaces, hyphens, parentheses (after optional leading "+").')

        # Validate overall length for DB storage (max_length=15 in model).
        if len(s) > 15:
            raise ValueError(
                f'Mobile number too long (max 15 chars after stripping "+"), got {len(s)} chars.')

        # Validate minimum number of actual digits (e.g. at least 7).
        num_digits = len(re.sub(r'\D', '', s))  # Count only digits
        if num_digits < 7:
            raise ValueError(
                f'Mobile number must contain at least 7 digits, found {num_digits}.')

        return s  # Return the processed string (e.g., without leading '+')

    class Config:
        use_enum_values = True  # Export enum choices as values (strings)
        anystr_strip_whitespace = True  # Strip whitespace for all string fields
        # Allow creating from ORM objects (model_validate replacement in Pydantic v1 style)
        from_attributes = True


class BulkUploadResult(TypedDict):
    successful_users: List[Users]
    failed_rows: List[ValidationFailure]
    newly_created_count: int
    total_users_after_upload: List[Users]
    attempted_new_rows_count: int
    all_users_in_file_existed: bool
    input_data_was_empty_after_cleaning: bool
    file_internal_duplicates_removed_count: int  # New field
