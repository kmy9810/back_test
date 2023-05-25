from django.db import models
from django.urls import reverse


class Recipe(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    tip = models.CharField(max_length=255)
    ingredients = models.TextField()
    tag = models.CharField(max_length=255)
    car = models.CharField(max_length=255)
    na = models.CharField(max_length=255)
    fat = models.CharField(max_length=255)
    pro = models.CharField(max_length=255)
    kcal = models.CharField(max_length=255)
    main_img = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self, category):
        if category == 'recipe_detail':
            return reverse('recipe_detail_view', kwargs={'recipe_id': self.id})
        elif category == 'review':
            return reverse('review_view', kwargs={'recipe_id': self.id})


class SubRecipe(models.Model):
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE)
    turn = models.TextField()
    img = models.TextField()


class Review(models.Model):
    # user pk 추가
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    image = models.ImageField(null=True, blank=True)
    star = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('review_detail_view', kwargs={'review_id': self.id})


class Comment(models.Model):
    # user pk 추가
    review = models.ForeignKey('Review', on_delete=models.CASCADE)
    comment = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


