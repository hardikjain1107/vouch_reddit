from django.urls import path
from reddit_post.views import ShowReddit
from django.contrib.auth.decorators import login_required

urlpatterns = [
	path('' , login_required(ShowReddit.as_view()) , name = 'show_reddit'),
]