from django.contrib import messages
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
import pandas as pd

from bulkupload.schema import BulkUploadResult
from bulkupload.services import BulkUploadService


def render_paginated_users(request: HttpRequest, additional_context: dict | None = None) -> HttpResponse:
    """Render paginated users using data from services."""
    print(request.GET)
    page_number_str = request.GET.get('page_number', '1')
    try:
        page_number = int(page_number_str)
        if page_number < 1:
            page_number = 1
    except ValueError:
        page_number = 1

    per_page_str = request.GET.get('per_page', '10')
    try:
        per_page = int(per_page_str)
        if per_page not in [5, 10, 15, 20]:
            per_page = 10
    except ValueError:
        per_page = 10

    users_data = BulkUploadService.get_paginated_users(page_number, per_page)
    context = {'users': users_data}
    if additional_context:
        context.update(additional_context)

    return render(request, 'bulkupload/index.html', context)

def import_data_pandas(request: HttpRequest) -> HttpResponse:
    """Handle file upload and process user data."""
    if request.method != 'POST':
        return render_paginated_users(request)

    uploaded_file = request.FILES.get('myfile')
    if not uploaded_file:
        messages.error(request, "No file uploaded.")
        return render_paginated_users(request)
    if uploaded_file.name.split('.')[-1].lower() not in ['xlsx']:
        messages.error(request, "Invalid file type. Please upload an .xlsx file.")
        return render_paginated_users(request)
    if uploaded_file.size == 0:
        messages.error(request, "The uploaded file is empty.")
        return render_paginated_users(request)

    try:
        data_frame = pd.read_excel(uploaded_file)
        if data_frame.empty:
            messages.error(request, "The Excel file contains no data rows.")
            return render_paginated_users(request)
    except Exception as e:
        messages.error(request, f"Error reading Excel file: {e}")
        return render_paginated_users(request)

    try:
        upload_result: BulkUploadResult = BulkUploadService.save_bulk_data(data_frame.copy())
        newly_created_count = upload_result['newly_created_count']
        failed_rows = upload_result['failed_rows']
        attempted_new_rows_count = upload_result['attempted_new_rows_count']
        all_users_in_file_existed = upload_result['all_users_in_file_existed']
        input_data_was_empty_after_cleaning = upload_result['input_data_was_empty_after_cleaning']
        file_internal_duplicates_removed_count = upload_result['file_internal_duplicates_removed_count']

        if file_internal_duplicates_removed_count > 0:
            messages.info(request, f"{file_internal_duplicates_removed_count} duplicate row(s) within the uploaded file were ignored.")
        if newly_created_count > 0:
            messages.success(request, f"{newly_created_count} user(s) uploaded successfully.")
        for failure in failed_rows:
            error_messages_list = [f"Column '{ ' -> '.join(map(str, err_detail.get('loc', ['unknown field']))) }': {err_detail.get('msg', 'Unknown error')}" 
                                   for err_detail in failure['errors']]
            detailed_errors = "; ".join(error_messages_list)
            display_data = {k: str(v)[:30] + '...' if len(str(v)) > 30 else str(v) for k, v in failure['data'].items()}
            messages.warning(request, f"Excel Row {failure['row_index']} failed validation: {detailed_errors}. Data: {display_data}")
        if newly_created_count == 0:
            if input_data_was_empty_after_cleaning and not data_frame.empty:
                messages.info(request, "No processable user data found after cleaning.")
            elif all_users_in_file_existed:
                messages.info(request, "All unique users from the file already exist.")
            elif attempted_new_rows_count > 0 and not failed_rows:
                messages.info(request, "Data valid but no new users saved, possibly due to conflicts.")
            elif attempted_new_rows_count > 0 and len(failed_rows) == attempted_new_rows_count:
                messages.info(request, "All new user entries failed validation.")
            elif not failed_rows and not data_frame.empty and file_internal_duplicates_removed_count == 0 and attempted_new_rows_count == 0:
                messages.info(request, "No new users added after processing.")

    except ValueError as e:
        messages.error(request, f"Error processing data: {e}")
    except Exception as e:
        messages.error(request, f"An unexpected error occurred: {e}")

    return render_paginated_users(request)