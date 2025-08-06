# urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('home/', views.home, name='home'),
    path('assign_asset/', views.assign_asset, name='assign_asset'),
    path('return_asset/', views.return_asset, name='return_asset'),
    path('success/', views.success_page, name='success_page'),  # Define the URL pattern for the success page
    path('add_employee/', views.add_employee, name='add_employee'),
    path('add_asset/', views.add_asset, name='add_asset'),
    path('report/', views.asset_report, name='asset_report'),
    path('assets/', views.asset_list, name='asset_list'),
    path('asset-allocation/', views.asset_allocation_form, name='asset_allocation_form'),
    path('asset-return/', views.asset_return_form, name='asset_return_form'),
    path('unallocated-assets/', views.unallocated_assets_report, name='unallocated_assets_report'),
    path('assets-per-company/', views.assets_per_company_report, name='assets_per_company_report'),
    path('asset/allocated-assets-report/', views.allocated_assets_report, name='allocated_assets_report'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('password_change/', views.password_change_view, name='password_change'),
    path('password_reset/', views.password_reset_view, name='password_reset'),
    path('password_reset_done/', views.password_reset_done_view, name='password_reset_done'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('asset_disposal', views.asset_disposal, name='asset_disposal'),
    path('asset_detail/<int:asset_id>/', views.asset_detail, name='asset_detail'),
    path('assetreturn_detail/<int:asset_id>/', views.assetreturn_detail, name='assetreturn_detail'),
    path('signin/',views.signin, name='signin'),
    path('signup/',views.signup, name='signup'),
    path('profile/',views.profile, name='profile'),
    path('search/', views.search, name='search'),
]
