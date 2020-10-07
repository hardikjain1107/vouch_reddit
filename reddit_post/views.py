from django.shortcuts import render
from django.views import View
from allauth.socialaccount.models import SocialToken
from reddit_vouch_project.settings import API_BASE_URL
import requests
from reddit_post.models import Post
from django.db.models import Count

# Create your views here.
class ShowReddit(View):
	def _base_headers(self):
		return {"User-Agent": "/u/hardik_jain"}

	def _get_token(self , request):
		return str(SocialToken.objects.get(account__user=request.user, account__provider='reddit'))

	def _get_response(self , url , request):
		headers = self._base_headers()
		access_token = self._get_token(request)
		headers.update({"Authorization": "bearer " + str(access_token)})
		response = requests.get(API_BASE_URL + url , headers=headers)
		return response.json()

	def _get_posts(self, subreddit_name , request , limit = 5):
		posts_json = self._get_response(subreddit_name + '.json?limit=' + str(limit), request)
		return posts_json

	def _save_posts(self , posts_json , user):
		for i in range (len(posts_json['data']['children'])):
			title = posts_json['data']['children'][i]['data']['title']
			url = posts_json['data']['children'][i]['data']['url']
			author = posts_json['data']['children'][i]['data']['author']
			upvotes = posts_json['data']['children'][i]['data']['ups']
			link = "https://www.reddit.com" + posts_json['data']['children'][i]['data']['permalink']
			post = Post(title = title , url = url , author = author , upvotes = upvotes , of_user = user , link  = link)
			post.save()

	def _save_posts_for_user(self , request , limit = 5 ):
		user_subreddits = self._get_response("subreddits/mine/subscriber.json?limit=" + str(limit), request)
		list_user_subreddits = []
		for i in range(len(user_subreddits['data']['children'])):
			list_user_subreddits.append(user_subreddits['data']['children'][i]['data']['display_name_prefixed'])
			self._save_posts(self._get_posts(user_subreddits['data']['children'][i]['data']['display_name_prefixed'] , request) , request.user)
		return list_user_subreddits

	def _retrieve_posts(self ):
		posts = Post.objects.all().exclude(url__startswith = "https://www.reddit.com")[:10]
		return posts

	def _retrieve_users(self ):
		user_counts = Post.objects.values('author').annotate(count=Count('author')).order_by("-count")[:10]
		return user_counts

	def get(self , request):
		user_subreddits = self._save_posts_for_user(request)
		posts = self._retrieve_posts()
		user_counts = self._retrieve_users()
		context = {
		'posts' : posts,
		'user_counts' : user_counts,
		'user_subreddits' : user_subreddits,
		}
		return render(request, "show_reddit.html" , context = context)