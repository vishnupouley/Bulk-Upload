from django.contrib import messages
from django.shortcuts import render
import pandas as pd

from django.http import HttpRequest, HttpResponse
from pandas import DataFrame

from bulkupload.models import UsersModel
from bulkupload.services import save_bulk_data


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
    except ValueError:
        messages.error(request, "Error reading file. Please check the file format.")
        return render(request, 'bulkupload/index.html', {'users': save_bulk_data(data_frame=None)})

    messages.success(request, "Data Uploaded Successfully")
    return render(request, 'bulkupload/index.html', {'users': save_bulk_data(data_frame=data_frame)})


"""

from bulkupload.resources import UsersResource
from tablib import Dataset


def import_data(request):

    Handle the import of data from an Excel file.

    If the request is a POST, read the Excel file, create a list of UsersModel
    objects from the data, and then use bulk_create to save them to the database.

    if request.method == 'POST':
        user_resource = UsersResource()
        dataset = Dataset()

        # Read the Excel file
        uploaded_file = request.FILES['myfile']
        imported_data = dataset.load(uploaded_file.read(), format='xlsx')

        # Create a list of UsersModel objects from the data
        users_to_create = []
        for row in imported_data:
            user = UsersModel(
                user_id=row[0],
                user_name=row[1],
                email=row[2],
                business_unit=row[3],
                department=row[4],
                date_of_joining=row[5],
                mobile_number=row[6],
            )
            users_to_create.append(user)

        # Use bulk_create to save the users to the database
        UsersModel.objects.bulk_create(users_to_create)

        # Send a success message
        messages.success(request, "Data Uploaded Successfully")

        # Return the updated list of users
        return render(request, 'bulkupload/index.html', {'users': UsersModel.objects.all()})

    # If the request is a GET, return the list of users
    return render(request, 'bulkupload/index.html', {'users': UsersModel.objects.all()})

"""
