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
    
    @classmethod
    def get_import_fields(cls):
        """Return mapping of CSV column names to model fields"""
        return {
            'first_name': 'first_name',
            'last_name': 'last_name',
            'email': 'email',
            'department': 'department',
            'phone_number': 'phone_number',
            'company': 'company'
        }

class Asset(models.Model):
    ASSET_TYPE_CHOICES = [
        ('laptop', 'Laptop'),
        ('mobile', 'Mobile'),
        ('desktop', 'Desktop'),
        ('server', 'Server'),
        ('printer', 'Printer'),
        ('tablet', 'Tablet'),
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
    PROCESSOR_CHOICES = [
        ('i3', 'Intel Core i3'),
        ('i5', 'Intel Core i5'),
        ('i7', 'Intel Core i7'),
        ('i9', 'Intel Core i9'),
        ('ryzen3', 'AMD Ryzen 3'),
        ('ryzen5', 'AMD Ryzen 5'),
        ('ryzen7', 'AMD Ryzen 7'),
        ('ryzen9', 'AMD Ryzen 9'),
        ('other', 'Other'),
    ]
    RAM_CHOICES = [
        ('2', '2GB'),
        ('4', '4GB'),
        ('8', '8GB'),
        ('16', '16GB'),
        ('32', '32GB'),
        ('64', '64GB'),
    ]
    STORAGE_TYPE_CHOICES = [
        ('hdd', 'HDD'),
        ('ssd', 'SSD'),
        ('nvme', 'NVMe SSD'),
        ('hybrid', 'Hybrid (SSD+HDD)'),
    ]
    
    APPLICATIONS_CHOICES = [
        ('adobe_reader', 'Adobe Reader'),
        ('antivirus_sophos', 'Antivirus (Sophos)'),
        ('browser_chrome', 'Browser (Chrome)'),
        ('anydesk', 'Anydesk'),
        ('teamviewer', 'TeamViewer'),
        ('tally', 'Tally'),
        ('sap_b1', 'SAP B1'),
        ('data_loggers', 'Data Loggers'),
        ('printers', 'Printers'),
        ('hr_software', 'HR Software'),
        ('shared_folders', 'Shared Folders'),
        ('winrar', 'WinRAR'),
        ('zoom', 'Zoom'),
        ('other', 'Other Applications'),
    ]
    name = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    type = models.CharField(max_length=50, choices=ASSET_TYPE_CHOICES, blank=True, null=True)
    office = models.CharField(max_length=50, choices=OFFICE_TYPE_CHOICES, null=True, blank=True)
    office_licence = models.CharField(max_length=50, null=True, blank=True)
    os = models.CharField(max_length=100, choices=OS_TYPE_CHOICES, null=True, blank=True)
    os_licence = models.CharField(max_length=100, null=True, blank=True)
    specs = models.TextField(blank=True)
    
    # New fields
    imei_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="IMEI Number")
    processor = models.CharField(max_length=50, choices=PROCESSOR_CHOICES, blank=True, null=True)
    ram = models.CharField(max_length=10, choices=RAM_CHOICES, blank=True, null=True, verbose_name="RAM")
    ssd_capacity = models.CharField(max_length=20, blank=True, null=True, verbose_name="SSD Capacity (GB/TB)")
    hdd_capacity = models.CharField(max_length=20, blank=True, null=True, verbose_name="HDD Capacity (GB/TB)")
    
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    purchase_date = models.DateField(blank=True, null=True)
    serial_number = models.CharField(max_length=100)
    accessories = models.CharField(max_length=100, null=True, blank=True)
    ip = models.GenericIPAddressField(protocol='both', unpack_ipv4=False, blank=True, null=True)  # Changed from DecimalField
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    applications = models.JSONField(
        default=dict,
        blank=True,
        help_text="Business applications and support systems installed on this asset"
    )
    other_applications = models.TextField(
        blank=True,
        null=True,
        verbose_name="Other Applications Description",
        help_text="Specify any additional software or applications not listed above")
    
    is_allocated = models.BooleanField(default=False)
    is_returned = models.BooleanField(default=False)

    def __str__(self):
        return self.serial_number
    
    def clean(self):
        if self.is_allocated and self.is_returned:
            raise ValidationError("An asset cannot be both allocated and returned at the same time")
        
        # Validate IMEI number format (if provided)
        if self.imei_number and not self.imei_number.isdigit():
            raise ValidationError("IMEI number should contain only digits")
        if self.imei_number and len(self.imei_number) not in [15, 16]:
            raise ValidationError("IMEI number should be 15 or 16 digits long")
    
    def current_allocation(self):
        """Returns the current active allocation if one exists"""
        return self.assetallocation_set.filter(return_date__isnull=True).first()
    
    def is_currently_allocated(self):
        """Check if asset is currently allocated"""
        return self.current_allocation() is not None
    
    
    
    def get_full_specs(self):
        """Return a formatted string with all specifications"""
        specs_list = []
        if self.processor:
            specs_list.append(f"Processor: {self.get_processor_display()}")
        if self.processor_cores:
            specs_list.append(f"Cores: {self.processor_cores}")
        if self.ram:
            specs_list.append(f"RAM: {self.get_ram_display()}")
        if self.storage_type:
            specs_list.append(f"Storage Type: {self.get_storage_type_display()}")
        if self.storage_capacity:
            specs_list.append(f"Storage: {self.storage_capacity}")
        if self.ssd_capacity:
            specs_list.append(f"SSD: {self.ssd_capacity}")
        if self.hdd_capacity:
            specs_list.append(f"HDD: {self.hdd_capacity}")
        
        return ", ".join(specs_list)


    @classmethod
    def get_import_fields(cls):
        """Return mapping of CSV column names to model fields"""
        return {
            'serial_number': 'serial_number',
            'name': 'name',
            'model': 'model',
            'type': 'type',
            'company': 'company',
            'purchase_date': 'purchase_date',
            'purchase_price': 'purchase_price',
            'imei_number': 'imei_number',
            'processor': 'processor',
            'ram': 'ram',
            'ssd_capacity': 'ssd_capacity',
            'hdd_capacity': 'hdd_capacity',
            'os': 'os',
            'os_licence': 'os_licence',
            'office': 'office',
            'office_licence': 'office_licence',
            'specs': 'specs',
            'accessories': 'accessories',
            'ip': 'ip',
            'applications_description': 'applications_description'
        }

    

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
    allocated_applications = models.JSONField(
        default=dict,
        blank=True,
        help_text="Applications included in this allocation"
    )

    def __str__(self):
        return f"{self.asset.name} - {self.asset.serial_number} - Allocated to {self.employee_allocated} on {self.allocation_date}"
    
    def save(self, *args, **kwargs):
        # When saving a new allocation, update the asset status
        if not self.pk:
            self.asset.is_allocated = True
            self.asset.is_returned = False
            self.asset.save()
        super().save(*args, **kwargs)
    
    def return_asset(self, return_date=None):
        """Mark this allocation as returned"""
        if self.return_date:
            raise ValidationError("This asset has already been returned")
        
        self.return_date = return_date or timezone.now().date()
        self.save()
        
        # Update asset status
        self.asset.is_allocated = False
        self.asset.is_returned = True
        self.asset.save()

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

    @classmethod
    def get_import_fields(cls):
        """Return mapping of CSV column names to model fields"""
        return {
            'asset_serial_number': 'asset',
            'employee_email': 'employee_allocated',
            'allocation_date': 'allocation_date',
            'return_date': 'return_date',
            'asset_status': 'asset_status'
        }

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
        # When creating a return, update the corresponding allocation
        if not self.pk:
            # Find the active allocation and mark it as returned
            allocation = AssetAllocation.objects.filter(
                asset=self.asset,
                return_date__isnull=True
            ).first()
            
            if allocation:
                allocation.return_asset(self.return_date)
            
            # Update asset status
            self.asset.is_allocated = False
            self.asset.is_returned = True
            self.asset.save()
        
        super().save(*args, **kwargs)

    def save(self, *args, **kwargs):
        # If this is a new allocation
        if not self.pk:
            if self.asset.is_allocated:
                raise ValidationError("This asset is already allocated.")
            
            # Mark asset as allocated and not returned
            self.asset.is_allocated = True
            self.asset.is_returned = False
            self.asset.save()
            
        super().save(*args, **kwargs)


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



