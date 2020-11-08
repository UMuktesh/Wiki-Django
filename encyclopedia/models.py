from django.db import models

# Create your models here.

class log(models.Model):
    username = models.CharField(max_length=32)
    wikiname = models.CharField(max_length=32)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        fmt = "%d %b %Y %X"
        return f"{self.username} edited at {self.time.strftime(fmt)}"

class creation(models.Model):
    username = models.CharField(max_length=32)
    wikiname = models.CharField(max_length=32)
    creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        fmt = "%d %b %Y %X"
        return f"Created at {self.creation.strftime(fmt)} by {self.username}"