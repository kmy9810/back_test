from .slack_notify import slack_notify
from django.db.models import Q
from rest_framework.generics import get_object_or_404
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Recipe, Review, Comment
from .serializers import RecipeSerializer, ReviewSerializer, CommentSerializer, SearchSerializer


# 레시피 카테 고리별 조회 및 등록
class RecipeView(APIView):
    def get(self, request, category_id, offset=0):
        # category 모델 생성! -> 확장성을 위해 빼자
        CheckUserView.as_view()
        category = {1: "국&찌개", 2: "밥", 3: "반찬", 4: "후식", 5: "일품"}
        limit = 8
        recipe = Recipe.objects.filter(category=category[category_id])[offset:offset+limit]
        total = Recipe.objects.filter(category=category[category_id]).count()
        serializer = RecipeSerializer(recipe, many=True)
        data = {
            'data': serializer.data,
            'total': total
        }
        return Response(data, status=status.HTTP_200_OK)


# 레시피 상세 조회
class RecipeDetailView(APIView):
    def get(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        serializer = RecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, recipe_id):
        CheckUserView.as_view()
        recipe = get_object_or_404(Recipe, id=recipe_id)
        serializer = RecipeSerializer(recipe, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, recipe_id):
        CheckUserView.as_view()
        recipe = get_object_or_404(Recipe, id=recipe_id)
        recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# 리뷰 조회 및 작성
class ReviewView(APIView):
    def get(self, request, recipe_id=None):
        review = Review.objects.all()
        serializer = ReviewSerializer(review, many=True)
        return Response(serializer.data[::-1], status=status.HTTP_200_OK)

    def post(self, request, recipe_id):
        # 이미지가 빈값으로 올 땐 copy를 사용해서 변경!
        # deepcopy -> copy모듈 임포트? -> 완전 복사!(안전)
        # try, except 사용 고려 -> 추가 예외 처리!
        CheckUserView.as_view()
        if request.data['image'] == 'undefined':
            data = request.data.copy()
            data['image'] = ''
            serializer = ReviewSerializer(data=data)
        else:
            serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(recipe_id=recipe_id, user_id=request.user.id)
            slack_message = f"[새로운 후기 알람] \n" \
                            f"레시피 : {serializer.data['recipe']} \n" \
                            f"후기 제목 : {serializer.data['title']} \n" \
                            f"내용 : {serializer.data['content']} \n"
            slack_notify(slack_message, "#프로젝트", username='후기 알람봇')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 리뷰 상세
class ReviewDetailView(APIView):
    def get(self, request, review_id):
        review = get_object_or_404(Review, id=review_id)
        serializer = ReviewSerializer(review)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, review_id):
        CheckUserView.as_view()
        review = get_object_or_404(Review, id=review_id)
        serializer = ReviewSerializer(review, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, review_id):
        CheckUserView.as_view()
        review = get_object_or_404(Review, id=review_id)
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentView(APIView):
    # pk = review_id
    def get(self, request, pk):
        comment = Comment.objects.filter(review_id=pk)
        serializer = CommentSerializer(comment, many=True)
        return Response(serializer.data[::-1], status=status.HTTP_200_OK)

    # pk = review_id
    def post(self, request, pk):
        CheckUserView.as_view()
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            # 유저도 같이 저장 추가 예정
            serializer.save(review_id=pk, user_id=request.user.id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # pk = comment_id
    # patch, put 차이 찾아 보자
    def patch(self, request, pk):
        CheckUserView.as_view()
        comment = get_object_or_404(Comment, id=pk)
        serializer = CommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # pk = comment_id
    def delete(self, request, pk):
        CheckUserView.as_view()
        comment = get_object_or_404(Comment, id=pk)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SearchView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        search_word = request.data['search']
        ingredients = search_word.split(',')[:3]  # 최대 3개의 재료 추출
        # 재료를 모두 포함 하는 레시피 필터링
        # Recipe.objects.all() -> 다 가져 오지 말고 한번에 해당 되는 내용을 가져 오자!
        # 혹시 영어가 될 때를 대비 해서 icontains(대소문자)
        recipes = Recipe.objects.filter(*[Q(ingredients__icontains=ingredient) |
                                          Q(name__icontains=ingredient) for ingredient in ingredients])

        serializer = SearchSerializer(recipes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CheckUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]
