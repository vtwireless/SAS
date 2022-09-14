from django.db import models


class PrioritySchema(models.Model):
    category_type = models.CharField(max_length=255)
    category_values = models.CharField(max_length=255)
    priority_index = models.CharField(max_length=255)

