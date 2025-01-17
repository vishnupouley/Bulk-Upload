# Bulk Upload Django Application

## Overview

This is a Django application designed to handle bulk uploads of user data. It provides a simple and efficient way to import user information from Excel files and store it in a database.

## Features

- Handles bulk uploads of user data from Excel files
- Validates user data before saving it to the database
- Provides a simple and user-friendly interface for uploading files
- Supports multiple file formats (currently only Excel)

## Requirements

- [Python 3.10+](https://docs.python.org/3/whatsnew/3.10.html)
- [Django](https://docs.djangoproject.com/en/5.1/)
- [django-browser-reload](https://github.com/adamchainz/django-browser-reload)
- [django-cotton](https://django-cotton.com)
- [django-htmx](https://django-htmx.readthedocs.io)
- [django-tailwind](https://django-tailwind.readthedocs.io/en/latest/installation.html)
- [pandas](https://pandas.pydata.org/docs)
- [pydantic](https://docs.pydantic.dev/latest)
- [pytest-django](https://pytest-django.readthedocs.io)
  
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
- Complete the process that the documentation says (which I've linked in the [Requirements](https://github.com/vishnupouley/Bulk-Upload/blob/main/README.md#requirements))
- Add this into your INSTALLED_APPS and MIDDLEWARE list which is in the settings.py:
  ```python
  INSTALLED_APPS = [
  
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_cotton', # Read the ducumentations
    'django_htmx', # Read the documentations
    'tailwind', # Read the documentation
    'theme', # Read the documentation
    'django_browser_reload', # Read the documentation

    'bulkupload', # Name of this application 
  ]

  TAILWIND_APP_NAME = 'theme'

  INTERNAL_IPS = [
    "127.0.0.1",
  ]

  MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'django_browser_reload.middleware.BrowserReloadMiddleware', # Read the documentation
    "django_htmx.middleware.HtmxMiddleware", # Read the documentation
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

## Troubleshooting

- If you encounter any issues during installation or usage, please check the logs for errors
- Make sure you have the required packages installed
- If you're still having trouble, feel free to open an issue on the GitHub repository
