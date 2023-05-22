from django.db import models


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


class SubRecipe(models.Model):
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE)
    turn = models.TextField()
    img = models.TextField()


class Review(models.Model):
    # user pk 추가
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE)
    content = models.TextField()
    # img = models.ImageField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Comment(models.Model):
    # user pk 추가
    review = models.ForeignKey('Review', on_delete=models.CASCADE)
    comment = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


