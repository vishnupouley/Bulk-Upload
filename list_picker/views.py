from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template.loader import render_to_string
from .services import get_all_teams, get_employees_by_teams, get_employees_by_teams_not_in_list, get_employees_by_teams_in_list

def index(request):
    teams = get_all_teams()
    employees = get_employees_by_teams([])  # Initially no teams selected
    return render(request, 'list_picker/index.html', {'teams': teams, 'employees': employees})

def add_teams(request):
    # Get selected team IDs from the request
    current_selected_teams_ids = request.POST.get('selected_teams', '').split(',')
    to_add = request.POST.getlist('available_teams')
    new_selected_teams_ids = list(set(current_selected_teams_ids + to_add) - {''})
    
    # Fetch teams and employees
    all_teams = get_all_teams()
    available_teams = all_teams.exclude(id__in=new_selected_teams_ids)
    selected_teams = all_teams.filter(id__in=new_selected_teams_ids)
    employees = get_employees_by_teams(new_selected_teams_ids)
    
    # Render partial templates
    available_teams_html = render_to_string('list_picker/partials/available_teams.html', {'teams': available_teams})
    selected_teams_html = render_to_string('list_picker/partials/selected_teams.html', {'teams': selected_teams})
    available_employees_html = render_to_string('list_picker/partials/available_employees.html', {'employees': employees})
    selected_teams_ids_html = f'<input type="hidden" id="selected-teams-ids" name="selected_teams" value="{','.join(new_selected_teams_ids)}" hx-swap-oob="true">'
    
    # Build response
    response = HttpResponse()
    response.write(selected_teams_ids_html)
    response.write(f'<div id="available-teams" hx-swap-oob="true">{available_teams_html}</div>')
    response.write(f'<div id="selected-teams" hx-swap-oob="true">{selected_teams_html}</div>')
    response.write(available_employees_html)  # Updates #available-employees-select
    return response

def remove_teams(request):
    # Get current selected teams from hidden input
    current_selected_teams = request.POST.get('selected_teams', '').split(',')
    # Get teams to remove from the select multiple
    to_remove = request.POST.getlist('teams_to_remove')
    
    # Update selected teams by removing only the specified ones
    new_selected_teams_ids = [tid for tid in current_selected_teams if tid not in to_remove and tid != '']
    
    # Get available and selected teams
    all_teams = get_all_teams()
    available_teams = all_teams.exclude(id__in=new_selected_teams_ids)
    selected_teams = all_teams.filter(id__in=new_selected_teams_ids)
    
    # Update available employees based on new selected teams
    employees = get_employees_by_teams(new_selected_teams_ids)
    
    # Render partial templates
    available_teams_html = render_to_string('list_picker/partials/available_teams.html', {'teams': available_teams})
    selected_teams_html = render_to_string('list_picker/partials/selected_teams.html', {'teams': selected_teams})
    available_employees_html = render_to_string('list_picker/partials/available_employees.html', {'employees': employees})
    selected_teams_ids_html = f'<input type="hidden" id="selected-teams-ids" name="selected_teams" value="{','.join(new_selected_teams_ids)}" hx-swap-oob="true">'
    
    # Build response
    response = HttpResponse()
    response.write(selected_teams_ids_html)
    response.write(f'<div id="available-teams" hx-swap-oob="true">{available_teams_html}</div>')
    response.write(f'<div id="selected-teams" hx-swap-oob="true">{selected_teams_html}</div>')
    response.write(f'<div id="available-employees" hx-swap-oob="true">{available_employees_html}</div>')
    return response

def add_employees(request):
    selected_teams_ids = request.POST.get('selected_teams', '').split(',')
    current_selected_employees_ids = request.POST.get('selected_employees', '').split(',')
    to_add = request.POST.getlist('available_employees')
    new_selected_employees_ids = list(set(current_selected_employees_ids + to_add) - {''})
    
    # Fetch available employees: from selected teams, not in selected employees
    available_employees = get_employees_by_teams_not_in_list(selected_teams_ids, new_selected_employees_ids)
    selected_employees = get_employees_by_teams_in_list(selected_teams_ids, new_selected_employees_ids)
    
    available_employees_html = render_to_string('list_picker/partials/available_employees.html', {'employees': available_employees})
    selected_employees_html = render_to_string('list_picker/partials/selected_employees.html', {'employees': selected_employees})
    selected_employees_ids_html = f'<input type="hidden" id="selected-employees-ids" name="selected_employees" value="{','.join(new_selected_employees_ids)}" hx-swap-oob="true">'
    
    response = HttpResponse()
    response.write(selected_employees_ids_html)
    response.write(f'<div id="available-employees" hx-swap-oob="true">{available_employees_html}</div>')
    response.write(f'<div id="selected-employees" hx-swap-oob="true">{selected_employees_html}</div>')
    return response

def remove_employees(request):
    # Get current selected teams and employees from hidden inputs
    selected_teams_ids = request.POST.get('selected_teams', '').split(',')
    current_selected_employees = request.POST.get('selected_employees', '').split(',')
    # Get employees to remove from the select multiple
    to_remove = request.POST.getlist('employees_to_remove')
    
    # Update selected employees by removing only the specified ones
    new_selected_employees_ids = [eid for eid in current_selected_employees if eid not in to_remove and eid != '']
    
    # Get available and selected employees
    available_employees = get_employees_by_teams_not_in_list(selected_teams_ids, new_selected_employees_ids)
    selected_employees = get_employees_by_teams_in_list(selected_teams_ids, new_selected_employees_ids)
    
    # Render partial templates
    available_employees_html = render_to_string('list_picker/partials/available_employees.html', {'employees': available_employees})
    selected_employees_html = render_to_string('list_picker/partials/selected_employees.html', {'employees': selected_employees})
    selected_employees_ids_html = f'<input type="hidden" id="selected-employees-ids" name="selected_employees" value="{','.join(new_selected_employees_ids)}" hx-swap-oob="true">'
    
    # Build response
    response = HttpResponse()
    response.write(selected_employees_ids_html)
    response.write(f'<div id="available-employees" hx-swap-oob="true">{available_employees_html}</div>')
    response.write(f'<div id="selected-employees" hx-swap-oob="true">{selected_employees_html}</div>')
    return response

def save(request):
    selected_teams = request.POST.get('selected_teams', '').split(',')
    selected_employees = request.POST.get('selected_employees', '').split(',')
    print(f"Selected Teams: {selected_teams}")
    print(f"Selected Employees: {selected_employees}")
    return redirect('list_picker:index')