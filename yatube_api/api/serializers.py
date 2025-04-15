from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from django.db.utils import IntegrityError
from posts.models import Comment, Post, Group, Follow
from django.contrib.auth import get_user_model

User = get_user_model()


class PostSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        fields = '__all__'
        model = Post


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = '__all__'
        model = Comment
        read_only_fields = ('post',)


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='username', read_only=True)
    following = serializers.CharField()

    class Meta:
        model = Follow
        fields = '__all__'

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError:
            raise serializers.ValidationError(
                {"error": "Вы уже подписаны на этого пользователя."},
                code=400
            )

    def validate_following(self, value):
        try:
            user = User.objects.get(username=value)
            if user == self.context['request'].user:
                raise serializers.ValidationError("Нельзя подписаться на себя")
            return user
        except User.DoesNotExist:
            raise serializers.ValidationError("Пользователь не найден")
