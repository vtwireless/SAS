from django.db import models


class PrioritySchema(models.Model):
    category_type = models.TextField()
    category_values = models.TextField()
    priority_index = models.TextField()

