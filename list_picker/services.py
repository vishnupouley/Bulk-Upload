from list_picker.models import Team, Employee

class ListPickerService:
    @staticmethod
    def get_all_teams():
        return Team.objects.all()

    @staticmethod
    def get_available_teams(new_selected_teams_ids):
        return Team.objects.exclude(id__in=new_selected_teams_ids)

    @staticmethod
    def get_selected_teams(new_selected_teams_ids):
        return Team.objects.filter(id__in=new_selected_teams_ids)

    @staticmethod
    def get_employees_by_teams(team_ids):
        return Employee.objects.filter(team_id__in=team_ids)

    @staticmethod
    def get_employees_not_in_list(employee_ids):
        return Employee.objects.exclude(id__in=employee_ids)
        
    @staticmethod
    def get_employees_by_teams_not_in_list(selected_teams_ids, new_selected_employees_ids):
        return Employee.objects.filter(team_id__in=selected_teams_ids).exclude(id__in=new_selected_employees_ids)

    @staticmethod
    def get_employees_by_teams_in_list(new_selected_employees_ids):
        return Employee.objects.filter(id__in=new_selected_employees_ids)