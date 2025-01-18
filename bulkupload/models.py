from django.db import models


# Create your models here.

class BusinessUnitChoices(models.TextChoices):
    chennai = 'Chennai'
    coimbatore = 'Coimbatore'
    madurai = 'Madurai'
    uk_office = 'UK Office'
    us_office = 'US Office'


class DepartmentChoices(models.TextChoices):
    web_development = 'Web Development'
    mobile_development = 'Mobile Development'
    software = 'Software'
    hr = 'Human Resource'
    web_design = 'Web Design'
    ui_ux = 'UI/UX'
    testing = 'Testing'
    qa = 'Quality Assurance'
    sales = 'Sales'
    marketing = 'Marketing'
    admin = 'Admin'


class UsersModel(models.Model):
    user_id = models.CharField(max_length=10)
    user_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    business_unit = models.CharField(
        max_length=10,
        choices=BusinessUnitChoices,
    )
    department = models.CharField(
        max_length=18,
        choices=DepartmentChoices,
    )
    date_of_joining = models.DateField()
    mobile_number = models.CharField(max_length=15)

    def __str__(self):
        return self.user_name
