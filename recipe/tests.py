from django.urls import reverse
from rest_framework.test import APITestCase
from .models import Recipe, Review, Comment
from .serializers import RecipeSerializer, ReviewSerializer, CommentSerializer, SearchSerializer
from faker import Faker


class RecipeTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()
        cls.recipes = []
        for i in range(10):
            cls.recipes.append(Recipe.objects.create(name=cls.faker.sentence(), category=cls.faker.word(),
                                                 tip=cls.faker.word(),ingredients=cls.faker.sentence(),
                                                     tag=cls.faker.word(), car=cls.faker.word(), na=cls.faker.word(),
                                                     fat=cls.faker.word(), pro=cls.faker.word()))
        # cls.user = User.objects.create_user(username='mimi', email='miyeong@naver.com', password='1234')

    # def setUp(self):
    #     self.access_token = self.client.post(reverse('token_obtain_pair'), self.data).data['access']

    def test_get_recipe_list(self):
        response = self.client.get(
            path=reverse('recipe_view'),
        )
        self.assertEquals(response.status_code, 200)

    def test_get_recipe_detail(self):
        for recipe in self.recipes:
            url = recipe.get_absolute_url(category='recipe_detail')
            response = self.client.get(path=url)
            serializer = RecipeSerializer(recipe).data
            for k, v in serializer.items():
                self.assertEquals(response.data[k], v)

    def test_patch_recipe_detail(self):
        for recipe in self.recipes:
            url = recipe.get_absolute_url(category='recipe_detail')
            response = self.client.patch(path=url,
                                         data={'name': self.faker.sentence()})
            self.assertEquals(response.status_code, 200)

    def test_delete_todo(self):
        for recipe in self.recipes:
            url = recipe.get_absolute_url(category='recipe_detail')
            response = self.client.delete(path=url)
            self.assertEquals(response.status_code, 204)


class ReviewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()
        cls.recipes = []
        for i in range(10):
            cls.recipes.append(Recipe.objects.create(name=cls.faker.sentence(), category=cls.faker.word(),
                                                     tip=cls.faker.word(), ingredients=cls.faker.sentence(),
                                                     tag=cls.faker.word(), car=cls.faker.word(), na=cls.faker.word(),
                                                     fat=cls.faker.word(), pro=cls.faker.word()))

    def test_post_review(self):
        for recipe in self.recipes:
            url = recipe.get_absolute_url(category='review')
            response = self.client.post(path=url,
                                        data={'title': self.faker.sentence(), 'content': self.faker.sentence()})
            self.assertEquals(response.status_code, 201)
