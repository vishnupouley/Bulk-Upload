# Generated by Django 5.1.4 on 2025-05-30 09:50

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UsersModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(max_length=10)),
                ('user_name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=50)),
                ('business_unit', models.CharField(choices=[('Chennai', 'Chennai'), ('Coimbatore', 'Coimbatore'), ('Madurai', 'Madurai'), ('UK Office', 'Uk Office'), ('US Office', 'Us Office')], max_length=10)),
                ('department', models.CharField(choices=[('Web Development', 'Web Development'), ('Mobile Development', 'Mobile Development'), ('Software', 'Software'), ('Human Resource', 'Hr'), ('Web Design', 'Web Design'), ('Testing', 'Testing'), ('Quality Assurance', 'Qa'), ('Sales', 'Sales'), ('Marketing', 'Marketing'), ('Admin', 'Admin')], max_length=18)),
                ('date_of_joining', models.DateField()),
                ('mobile_number', models.CharField(max_length=15)),
            ],
        ),
    ]
