from django.contrib import messages
from django.shortcuts import render
import pandas as pd

from django.http import HttpRequest, HttpResponse
from pandas import DataFrame

from bulkupload.models import UsersModel
from bulkupload.services import save_bulk_data, validate_column_names


# Create your views here.


def import_data_pandas(request: HttpRequest) -> HttpResponse:
    """Handles the POST request to upload a file. Reads the file, checks if the columns match the model, and
    bulk creates the objects in the database.

    Args:
        request (HttpRequest): The request object containing the file to be uploaded.

    Returns:
        HttpResponse: The rendered page with the uploaded data, or the page with existing data if the request method is not POST.
    """
    if request.method != 'POST':
        return render(request, 'bulkupload/index.html', {'users': save_bulk_data(data_frame=None)})
    uploaded_file = request.FILES.get('myfile')
    if uploaded_file is None:
        messages.error(request, "No file uploaded.")
        return render(request, 'bulkupload/index.html', {'users': save_bulk_data(data_frame=None)})
    if uploaded_file.size == 0:
        messages.error(request, "No data in the file uploaded.")
        return render(request, 'bulkupload/index.html', {'users': save_bulk_data(data_frame=None)})
    try:
        data_frame: DataFrame = pd.read_excel(uploaded_file)
        if len(data_frame) == 0:
            messages.error(request, "No data in the file uploaded.")
            return render(request, 'bulkupload/index.html', {'users': save_bulk_data(data_frame=None)})
        if not validate_column_names(data_frame=data_frame):
            messages.error(request, "Invalid file format. Please check the file format.")
            return render(request, 'bulkupload/index.html', {'users': save_bulk_data(data_frame=None)})
    except ValueError:
        messages.error(request, "Error reading file. Please check the file format.")
        return render(request, 'bulkupload/index.html', {'users': save_bulk_data(data_frame=None)})

    messages.success(request, "Data Uploaded Successfully")
    return render(request, 'bulkupload/index.html', {'users': save_bulk_data(data_frame=data_frame)})

