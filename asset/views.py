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
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.shortcuts import render, redirect
from django.shortcuts import render, redirect
from .models import Asset, Company
from .forms import AddTablet, AddMobile, AddDesktop, AddLaptop, AddServer, AddPrinter
from django.shortcuts import render, redirect
from .models import Asset 
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.shortcuts import render
from .models import Asset, Employee, AssetAllocation
from django.contrib.auth.forms import PasswordResetForm
from django.shortcuts import render, redirect
from django.db.models import Q, Count
from django.db import models
from django.db.models import Q, Prefetch
from django.db.models import Count
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from django.shortcuts import HttpResponseRedirect
from .forms import CustomUserCreationForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Count
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
import csv
from django.template.loader import render_to_string
import tempfile
import openpyxl
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import AssetImportForm, UserImportForm
import pandas as pd
from django.views.generic import ListView
import pandas as pd
import chardet
from datetime import datetime
from django.contrib import messages
from django.shortcuts import render, redirect
from django.db import transaction
from .models import Asset, Employee, AssetAllocation, Company
from .forms import MassUploadForm
import pandas as pd
from django.http import HttpResponse
from io import BytesIO
from django.http import HttpResponse
from django.db.models import Count, Q
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
import pandas as pd
from io import BytesIO
from datetime import datetime


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'asset/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('login')

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'asset/signup.html', {'form': form})

def password_change_view(request):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to change your password.")
        return redirect('login')
    
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Update session to prevent logging out
            update_session_auth_hash(request, user)
            messages.success(request, "Your password has been changed successfully!")
            return redirect('home')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'asset/password_change.html', {'form': form})

@login_required
def home(request):
    total_assets = Asset.objects.count()
    allocated_assets = Asset.objects.filter(is_allocated=True).count()
    unallocated_assets = total_assets - allocated_assets
    total_employees = Employee.objects.count()
    
    # Count assets by type
    laptop_count = Asset.objects.filter(type='Laptop').count()
    desktop_count = Asset.objects.filter(type='Desktop').count()
    mobile_count = Asset.objects.filter(type='Mobile').count()
    tablet_count = Asset.objects.filter(type='Tablet').count()
    printer_count = Asset.objects.filter(type='Printer').count()
    other_count = Asset.objects.filter(type='Other').count()
    
    # Allocation status counts
    assigned_assets = allocated_assets
    available_assets = unallocated_assets
    
    context = {
        'total_assets': total_assets,
        'allocated_assets': allocated_assets,
        'unallocated_assets': unallocated_assets,
        'total_employees': total_employees,
        'laptop_count': laptop_count,
        'desktop_count': desktop_count,
        'mobile_count': mobile_count,
        'tablet_count': tablet_count,
        'printer_count': printer_count,
        'other_count': other_count,
        'assigned_assets': assigned_assets,
        'available_assets': available_assets,
        
    }

    return render(request, 'asset/home.html', context)

@login_required
def dashboard(request):
    # Basic counts
    total_assets = Asset.objects.count()
    allocated_assets = Asset.objects.filter(is_allocated=True).count()
    unallocated_assets = total_assets - allocated_assets
    damaged_assets = Damaged.objects.count()
    
    # Recent activity
    recent_allocations = AssetAllocation.objects.select_related(
        'asset', 'employee_allocated'
    ).order_by('-allocation_date')[:5]
    
    recent_returns = AssetReturn.objects.select_related(
        'asset', 'employee_returning'
    ).order_by('-return_date')[:5]
    
    context = {
        'total_assets': total_assets,
        'allocated_assets': allocated_assets,
        'unallocated_assets': unallocated_assets,
        'damaged_assets': damaged_assets,
        'recent_allocations': recent_allocations,
        'recent_returns': recent_returns,
    }
    return render(request, 'asset/dashboard.html', context)

@login_required
@login_required
def asset_allocation_form(request):
    if request.method == 'POST':
        form = AssetAllocationForm(request.POST)
        if form.is_valid():
            allocation = form.save(commit=False)
            allocation.allocation_date = timezone.now().date()
            allocation.save()
            
            # Redirect to form generation after successful allocation
            return redirect('generate_allocation_form', allocation_id=allocation.id)
    else:
        form = AssetAllocationForm()
        # Pre-fill asset if provided in GET parameters
        asset_id = request.GET.get('asset')
        if asset_id:
            try:
                asset = Asset.objects.get(id=asset_id)
                form.fields['asset'].initial = asset
                # Pre-select applications based on asset
                available_apps = [app for app, included in asset.applications.items() if included]
                form.fields['applications'].initial = available_apps
            except Asset.DoesNotExist:
                pass
    
    return render(request, 'asset/asset_allocation_form.html', {'form': form})

@login_required
def generate_allocation_form(request, allocation_id):
    allocation = get_object_or_404(AssetAllocation, id=allocation_id)
    asset = allocation.asset
    
    # Determine which template to use based on asset type
    if asset.type in ['Laptop', 'Desktop']:
        template_name = 'asset/computer_allocation_form.html'
    elif asset.type in ['Tablet', 'Mobile']:
        template_name = 'asset/mobile_allocation_form.html'
    else:
        # Default to computer form for other types
        template_name = 'asset/computer_allocation_form.html'
    
    context = {
        'allocation': allocation,
        'asset': asset,
    }
    
    return render(request, template_name, context)


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


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to the login page after successful signup
    else:
        form = UserCreationForm()
    return render(request, 'asset/signup.html', {'form': form})



def password_change_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')  # Redirect to the home page after successful password change
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'asset/password_change.html', {'form': form})



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
    assigned_assets = Asset.objects.filter(is_allocated=True).count()
    

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

@login_required
def return_asset(request, asset_id):
    asset = get_object_or_404(Asset, id=asset_id)
    
    if request.method == 'POST':
        form = ReturnForm(request.POST)
        if form.is_valid():
            # Create the return record
            return_record = form.save(commit=False)
            return_record.asset = asset
            return_record.return_date = timezone.now().date()
            return_record.save()
            
            messages.success(request, f"Asset {asset.serial_number} has been successfully returned.")
            return redirect('asset_detail', asset_id=asset.id)
    else:
        # Get current allocation to pre-populate employee
        current_allocation = AssetAllocation.objects.filter(
            asset=asset,
            return_date__isnull=True
        ).first()
        
        initial = {
            'asset': asset,
            'employee_returning': current_allocation.employee_allocated if current_allocation else None,
        }
        
        form = ReturnForm(initial=initial)
    
    return render(request, 'asset/return_asset.html', {
        'form': form,
        'asset': asset,
    })


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


def search(request):
    query = request.GET.get('q', '').strip()
    
    if not query:
        return render(request, 'asset/search_results.html', {'query': query})
    
    # Prefetch current allocations for assets
    current_allocations = AssetAllocation.objects.filter(
        return_date__isnull=True
    ).select_related('employee_allocated')
    
    # Search for assets with prefetched allocations
    assets = Asset.objects.filter(
        Q(serial_number__icontains=query) |
        Q(name__icontains=query) |
        Q(model__icontains=query) |
        Q(type__icontains=query)
    ).prefetch_related(
        Prefetch('assetallocation_set', queryset=current_allocations, to_attr='current_allocation')
    ).distinct()
    
    # Search for employees with annotated current asset count
    employees = Employee.objects.filter(
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(department__icontains=query) |
        Q(email__icontains=query)
    ).annotate(
        current_assets_count=Count(
            'assetallocation',
            filter=Q(assetallocation__return_date__isnull=True)
        )
    ).distinct()
    
    context = {
        'query': query,
        'assets': assets,
        'employees': employees,
    }
    
    return render(request, 'asset/search_results.html', context)


def asset_detail(request, asset_id):
    asset = get_object_or_404(Asset, pk=asset_id)
    
    # Get all allocations ordered by date
    allocations = AssetAllocation.objects.filter(asset=asset).order_by('-allocation_date')
    
    # Get all returns ordered by date
    returns = AssetReturn.objects.filter(asset=asset).order_by('-return_date')
    
    # Determine current status
    current_allocation = None
    if asset.is_allocated and not asset.is_returned:
        current_allocation = AssetAllocation.objects.filter(
            asset=asset,
            return_date__isnull=True
        ).first()
    
    context = {
        'asset': asset,
        'allocations': allocations,
        'returns': returns,
        'current_allocation': current_allocation,
    }
    
    return render(request, 'asset/asset_detail.html', context)


def employee_detail(request, employee_id):
    employee = get_object_or_404(Employee, pk=employee_id)
    allocations = AssetAllocation.objects.filter(employee_allocated=employee).order_by('-allocation_date')
    returns = AssetReturn.objects.filter(employee_returning=employee).order_by('-return_date')
    
    context = {
        'employee': employee,
        'allocations': allocations,
        'returns': returns,
        'current_assets': allocations.filter(return_date__isnull=True),
    }
    
    return render(request, 'asset/employee_detail.html', context)

class AllAssetsReport(LoginRequiredMixin, ListView):
    model = Asset
    template_name = 'asset/reports/all_assets.html'
    context_object_name = 'assets'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related('company').order_by('type', 'serial_number')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['report_title'] = "All Assets Report"
        context['total_count'] = self.get_queryset().count()
        return context

class AllocatedAssetsReport(LoginRequiredMixin, ListView):
    model = Asset
    template_name = 'asset/reports/allocated_assets.html'
    context_object_name = 'assets'
    paginate_by = 25
    
    def get_queryset(self):
        return Asset.objects.filter(
            is_allocated=True
        ).select_related('company').prefetch_related(
            'assetallocation_set'
        ).order_by('type', 'serial_number')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['report_title'] = "Allocated Assets Report"
        context['total_count'] = self.get_queryset().count()
        return context

class UnallocatedAssetsReport(LoginRequiredMixin, ListView):
    model = Asset
    template_name = 'asset/reports/unallocated_assets.html'
    context_object_name = 'assets'
    paginate_by = 25
    
    def get_queryset(self):
        return Asset.objects.filter(
            is_allocated=False
        ).select_related('company').order_by('type', 'serial_number')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['report_title'] = "Unallocated Assets Report"
        context['total_count'] = self.get_queryset().count()
        return context


def export_assets(request):
    format = request.GET.get('format', 'csv')
    assets = Asset.objects.all().select_related('company')
    
    if format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="assets_{}.csv"'.format(
            datetime.now().strftime("%Y%m%d")
        )
        
        writer = csv.writer(response)
        writer.writerow([
            'Serial Number', 'Asset Type', 'Model', 'Company', 
            'Status', 'Purchase Date', 'Price'
        ])
        
        for asset in assets:
            status = "Allocated" if asset.is_allocated else "Unallocated"
            writer.writerow([
                asset.serial_number,
                asset.get_type_display(),
                asset.model,
                asset.company.name,
                status,
                asset.purchase_date.strftime("%Y-%m-%d") if asset.purchase_date else "",
                str(asset.purchase_price) if asset.purchase_price else ""
            ])
            
        return response
        
    elif format == 'excel':
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="assets_{}.xlsx"'.format(
            datetime.now().strftime("%Y%m%d")
        )
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Assets"
        
        headers = [
            'Serial Number', 'Asset Type', 'Model', 'Company', 
            'Status', 'Purchase Date', 'Price'
        ]
        ws.append(headers)
        
        for asset in assets:
            status = "Allocated" if asset.is_allocated else "Unallocated"
            ws.append([
                asset.serial_number,
                asset.get_type_display(),
                asset.model,
                asset.company.name,
                status,
                asset.purchase_date,
                asset.purchase_price
            ])
            
        wb.save(response)
        return response
        
    elif format == 'pdf':
        html_string = render_to_string('asset/reports/export_pdf.html', {
            'assets': assets,
            'date': datetime.now().strftime("%B %d, %Y")
        })
        
        html = HTML(string=html_string)
        result = html.write_pdf()
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="assets_{}.pdf"'.format(
            datetime.now().strftime("%Y%m%d")
        )
        response.write(result)
        
        return response
        
    return redirect('dashboard')


class AssetTypeReportView(LoginRequiredMixin, ListView):
    model = Asset
    template_name = 'asset/reports/asset_type_report.html'
    context_object_name = 'assets'
    paginate_by = 25
    
    def get_queryset(self):
        asset_type = self.kwargs['type']
        return Asset.objects.filter(
            type=asset_type
        ).select_related('company').order_by('serial_number')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        asset_type = self.kwargs['type']
        context['report_title'] = f"{asset_type.capitalize()} Assets Report"
        context['asset_type'] = asset_type
        context['total_count'] = self.get_queryset().count()
        return context


def import_assets(request):
    if request.method == 'POST':
        form = AssetImportForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                df = pd.read_excel(request.FILES['file'])
                # Process each row
                for index, row in df.iterrows():
                    Asset.objects.create(
                        name=row.get('Name', ''),
                        serial_number=row.get('Serial Number', ''),
                        type=row.get('Type', 'laptop'),
                        model=row.get('Model', ''),
                        company=Company.objects.get_or_create(name=row.get('Company', 'Default Company'))[0],
                        # Add other fields as needed
                    )
                messages.success(request, f'Successfully imported {len(df)} assets')
                return redirect('asset_list')
            except Exception as e:
                messages.error(request, f'Error importing file: {str(e)}')
    else:
        form = AssetImportForm()
    return render(request, 'asset/import_form.html', {'form': form, 'title': 'Import Assets'})

def import_users(request):
    if request.method == 'POST':
        form = UserImportForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                df = pd.read_excel(request.FILES['file'])
                for index, row in df.iterrows():
                    Employee.objects.create(
                        first_name=row.get('First Name', ''),
                        last_name=row.get('Last Name', ''),
                        email=row.get('Email', ''),
                        department=row.get('Department', ''),
                        company=Company.objects.get_or_create(name=row.get('Company', 'Default Company'))[0],
                        # Add other fields as needed
                    )
                messages.success(request, f'Successfully imported {len(df)} users')
                return redirect('employee_list')
            except Exception as e:
                messages.error(request, f'Error importing file: {str(e)}')
    else:
        form = UserImportForm()
    return render(request, 'asset/import_form.html', {'form': form, 'title': 'Import Users'})



@login_required
def mass_upload(request):
    if request.method == 'POST':
        form = MassUploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload_type = form.cleaned_data['upload_type']
            file = form.cleaned_data['file']
            
            try:
                # Process the file based on type
                if upload_type == 'asset':
                    result = process_asset_upload(file)
                elif upload_type == 'employee':
                    result = process_employee_upload(file)
                elif upload_type == 'allocation':
                    result = process_allocation_upload(file)
                
                if result['error_count'] > 0:
                    # Show warning if there were errors but some succeeded
                    messages.warning(request, result['message'])
                else:
                    messages.success(request, result['message'])
                    
                # Store errors in session to display on page
                if result['errors']:
                    request.session['upload_errors'] = result['errors'][:10]  # Store first 10 errors
                
                return redirect('mass_upload')
                
            except Exception as e:
                error_msg = f"Error processing file: {str(e)}"
                print(error_msg)
                messages.error(request, error_msg)
                return render(request, 'asset/mass_upload.html', {'form': form})
    else:
        form = MassUploadForm()
        
        # Check if there are errors from previous upload to display
        upload_errors = request.session.pop('upload_errors', None)
    
    return render(request, 'asset/mass_upload.html', {
        'form': form,
        'upload_errors': upload_errors
    })


def read_uploaded_file(file):
    """Read uploaded file (CSV or Excel) into a DataFrame"""
    file_name = file.name.lower()
    
    try:
        if file_name.endswith('.csv'):
            # Try different encodings and separators
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'windows-1252']
            separators = [',', '\t', ';']
            
            for encoding in encodings:
                for sep in separators:
                    try:
                        file.seek(0)  # Reset file pointer
                        df = pd.read_csv(file, encoding=encoding, sep=sep)
                        print(f"Successfully read CSV with encoding: {encoding}, separator: '{sep}'")
                        print(f"Columns: {df.columns.tolist()}")
                        print(f"Shape: {df.shape}")
                        return df
                    except (UnicodeDecodeError, pd.errors.ParserError):
                        continue
            
            # If all else fails, try with error handling
            file.seek(0)
            try:
                df = pd.read_csv(file, encoding='utf-8', sep=None, engine='python', on_bad_lines='skip')
                print("Read CSV with error handling")
                return df
            except:
                file.seek(0)
                df = pd.read_csv(file, error_bad_lines=False)
                print("Read CSV with error_bad_lines=False")
                return df
            
        elif file_name.endswith(('.xlsx', '.xls')):
            file.seek(0)
            df = pd.read_excel(file)
            print(f"Successfully read Excel file")
            print(f"Columns: {df.columns.tolist()}")
            print(f"Shape: {df.shape}")
            return df
            
        else:
            raise ValueError("Unsupported file format. Please upload a CSV or Excel file.")
            
    except Exception as e:
        print(f"Error reading file: {str(e)}")
        raise ValueError(f"Error reading file: {str(e)}")

def process_asset_upload(file):
    """Process asset upload from CSV/Excel"""
    df = read_uploaded_file(file)
    
    # Normalize column names (remove spaces, lowercase, etc.)
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    
    required_columns = ['serial_number', 'name']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
    
    success_count = 0
    error_count = 0
    errors = []
    
    with transaction.atomic():
        for index, row in df.iterrows():
            try:
                asset_data = {}
                
                # Map CSV columns to model fields
                field_mapping = Asset.get_import_fields()
                for csv_col, model_field in field_mapping.items():
                    if csv_col in df.columns and pd.notna(row.get(csv_col)):
                        asset_data[model_field] = row[csv_col]
                
                # Handle company field (could be name or ID)
                if 'company' in asset_data:
                    company_value = asset_data['company']
                    if isinstance(company_value, str):
                        # Try to find company by name
                        company, created = Company.objects.get_or_create(
                            name=company_value,
                            defaults={'location': 'Unknown'}
                        )
                        asset_data['company'] = company
                    elif isinstance(company_value, (int, float)):
                        # Try to find company by ID
                        try:
                            asset_data['company'] = Company.objects.get(id=int(company_value))
                        except Company.DoesNotExist:
                            errors.append(f"Row {index+2}: Company with ID {company_value} not found")
                            error_count += 1
                            continue
                
                # Check if asset already exists
                serial_number = asset_data.get('serial_number')
                if Asset.objects.filter(serial_number=serial_number).exists():
                    asset = Asset.objects.get(serial_number=serial_number)
                    for key, value in asset_data.items():
                        setattr(asset, key, value)
                    asset.save()
                else:
                    asset = Asset.objects.create(**asset_data)
                
                success_count += 1
                
            except Exception as e:
                errors.append(f"Row {index+2}: {str(e)}")
                error_count += 1
    
    message = f"Processed {success_count} assets successfully."
    if error_count > 0:
        message += f" {error_count} errors occurred."
        if errors:
            message += " First error: " + errors[0]
    
    return {'message': message, 'success_count': success_count, 'error_count': error_count, 'errors': errors}

def process_employee_upload(file):
    """Process employee upload from CSV/Excel"""
    df = read_uploaded_file(file)
    
    # Normalize column names
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    
    required_columns = ['first_name', 'last_name', 'email', 'company']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
    
    success_count = 0
    error_count = 0
    errors = []
    
    with transaction.atomic():
        for index, row in df.iterrows():
            try:
                employee_data = {}
                
                # Map CSV columns to model fields
                field_mapping = Employee.get_import_fields()
                for csv_col, model_field in field_mapping.items():
                    if csv_col in df.columns and pd.notna(row.get(csv_col)):
                        employee_data[model_field] = row[csv_col]
                
                # Handle company field
                if 'company' in employee_data:
                    company_value = employee_data['company']
                    if isinstance(company_value, str):
                        company, created = Company.objects.get_or_create(
                            name=company_value,
                            defaults={'location': 'Unknown'}
                        )
                        employee_data['company'] = company
                    elif isinstance(company_value, (int, float)):
                        try:
                            employee_data['company'] = Company.objects.get(id=int(company_value))
                        except Company.DoesNotExist:
                            errors.append(f"Row {index+2}: Company with ID {company_value} not found")
                            error_count += 1
                            continue
                
                # Check if employee already exists
                email = employee_data.get('email')
                if Employee.objects.filter(email=email).exists():
                    employee = Employee.objects.get(email=email)
                    for key, value in employee_data.items():
                        setattr(employee, key, value)
                    employee.save()
                else:
                    employee = Employee.objects.create(**employee_data)
                
                success_count += 1
                
            except Exception as e:
                errors.append(f"Row {index+2}: {str(e)}")
                error_count += 1
    
    message = f"Processed {success_count} employees successfully."
    if error_count > 0:
        message += f" {error_count} errors occurred."
        if errors:
            message += " First error: " + errors[0]
    
    return {'message': message, 'success_count': success_count, 'error_count': error_count, 'errors': errors}

def process_allocation_upload(file):
    """Process allocation upload using employee names"""
    df = read_uploaded_file(file)
    
    # Normalize column names
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    
    # Map possible column names to standard names
    column_mapping = {
        'asset_serial_number': ['asset_serial_number', 'serial_number', 'serial', 'asset_serial'],
        'employee_first_name': ['employee_first_name', 'first_name', 'firstname', 'fname'],
        'employee_last_name': ['employee_last_name', 'last_name', 'lastname', 'lname'],
        'allocation_date': ['allocation_date', 'date', 'alloc_date'],
        'return_date': ['return_date', 'returndate'],
        'asset_status': ['asset_status', 'status']
    }
    
    # Rename columns
    for std_name, possible_names in column_mapping.items():
        for possible_name in possible_names:
            if possible_name in df.columns:
                df = df.rename(columns={possible_name: std_name})
                break
    
    # Check required columns
    required_columns = ['asset_serial_number', 'employee_first_name', 'employee_last_name', 'allocation_date']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
    
    success_count = 0
    error_count = 0
    errors = []
    
    with transaction.atomic():
        for index, row in df.iterrows():
            row_num = index + 2  # +2 for header row and 0-based index
            
            try:
                # Get and validate serial number
                serial_number = str(row.get('asset_serial_number', '')).strip()
                if not serial_number or serial_number.lower() in ['nan', 'null', 'none']:
                    errors.append(f"Row {row_num}: Serial number is required")
                    error_count += 1
                    continue
                
                # Find asset
                try:
                    asset = Asset.objects.get(serial_number=serial_number)
                except Asset.DoesNotExist:
                    errors.append(f"Row {row_num}: Asset with serial number '{serial_number}' not found")
                    error_count += 1
                    continue
                
                # Get employee names
                first_name = str(row.get('employee_first_name', '')).strip()
                last_name = str(row.get('employee_last_name', '')).strip()
                
                if not first_name or not last_name:
                    errors.append(f"Row {row_num}: Both first and last name are required")
                    error_count += 1
                    continue
                
                # Find employee
                employee = Employee.find_by_name(first_name, last_name)
                if not employee:
                    errors.append(f"Row {row_num}: Employee '{first_name} {last_name}' not found")
                    error_count += 1
                    continue
                
                # Parse dates
                allocation_date = parse_date(row.get('allocation_date'), row_num, 'allocation_date', errors)
                return_date = parse_date(row.get('return_date'), row_num, 'return_date', errors) if pd.notna(row.get('return_date')) else None
                
                if allocation_date is None:
                    error_count += 1
                    continue
                
                # Get asset status
                asset_status = str(row.get('asset_status', 'new')).strip().lower()
                if asset_status not in ['new', 'old', 'damaged']:
                    asset_status = 'new'
                
                # Check if asset is already allocated
                if AssetAllocation.objects.filter(asset=asset, return_date__isnull=True).exists():
                    errors.append(f"Row {row_num}: Asset {serial_number} is already allocated")
                    error_count += 1
                    continue
                
                # Create allocation
                allocation = AssetAllocation.objects.create(
                    asset=asset,
                    employee_allocated=employee,
                    allocation_date=allocation_date,
                    return_date=return_date,
                    asset_status=asset_status
                )
                
                # Update asset status
                asset.is_allocated = True
                asset.is_returned = False
                asset.save()
                
                success_count += 1
                
            except Exception as e:
                errors.append(f"Row {row_num}: Unexpected error - {str(e)}")
                error_count += 1
    
    message = f"Successfully processed {success_count} allocations"
    if error_count > 0:
        message += f" with {error_count} errors"
    
    return {
        'message': message,
        'success_count': success_count,
        'error_count': error_count,
        'errors': errors
    }

def parse_date(date_value, row_num, field_name, errors):
    """Parse date from various formats"""
    if pd.isna(date_value) or date_value == '':
        errors.append(f"Row {row_num}: {field_name} is required")
        return None
    
    try:
        # Try different date formats
        if isinstance(date_value, datetime):
            return date_value.date()
        
        if isinstance(date_value, str):
            # Try common date formats
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']:
                try:
                    return datetime.strptime(date_value.strip(), fmt).date()
                except ValueError:
                    continue
        
        # Try pandas timestamp
        if hasattr(date_value, 'date'):
            return date_value.date()
            
        errors.append(f"Row {row_num}: Invalid date format for {field_name}: '{date_value}'")
        return None
        
    except Exception as e:
        errors.append(f"Row {row_num}: Error parsing {field_name}: {str(e)}")
        return None


@login_required
def download_template(request, template_type):
    """Download CSV template for mass upload"""
    if template_type == 'asset':
        # Create asset template
        columns = [
            'serial_number', 'name', 'model', 'type', 'company', 
            'purchase_date', 'purchase_price', 'imei_number', 'processor', 
            'ram', 'ssd_capacity', 'hdd_capacity', 'os', 'os_licence', 
            'office', 'office_licence', 'specs', 'accessories', 'ip',
            'applications_description'
        ]
        filename = 'asset_upload_template.csv'
        
    elif template_type == 'employee':
        # Create employee template
        columns = [
            'first_name', 'last_name', 'email', 'department', 
            'phone_number', 'company'
        ]
        filename = 'employee_upload_template.csv'
        
    elif template_type == 'allocation':
        # Create allocation template
        columns = [
            'asset_serial_number', 'employee_first_name', 'employee_last_name', 'allocation_date',
            'return_date', 'asset_status'
        ]
        filename = 'allocation_upload_template.csv'
        
    else:
        return HttpResponse("Invalid template type", status=400)
    
    # Create empty DataFrame with required columns
    df = pd.DataFrame(columns=columns)
    
    # Create response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # Write DataFrame to response
    df.to_csv(response, index=False)
    
    return response



class AssetReportView(LoginRequiredMixin, View):
    def get(self, request, report_type):
        # Get the requested format (default to Excel)
        format = request.GET.get('format', 'excel')
        
        if report_type == 'total_assets':
            return self.total_assets_report(request, format)
        elif report_type == 'allocated_assets':
            return self.allocated_assets_report(request, format)
        elif report_type == 'unallocated_assets':
            return self.unallocated_assets_report(request, format)
        elif report_type == 'status':
            return self.assets_by_status_report(request, format)
        elif report_type == 'department':
            return self.assets_by_department_report(request, format)
        else:
            return HttpResponse("Invalid report type", status=400)
    
    def total_assets_report(self, request, format):
        """Generate report of all assets"""
        assets = Asset.objects.select_related('company').order_by('name', 'serial_number')
        
        data = []
        for asset in assets:
            current_allocation = asset.current_allocation()
            allocated_to = f"{current_allocation.employee_allocated.first_name} {current_allocation.employee_allocated.last_name}" if current_allocation else "Not Allocated"
            department = current_allocation.employee_allocated.department if current_allocation else "N/A"
            
            data.append({
                'Name': asset.name,
                'Serial Number': asset.serial_number,
                'Type': asset.get_type_display(),
                'Model': asset.model,
                'Company': asset.company.name,
                'Status': 'Allocated' if asset.is_allocated else 'Unallocated',
                'Allocated To': allocated_to,
                'Department': department,
                'Purchase Date': asset.purchase_date.strftime("%Y-%m-%d") if asset.purchase_date else "",
                'Purchase Price': str(asset.purchase_price) if asset.purchase_price else ""
            })
        
        return self.export_to_excel(data, "Total Assets Report")
    
    def allocated_assets_report(self, request, format):
        """Generate report of allocated assets"""
        assets = Asset.objects.filter(is_allocated=True).select_related('company').order_by('name', 'serial_number')
        
        data = []
        for asset in assets:
            current_allocation = asset.current_allocation()
            if current_allocation:
                data.append({
                    'Name': asset.name,
                    'Serial Number': asset.serial_number,
                    'Type': asset.get_type_display(),
                    'Model': asset.model,
                    'Company': asset.company.name,
                    'Allocated To': f"{current_allocation.employee_allocated.first_name} {current_allocation.employee_allocated.last_name}",
                    'Department': current_allocation.employee_allocated.department,
                    'Allocation Date': current_allocation.allocation_date.strftime("%Y-%m-%d"),
                    'Asset Status': current_allocation.get_asset_status_display(),
                    'Purchase Date': asset.purchase_date.strftime("%Y-%m-%d") if asset.purchase_date else "",
                })
        
        return self.export_to_excel(data, "Allocated Assets Report")
    
    def unallocated_assets_report(self, request, format):
        """Generate report of unallocated assets"""
        assets = Asset.objects.filter(is_allocated=False).select_related('company').order_by('name', 'serial_number')
        
        data = []
        for asset in assets:
            data.append({
                'Name': asset.name,
                'Serial Number': asset.serial_number,
                'Type': asset.get_type_display(),
                'Model': asset.model,
                'Company': asset.company.name,
                'Purchase Date': asset.purchase_date.strftime("%Y-%m-%d") if asset.purchase_date else "",
                'Purchase Price': str(asset.purchase_price) if asset.purchase_price else "",
                'Status': 'Available' if not asset.is_returned else 'Returned'
            })
        
        return self.export_to_excel(data, "Unallocated Assets Report")
    
    def assets_by_status_report(self, request, format):
        """Generate report grouping assets by status"""
        # Get status filter from request if provided
        status_filter = request.GET.get('status', None)
        
        if status_filter:
            allocations = AssetAllocation.objects.filter(asset_status=status_filter)
        else:
            allocations = AssetAllocation.objects.all()
        
        # Group by status
        allocations = allocations.select_related('asset', 'employee_allocated').order_by('asset_status')
        
        data = []
        for allocation in allocations:
            data.append({
                'Asset Name': allocation.asset.name,
                'Serial Number': allocation.asset.serial_number,
                'Type': allocation.asset.get_type_display(),
                'Status': allocation.get_asset_status_display(),
                'Allocated To': f"{allocation.employee_allocated.first_name} {allocation.employee_allocated.last_name}",
                'Department': allocation.employee_allocated.department,
                'Allocation Date': allocation.allocation_date.strftime("%Y-%m-%d"),
                'Return Date': allocation.return_date.strftime("%Y-%m-%d") if allocation.return_date else "Not Returned"
            })
        
        report_title = "Assets by Status Report"
        if status_filter:
            report_title += f" - {dict(AssetAllocation.ASSET_STATUS_CHOICES).get(status_filter, status_filter)}"
        
        return self.export_to_excel(data, report_title)
    
    def assets_by_department_report(self, request, format):
        """Generate report grouping assets by department"""
        # Get department filter from request if provided
        department_filter = request.GET.get('department', None)
        
        # Get allocations with related data
        allocations = AssetAllocation.objects.filter(
            return_date__isnull=True  # Only current allocations
        ).select_related(
            'employee_allocated', 'asset'
        )
        
        if department_filter:
            allocations = allocations.filter(employee_allocated__department=department_filter)
        
        # Group by department
        allocations = allocations.order_by('employee_allocated__department')
        
        data = []
        for allocation in allocations:
            data.append({
                'Department': allocation.employee_allocated.department,
                'Asset Name': allocation.asset.name,
                'Serial Number': allocation.asset.serial_number,
                'Type': allocation.asset.get_type_display(),
                'Allocated To': f"{allocation.employee_allocated.first_name} {allocation.employee_allocated.last_name}",
                'Email': allocation.employee_allocated.email,
                'Allocation Date': allocation.allocation_date.strftime("%Y-%m-%d"),
                'Asset Status': allocation.get_asset_status_display()
            })
        
        report_title = "Assets by Department Report"
        if department_filter:
            report_title += f" - {department_filter}"
        
        return self.export_to_excel(data, report_title)
    
    def export_to_excel(self, data, title):
        """Export data to Excel format"""
        if not data:
            # Return empty Excel file with message
            df = pd.DataFrame({"Message": ["No data available for this report"]})
        else:
            df = pd.DataFrame(data)
        
        # Create Excel file in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=title[:30], index=False)  # Sheet name max 31 chars
            
            # Auto-adjust columns width
            worksheet = writer.sheets[title[:30]]
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 2)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        # Prepare HTTP response
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        filename = f"{title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Write Excel file to response
        output.seek(0)
        response.write(output.getvalue())
        
        return response
    
# @login_required
#def reports_dashboard(request):
   # """Display all available reports"""
    # Get counts for dashboard
   # total_assets = Asset.objects.count()
   # allocated_assets = Asset.objects.filter(is_allocated=True).count()
    #unallocated_assets = total_assets - allocated_assets
    
    # Get unique departments
    #departments = Employee.objects.values_list('department', flat=True).distinct()
    
   # context = {
   #     'total_assets': total_assets,
     #   'allocated_assets': allocated_assets,
     #   'unallocated_assets': unallocated_assets,
      #  'departments': departments,
      #  'status_choices': AssetAllocation.ASSET_STATUS_CHOICES,
   # }
   # return render(request, 'asset/reports_dashboard.html', context)



from django.http import JsonResponse
from django.db.models import Count, Q, Prefetch
from django.views.generic import TemplateView

# Add these class-based views
class ReportsDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'asset/reports_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get counts for dashboard
        total_assets = Asset.objects.count()
        allocated_assets = Asset.objects.filter(is_allocated=True).count()
        unallocated_assets = total_assets - allocated_assets
        
        # Get all companies
        companies = Company.objects.annotate(
            asset_count=Count('asset'),
            allocated_count=Count('asset', filter=Q(asset__is_allocated=True)),
            unallocated_count=Count('asset', filter=Q(asset__is_allocated=False))
        )
        
        # Get unique departments - filter out empty/null values
        departments = Employee.objects.exclude(
            Q(department__isnull=True) | Q(department__exact='')
        ).values_list('department', flat=True).distinct()
        
        # Get asset type counts
        asset_types = Asset.ASSET_TYPE_CHOICES
        asset_type_counts = []
        
        for type_code, type_name in asset_types:
            count = Asset.objects.filter(type=type_code).count()
            allocated_count = Asset.objects.filter(type=type_code, is_allocated=True).count()
            unallocated_count = Asset.objects.filter(type=type_code, is_allocated=False).count()
            
            asset_type_counts.append({
                'type_code': type_code,
                'type_name': type_name,
                'total_count': count,
                'allocated_count': allocated_count,
                'unallocated_count': unallocated_count
            })
        
        context.update({
            'total_assets': total_assets,
            'allocated_assets': allocated_assets,
            'unallocated_assets': unallocated_assets,
            'companies': companies,
            'departments': departments,
            'asset_types': asset_types,
            'asset_type_counts': asset_type_counts,
            'status_choices': AssetAllocation.ASSET_STATUS_CHOICES,
        })
        
        return context

# Add these report views
class CompanyAssetsReport(LoginRequiredMixin, ListView):
    model = Asset
    template_name = 'asset/company_assets.html'
    context_object_name = 'assets'
    paginate_by = 25
    
    def get_queryset(self):
        company_id = self.kwargs.get('company_id')
        if company_id:
            return Asset.objects.filter(
                company_id=company_id
            ).select_related('company').prefetch_related(
                Prefetch(
                    'assetallocation_set',
                    queryset=AssetAllocation.objects.filter(return_date__isnull=True),
                    to_attr='current_allocation'
                )
            ).order_by('type', 'serial_number')
        return Asset.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company_id = self.kwargs.get('company_id')
        company = Company.objects.get(id=company_id)
        
        context['report_title'] = f"Assets Report - {company.name}"
        context['company'] = company
        context['total_count'] = self.get_queryset().count()
        
        # Add counts by status
        context['allocated_count'] = self.get_queryset().filter(is_allocated=True).count()
        context['unallocated_count'] = self.get_queryset().filter(is_allocated=False).count()
        
        return context

class DepartmentAssetsReport(LoginRequiredMixin, ListView):
    model = AssetAllocation
    template_name = 'asset/department_assets.html'
    context_object_name = 'allocations'
    paginate_by = 25
    
    def get_queryset(self):
        department = self.kwargs.get('department')
        if department and department.strip():  # Check if department is not empty
            return AssetAllocation.objects.filter(
                employee_allocated__department=department,
                return_date__isnull=True
            ).select_related(
                'asset', 'employee_allocated', 'asset__company'
            ).order_by('asset__type', 'asset__serial_number')
        return AssetAllocation.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        department = self.kwargs.get('department')
        
        if not department or not department.strip():
            # Handle empty department case
            context['report_title'] = "Invalid Department"
            context['department'] = "Invalid"
            context['total_count'] = 0
            return context
        
        context['report_title'] = f"Department Assets Report - {department}"
        context['department'] = department
        context['total_count'] = self.get_queryset().count()
        
        return context

class AssetTypeReport(LoginRequiredMixin, ListView):
    model = Asset
    template_name = 'asset/asset_type_report.html'
    context_object_name = 'assets'
    paginate_by = 25
    
    def get_queryset(self):
        asset_type = self.kwargs.get('asset_type')
        if asset_type:
            return Asset.objects.filter(
                type=asset_type
            ).select_related('company').prefetch_related(
                Prefetch(
                    'assetallocation_set',
                    queryset=AssetAllocation.objects.filter(return_date__isnull=True),
                    to_attr='current_allocation'
                )
            ).order_by('serial_number')
        return Asset.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        asset_type = self.kwargs.get('asset_type')
        asset_type_name = dict(Asset.ASSET_TYPE_CHOICES).get(asset_type, asset_type)
        
        context['report_title'] = f"{asset_type_name} Assets Report"
        context['asset_type'] = asset_type
        context['asset_type_name'] = asset_type_name
        context['total_count'] = self.get_queryset().count()
        
        # Add counts by status
        context['allocated_count'] = self.get_queryset().filter(is_allocated=True).count()
        context['unallocated_count'] = self.get_queryset().filter(is_allocated=False).count()
        
        return context

# Add these export functions
@login_required
def export_company_assets(request, company_id):
    """Export company assets to Excel"""
    company = get_object_or_404(Company, id=company_id)
    assets = Asset.objects.filter(company=company).select_related('company')
    
    return export_assets_to_excel(assets, f"Assets_Report_{company.name}")

@login_required
def export_department_assets(request, department):
    """Export department assets to Excel"""
    if not department or not department.strip():
        # Return empty response for invalid department
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Invalid_Department_Report.xlsx"'
        return response
    
    allocations = AssetAllocation.objects.filter(
        employee_allocated__department=department,
        return_date__isnull=True
    ).select_related('asset', 'employee_allocated', 'asset__company')
    
    return export_allocations_to_excel(allocations, f"Department_Assets_Report_{department}")

@login_required
def export_asset_type_assets(request, asset_type):
    """Export asset type assets to Excel"""
    assets = Asset.objects.filter(type=asset_type).select_related('company')
    
    return export_assets_to_excel(assets, f"{asset_type.capitalize()}_Assets_Report")

@login_required
def export_allocated_assets(request):
    """Export allocated assets to Excel"""
    assets = Asset.objects.filter(is_allocated=True).select_related('company')
    
    return export_assets_to_excel(assets, "Allocated_Assets_Report")

@login_required
def export_unallocated_assets(request):
    """Export unallocated assets to Excel"""
    assets = Asset.objects.filter(is_allocated=False).select_related('company')
    
    return export_assets_to_excel(assets, "Unallocated_Assets_Report")

# Helper functions for export
def export_assets_to_excel(assets, title):
    """Export assets data to Excel format"""
    data = []
    for asset in assets:
        current_allocation = asset.current_allocation()
        allocated_to = f"{current_allocation.employee_allocated.first_name} {current_allocation.employee_allocated.last_name}" if current_allocation else "Not Allocated"
        department = current_allocation.employee_allocated.department if current_allocation else "N/A"
        
        data.append({
            'Name': asset.name,
            'Serial Number': asset.serial_number,
            'Type': asset.get_type_display(),
            'Model': asset.model,
            'Company': asset.company.name,
            'Status': 'Allocated' if asset.is_allocated else 'Unallocated',
            'Allocated To': allocated_to,
            'Department': department,
            'Purchase Date': asset.purchase_date.strftime("%Y-%m-%d") if asset.purchase_date else "",
            'Purchase Price': str(asset.purchase_price) if asset.purchase_price else ""
        })
    
    return generate_excel_response(data, title)

def export_allocations_to_excel(allocations, title):
    """Export allocation data to Excel format"""
    data = []
    for allocation in allocations:
        data.append({
            'Asset Name': allocation.asset.name,
            'Serial Number': allocation.asset.serial_number,
            'Type': allocation.asset.get_type_display(),
            'Model': allocation.asset.model,
            'Company': allocation.asset.company.name,
            'Allocated To': f"{allocation.employee_allocated.first_name} {allocation.employee_allocated.last_name}",
            'Department': allocation.employee_allocated.department,
            'Email': allocation.employee_allocated.email,
            'Allocation Date': allocation.allocation_date.strftime("%Y-%m-%d"),
            'Asset Status': allocation.get_asset_status_display()
        })
    
    return generate_excel_response(data, title)

def generate_excel_response(data, title):
    """Generate Excel file from data and return as HTTP response"""
    if not data:
        # Return empty Excel file with message
        df = pd.DataFrame({"Message": ["No data available for this report"]})
    else:
        df = pd.DataFrame(data)
    
    # Create Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=title[:30], index=False)
        
        # Auto-adjust columns width
        worksheet = writer.sheets[title[:30]]
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    # Prepare HTTP response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f"{title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # Write Excel file to response
    output.seek(0)
    response.write(output.getvalue())
    
    return response