from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Post(models.Model):
	title = models.TextField()
	url = models.URLField()
	upvotes = models.IntegerField()
	author = models.TextField()
	of_user = models.ForeignKey(User , on_delete = models.CASCADE , default = 1)
	link = models.URLField(default = 1)
	
	def __str__(self):
		return self.title + "\t" + self.author + "\t" + self.of_user