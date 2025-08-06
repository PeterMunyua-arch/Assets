from django.shortcuts import render, get_object_or_404, redirect
from .models import  Employee, Asset, Transaction, AssetAllocation, AssetReturn, Company, Damaged
from .forms import AssignmentForm, ReturnForm, AddForm, EmployeeForm, AssetAllocationForm, AssetReturnForm, DisposalForm
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from datetime import timedelta, datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to the home page after successful login
        else:
            # Handle invalid login credentials (optional)
            return render(request, 'asset/login.html', {'error_message': 'Invalid username or password'})
    else:
        return render(request, 'asset/login.html')


def logout_view(request):
    # Logout the user using Django's logout function
    logout(request)
    return redirect('login')  # Replace 'login' with the name of your login page URL


@login_required
def home(request):
    return render(request, 'asset/home.html')

@login_required
def asset_allocation_form(request):
    if request.method == 'POST':
        form = AssetAllocationForm(request.POST)
        if form.is_valid():
            allocation = form.save()  # Save the allocation
            return redirect('asset_detail', asset_id=allocation.pk)
    else:
        form = AssetAllocationForm()
    return render(request, 'asset/asset_allocation_form.html', {'form': form})


def asset_detail(request, asset_id):
    asset_allocation = get_object_or_404(AssetAllocation, pk=asset_id)
    return render(request, 'asset/asset_detail.html', {'asset_allocation': asset_allocation})


@login_required
def asset_return_form(request):
    if request.method == 'POST':
        form = AssetReturnForm(request.POST)
        if form.is_valid():
            allocation = form.save()  # Save the allocation
            return redirect('assetreturn_detail', asset_id=allocation.pk)   # Redirect to asset return detail page
    else:
        form = AssetReturnForm()
    return render(request, 'asset/asset_allocation_form.html', {'form': form})


def assetreturn_detail(request, asset_id):
    asset_return = get_object_or_404(AssetReturn, pk=asset_id)
    return render(request, 'asset/assetreturn_detail.html', {'asset_return': asset_return})

def success_page(request, success_message=None):
    return render(request, 'asset/success.html', {'success_message': success_message})



def assign_asset(request):
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            serial_number = form.cleaned_data['serial_number']
            if Transaction.objects.filter(serial_number=serial_number, return_date__isnull=True).exists():
                return render(request, 'asset/assign_asset.html', {'form': form, 'error_message': 'Asset is already assigned.'})
            else:
                form.save()
                return redirect('asset_list')  # Redirect to asset list page or wherever you want
    else:
        form = AssignmentForm()
    return render(request, 'asset/assign_asset.html', {'form': form})



# @login_required
#def add_asset(request):
    #if request.method == 'POST':
        #form = AddForm(request.POST)
       # if form.is_valid():
         #   form.save()  # Save the form data to the database
            #return redirect('home')  # Redirect to success page
   # else:
      #  form = AddForm()
   # return render(request, 'asset/add_asset.html', {'form': form})

from django.shortcuts import render, redirect
from .models import Asset, Company
from .forms import AddTablet, AddMobile, AddDesktop, AddLaptop, AddServer, AddPrinter

from django.shortcuts import render, redirect
from .models import Asset

@login_required
def add_asset(request):
    if request.method == 'POST':
        form = AddForm(request.POST)
        if form.is_valid():
            asset = form.save(commit=False)
            asset.company = Company.objects.first()  # Example: Assign a company
            asset.save()
            return redirect('add_asset')  # Redirect to asset list page or another page
    else:
        form = AddForm()

    return render(request, 'asset/add_asset.html', {'form': form})




@login_required
def add_employee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()  # Save the form data to the database
            return redirect('add_employee')  # Redirect to success page
    else:
        form = EmployeeForm()
    return render(request, 'asset/add_employee.html', {'form': form})

@login_required
def asset_report(request):
    # Retrieve all assets from the database
    assets = Asset.objects.all()
    
    # Pass the assets to the template for rendering
    return render(request, 'asset/report.html', {'assets': assets})

@login_required
def allocated_assets_report(request):
    allocated_assets = AssetAllocation.objects.filter(return_date__isnull=True)  # Filter assets that are currently allocated
    return render(request, 'asset/allocated_assets_report.html', {'allocated_assets': allocated_assets})

@login_required
def unallocated_assets_report(request):
    unallocated_assets = Asset.objects.filter(is_allocated=False)
    return render(request, 'asset/unallocated_assets_report.html', {'unallocated_assets': unallocated_assets})

def assets_per_company_report(request):
    # Assuming you have a Company model with a ForeignKey relationship with Asset
    companies = Company.objects.all()
    assets_per_company = {}
    for company in companies:
        assets_per_company[company.name] = Asset.objects.filter(company=company)
    return render(request, 'asset/assets_per_company_report.html', {'assets_per_company': assets_per_company})





from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to the login page after successful signup
    else:
        form = UserCreationForm()
    return render(request, 'asset/signup.html', {'form': form})


from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect


def password_change_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')  # Redirect to the home page after successful password change
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'asset/password_change.html', {'form': form})



from django.contrib.auth.forms import PasswordResetForm
from django.shortcuts import render, redirect

def password_reset_view(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('password_reset_done')  # Redirect to the password reset done page
    else:
        form = PasswordResetForm()
    return render(request, 'asset/password_reset.html', {'form': form})

def password_reset_done_view(request):
    return render(request, 'asset/password_reset_done.html')


def dashboard(request):
    total_assets = Asset.objects.count()
    assigned_assets = Asset.objects.filter(is_assigned=True).count()
    

    context = {
        'total_assets': total_assets,
        'assigned_assets': assigned_assets,
    }
    return render(request, 'asset/dashboard.html', context)


def asset_disposal(request):
    if request.method == 'POST':
        form = DisposalForm(request.POST)
        if form.is_valid():
            disposal = form.save()
            # Perform any additional actions after disposal
            return redirect('home')  # Redirect to dashboard or another page
    else:
        form = DisposalForm()

    context = {'form': form}
    return render(request, 'asset/disposal.html', context)



def asset_list(request):
    assets = Asset.objects.all()  # Retrieve all assets from the database
    return render(request, 'assets/asset_list.html', {'assets': assets})

def return_asset(request, asset_id):
    asset = get_object_or_404(Asset, id=asset_id)
    if request.method == 'POST':
        form = ReturnForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.asset_name = asset.name
            transaction.serial_number = asset.serial_number
            transaction.save()
            return redirect('asset_list')  # Redirect to asset list page or wherever you want
    else:
        form = ReturnForm(initial={'asset': asset, 'asset_name': asset.name, 'serial_number': asset.serial_number})
    return render(request, 'asset/return_asset.html', {'form': form})



from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from django.shortcuts import HttpResponseRedirect
from .forms import CustomUserCreationForm
def signup(request):
    if request.user.is_authenticated:
        return redirect('signin')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            # login(request, user)
            return redirect('/signin')
        else:
            return render(request, 'asset/signup.html', {'form': form})
    else:
        form = CustomUserCreationForm()
        return render(request, 'aseet/signup.html', {'form': form})


def signin(request):
    if request.user.is_authenticated:
        return render(request, 'asset/home.html')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home') #profile
        else:
            msg = 'Error Login'
            form = AuthenticationForm(request.POST)
            return render(request, 'asset/login.html', {'form': form, 'msg': msg})
    else:
        form = AuthenticationForm()
        return render(request, 'asset/login.html', {'form': form})

def profile(request): 
    return render(request, 'asset/profile.html')


    # views.py
# views.py

# views.py
# views.py

# views.py
# views.py

from django.shortcuts import render
from .models import Asset, Employee, AssetAllocation

def search(request):
    query = request.GET.get('q')

    assets = Asset.objects.filter(
        serial_number__icontains=query
    ) | Asset.objects.filter(name__icontains=query)
    
    employees = Employee.objects.filter(
        first_name__icontains=query
    ) | Employee.objects.filter(last_name__icontains=query)
    
    allocations = AssetAllocation.objects.filter(
        employee_allocated__first_name__icontains=query
    ) | AssetAllocation.objects.filter(
        employee_allocated__last_name__icontains=query
    ) | AssetAllocation.objects.filter(
        asset__serial_number__icontains=query
    )

    context = {
        'assets': assets,
        'employees': employees,
        'allocations': allocations,
        'query': query
    }

    return render(request, 'asset/search_results.html', context)


