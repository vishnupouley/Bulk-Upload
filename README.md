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
- Django 5.1.4+
- pandas 1.4.2+
- pydantic 1.10.2+

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
  ...
  "bulkupload", # Application Name
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
