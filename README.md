# Bulk Upload Django Application

## Overview

This is a Django application designed to handle bulk uploads of user data. It provides a simple and efficient way to import user information from Excel files and store it in a database.

## Features

- Handles bulk uploads of user data from Excel files
- Validates user data before saving it to the database
- Provides a simple and user-friendly interface for uploading files
- Supports multiple file formats (currently only Excel)

## Requirements

- Python 3.8+
- Django 
- django-browser-reload
- django-cotton
- django-htmx
- django-tailwind
  - pandas
- pydantic
- pytest-django
  
## Installation

- Clone the repository:
  ```bash
  git clone https://github.com/vishnupouley/Bulk-Upload.git
  ```
- Navigate to the project directory:
  ```bash
  cd your-repo-name
  ```
- Install the required packages:
  ```bash
  pip install -r requirements.txt
  ```
- Add this into your INSTALLED_APPS list which is in the settings.py:
  ```python
  INSTALLED_APPS = [
  
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_cotton',
    'django_htmx',
    'tailwind',
    'theme',
    'django_browser_reload',

    'fileupload',
    'bulkupload',
  ]
  ```
- Run the migrations:
  ```bash
  python manage.py makemigrations
  python manage.py migrate
  ```
- Start the development server:
  ```bash
  python manage.py runserver
  ```

## Usage

1. Open the application in your web browser: http://localhost:8000
2. Click on the "Upload File" button to select an Excel file
3. Click on the "Upload" button to upload the file
4. The application will validate the data and save it to the database
5. You can view the uploaded data by clicking on the "View Data" button

## Troubleshooting

- If you encounter any issues during installation or usage, please check the logs for errors
- Make sure you have the required packages installed
- If you're still having trouble, feel free to open an issue on the GitHub repository
