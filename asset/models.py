from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver

class Company(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Employee(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    department = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True)
    

    def __str__(self):
        return self.first_name +" "+ self.last_name

class Asset(models.Model):
    ASSET_TYPE_CHOICES = ASSET_TYPE_CHOICES = [
        ('laptop', 'Laptop'),
        ('mobile', 'Mobile'),
        ('desktop', 'Desktop'),
        ('server', 'Server'),
        ('printer', 'Printer'),
        ('tablet', 'Tablet'),
        ('UPS', 'UPS'),
        ('Switch', 'Switch')
    ]
    OFFICE_TYPE_CHOICES = [
        ('2007', '2007'),
        ('2010', '2010'),
        ('2013', '2013'),
        ('2016', '2016'),
        ('365', '365'),
    ]
    OS_TYPE_CHOICES = [
        ('win7', 'Win7'),
        ('win8.1', 'Win8.1'),
        ('win10', 'Win10'),
        ('win11', 'Win11')
    ]
    name = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    type = models.CharField(max_length=50, choices=ASSET_TYPE_CHOICES,blank=True, null=True)
    office = models.CharField(max_length=50, choices=OFFICE_TYPE_CHOICES, null=True, blank=True)
    office_licence = models.CharField(max_length=50, null=True, blank=True)
    os = models.CharField(max_length=100, choices=OS_TYPE_CHOICES, null=True, blank=True)
    os_licence = models.CharField(max_length=100, null=True, blank=True)
    specs = models.TextField(blank=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    purchase_date = models.DateField(blank=True)
    serial_number = models.CharField(max_length=100)
    accessories = models.CharField(max_length=100, null=True, blank=True)
    ip = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    is_allocated = models.BooleanField(default=False)
    is_returned = models.BooleanField(default=False)

    def __str__(self):
        return self.serial_number

class AssetAllocation(models.Model):
    ASSET_STATUS_CHOICES = [
        ('new', 'New'),
        ('old', 'Old'),
        ('damaged', 'Damaged'),
    ]

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    # serial_number = models.CharField(max_length=100)
    employee_allocated = models.ForeignKey(Employee, on_delete=models.CASCADE)
    allocation_date = models.DateField()
    return_date = models.DateField(null=True, blank=True) 
    asset_status = models.CharField(max_length=50, choices=ASSET_STATUS_CHOICES)

    def __str__(self):
        return f"{self.asset.name} - {self.asset.serial_number} - Allocated to {self.employee_allocated} on {self.allocation_date}"

    def save(self, *args, **kwargs):
        if not self.pk:  # If this is a new allocation, mark the asset as allocated
            if self.asset.is_allocated:
                raise ValidationError("This asset is already allocated and cannot be allocated again until it's returned.")
            self.asset.is_allocated = True
            self.asset.save()
        super().save(*args, **kwargs)


    def return_asset(self):
        if self.asset.is_returned:
            raise ValidationError("This asset is already returned and cannot be returned again.")
        self.return_date = datetime.date.today()
        self.asset.is_allocated = False  # Mark the asset as not allocated
        self.asset.is_returned = True  # Mark the asset as returned
        self.asset.save()
        self.save()

class AssetReturn(models.Model):
    ASSET_STATUS_CHOICES = [
        ('new', 'New'),
        ('old', 'Old'),
        ('damaged', 'Damaged'),
    ]

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    # serial_number = models.CharField(max_length=100)
    employee_returning = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True)  # Allow NULL values
    return_date = models.DateField()
    asset_status = models.CharField(max_length=50, choices=ASSET_STATUS_CHOICES)

    def __str__(self):
        return f"{self.asset.name} - {self.asset.serial_number} - Returned by {self.employee_returning} on {self.return_date}"

    def save(self, *args, **kwargs):
        if not self.pk:  # If this is a new return, mark the asset as returned
            if self.asset.is_returned:
                raise ValidationError("This asset is already returned and cannot be returned again.")
            self.asset.is_returned = True
            self.asset.save()
        super().save(*args, **kwargs)

    def allocate_asset(self):
        if self.asset.is_allocated:
            raise ValidationError("This asset is already allocated and cannot be allocated again.")
        self.return_date = datetime.date.today()
        self.asset.is_allocated = True  # Mark the asset as allocated
        self.asset.is_returned = False  # Mark the asset as not returned
        self.asset.save()
        self.save()

class Transaction(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    asset_name = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    assigned_to = models.ForeignKey(Employee, on_delete=models.CASCADE)
    assignment_date = models.DateField(default=timezone.now)
    return_date = models.DateField(null=True, blank=True)
    STATUS_CHOICES = (
        ('New', 'New'),
        ('Old', 'Old'),
        ('Damaged', 'Damaged'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def _str_(self):
        return f"{self.asset.name} - {self.assigned_to}"

class InventoryItem(models.Model):
    serial_number = models.CharField(max_length=100, unique=True)
    asset = models.OneToOneField(Asset, on_delete=models.CASCADE, related_name='inventory_item')
    quantity = models.IntegerField(default=1)
    location = models.CharField(max_length=100)
    assigned_to = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_date = models.DateField(null=True, blank=True)
    returned_date = models.DateField(null=True, blank=True)
    is_assigned = models.BooleanField(default=False)

    def assign_to_employee(self, employee):
        if not self.is_assigned:
            self.assigned_to = employee
            self.is_assigned = True
            self.save()
            return True
        return False

    def return_asset(self):
        if self.is_assigned:
            self.assigned_to = None
            self.is_assigned = False
            self.save()
            return True
        return False


class Damaged(models.Model):
    serial_number = models.IntegerField(unique=True)
    asset = models.ForeignKey('Asset', on_delete=models.CASCADE)
    damage_reason = models.CharField(max_length=255)
    damage_date = models.DateField()

    def __str__(self):
        return f"{self.asset} - Disposed on {self.disposal_date}"

