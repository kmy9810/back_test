from rest_framework.serializers import ValidationError
from rest_framework import serializers
from .models import Recipe, SubRecipe, Comment, Review


class RecipeSerializer(serializers.ModelSerializer):
    sub_recipe_set = serializers.SerializerMethodField()  # 조리법 데이터 추가
    review_set = serializers.SerializerMethodField()  # 해당 레시피 모든 후기 추가

    def get_sub_recipe_set(self, obj):
        sub_recipe = SubRecipe.objects.filter(recipe_id=obj.id)
        sub_recipe_list = SubRecipeSerializer(sub_recipe, many=True)
        return sub_recipe_list.data

    def get_review_set(self, obj):
        review = Review.objects.filter(recipe_id=obj.id)
        review_list = ReviewSerializer(review, many=True)
        return review_list.data

    class Meta:
        model = Recipe
        fields = '__all__'


class SubRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubRecipe
        exclude = ['id',]


class ReviewSerializer(serializers.ModelSerializer):
    comment_set = serializers.SerializerMethodField()

    def get_comment_set(self, obj):
        comment = Comment.objects.filter(review_id=obj.id)
        comment_list = CommentSerializer(comment, many=True)
        return comment_list.data

    class Meta:
        model = Review
        fields = '__all__'
        extra_kwargs = {"user": {"required": False},
                        "recipe": {"required": False}}


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
        extra_kwargs = {"user": {"required": False},
                        "review": {"required": False}}
