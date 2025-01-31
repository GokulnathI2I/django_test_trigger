from django.db import models


class SuperOrg(models.Model):
    name = models.CharField(max_length=50)
    flag = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}"
    
    class Meta:
        db_table = "super_org"
    


class Demo(models.Model):
    first_name = models.CharField(max_length=30)
    middle_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30)
    suffix = models.CharField(max_length=10, null=True, blank=True)
    super_org = models.ForeignKey(SuperOrg, on_delete=models.CASCADE)
    name_formats = models.JSONField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.first_name}"
    
    class Meta:
        db_table = "my_demo"