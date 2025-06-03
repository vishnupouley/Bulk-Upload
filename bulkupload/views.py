# bulkupload/views.py

from django.contrib import messages
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import pandas as pd

from bulkupload.models import UsersModel
from bulkupload.services import save_bulk_data, BulkUploadResult
from bulkupload.schema import Users as PydanticUsersSchema

# render_paginated_users function remains the same as in the previous correct response.
# Ensure it's correctly defined in your views.py.
def render_paginated_users(request: HttpRequest, additional_context: dict | None = None) -> HttpResponse:
    """Helper function to fetch, paginate, and render users."""
    
    page_number_str = request.GET.get('page_number', '1')
    try:
        page_number = int(page_number_str)
        if page_number < 1: page_number = 1
    except ValueError:
        page_number = 1

    per_page_str = request.GET.get('per_page', '10')
    try:
        per_page = int(per_page_str)
        if per_page not in [5, 10, 15, 20]:
            per_page = 10
    except ValueError:
        per_page = 10

    user_queryset = UsersModel.objects.all().order_by('user_id')
    paginator = Paginator(user_queryset, per_page)

    try:
        users_page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        users_page_obj = paginator.page(1)
    except EmptyPage:
        users_page_obj = paginator.page(paginator.num_pages)
    
    pydantic_users_list = [PydanticUsersSchema.model_validate(user) for user in users_page_obj.object_list]

    context = {
        'users': {
            'users': pydantic_users_list,
            'page': users_page_obj,
            'per_page': str(per_page),
            'total_users': paginator.count,
            'has_previous': users_page_obj.has_previous(),
            'previous_page_number': users_page_obj.previous_page_number() if users_page_obj.has_previous() else users_page_obj.number,
            'has_next': users_page_obj.has_next(),
            'next_page_number': users_page_obj.next_page_number() if users_page_obj.has_next() else users_page_obj.number,
        }
    }
    if additional_context:
        context.update(additional_context)
        
    return render(request, 'bulkupload/index.html', context)

def import_data_pandas(request: HttpRequest) -> HttpResponse:
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
        upload_result: BulkUploadResult = save_bulk_data(data_frame.copy())
        
        newly_created_count = upload_result['newly_created_count']
        failed_rows = upload_result['failed_rows']
        attempted_new_rows_count = upload_result['attempted_new_rows_count']
        all_users_in_file_existed = upload_result['all_users_in_file_existed']
        input_data_was_empty_after_cleaning = upload_result['input_data_was_empty_after_cleaning']
        file_internal_duplicates_removed_count = upload_result['file_internal_duplicates_removed_count']

        if file_internal_duplicates_removed_count > 0:
            messages.info(request, f"{file_internal_duplicates_removed_count} duplicate row(s) within the uploaded file were ignored (based on User ID, first occurrence kept).")

        if newly_created_count > 0:
            messages.success(request, f"{newly_created_count} user(s) uploaded successfully.")
        
        for failure in failed_rows:
            error_messages_list = []
            for err_detail in failure['errors']:
                loc = " -> ".join(map(str, err_detail.get('loc', ['unknown field'])))
                msg = err_detail.get('msg', 'Unknown error')
                error_messages_list.append(f"Column '{loc}': {msg}")
            detailed_errors = "; ".join(error_messages_list)
            display_data = {k: str(v)[:30] + '...' if len(str(v)) > 30 else str(v) for k,v in failure['data'].items()}
            messages.warning(request, f"Excel Row {failure['row_index']} failed validation: {detailed_errors}. Data: {display_data}")

        if newly_created_count == 0: # Further specific messages if no users were created
            if input_data_was_empty_after_cleaning and not data_frame.empty :
                 messages.info(request, "No processable user data found in the file after initial cleaning (e.g., all User IDs were blank or invalid).")
            elif all_users_in_file_existed:
                messages.info(request, "No new users were added. All unique users from the file already exist in the database.")
            elif attempted_new_rows_count > 0 and not failed_rows:
                messages.info(request, "Data was processed and deemed valid, but no new users were saved. This could be due to concurrent creations or other database constraints if 'ignore_conflicts' was used.")
            elif attempted_new_rows_count > 0 and len(failed_rows) == attempted_new_rows_count:
                messages.info(request, "All new user entries in the file failed validation. No users were uploaded.")
            elif not failed_rows and not data_frame.empty and file_internal_duplicates_removed_count == 0 and attempted_new_rows_count == 0 and not all_users_in_file_existed : # Catch-all for other no-creation scenarios
                 messages.info(request, "Data processed. No new users were added. File may have contained no new entries after processing duplicates or existing records.")


    except ValueError as e:
        messages.error(request, f"Error processing data: {e}")
    except Exception as e:
        messages.error(request, f"An unexpected error occurred: {e}")
    
    return render_paginated_users(request)