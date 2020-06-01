from .models import Post
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
import os
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from . import serializers
from rest_framework.views import APIView
from .utils import get_and_authenticate_user, create_user_account
from rest_framework import viewsets
import json

class AllPosts(viewsets.ViewSet):
	permission_classes = (IsAuthenticated,)
	@action(methods=['GET', ], detail=False)
	def showposts(self, request):
		posts= Post.objects.all().order_by('create_date').reverse()
		if posts:
			data= serializers.PostSerializer(posts, many=True).data()
		else:
			data={'Error': "No posts"}
		return Response(data)


	@action(methods=['POST', ], detail=False)
	def deletepost(self, request, pk):
		post= Post.objects.filter(pk=pk).first()
		if post:
			post.delete()
			data={'Massage': "Post Deleted"}
		else:
			data={'Error': "Post not found"}
		return Response(data)


class AuthViewSet(viewsets.ViewSet):

	permission_classes = [AllowAny, ]
	serializer_class = serializers.EmptySerializer
	
	@action(methods=['POST', ], detail=False)
	def login(self, request):
		data=json.dumps(request.data)
		data=json.loads(data)
		user = get_and_authenticate_user(data["username"], data["password"])
		data = serializers.AuthUserSerializer(user).data
		return Response(data=data, status=status.HTTP_200_OK)
	

	@action(methods=['POST', ], detail=False)
	def register(self, request):
		serializer = serializers.UserRegisterSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		user = create_user_account(**serializer.validated_data)
		data = serializers.AuthUserSerializer(user).data
		return Response(data=data, status=status.HTTP_201_CREATED)

	@action(methods=['GET', ], detail=False)
	def logout(self, request):
		if request.user.is_authenticated:
			request.user.auth_token.delete()
			data = {'success': 'Sucessfully logged out'}
		else:
			data = {'failed': 'Have not token'}
		return Response(data=data, status=status.HTTP_200_OK)