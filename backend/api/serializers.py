from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from users.serializers import CustomUserSerializer

from api.models import (FavoriteRecipe, Ingredient, Recipe, RecipeIngredient,
                        ShoppingCart, Tag)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time')

    def get_user(self):
        return self.context.get('request').user

    def get_request(self):
        return self.context.get('request')

    def get_is_favorited(self, obj):
        request = self.get_request()
        user = self.get_user()
        if not request or request.user.is_anonymous:
            return False
        return user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.get_request()
        user = self.get_user()
        if not request or request.user.is_anonymous:
            return False
        return user.shopping_carts.filter(recipe=obj).exists()


class IngredientWriteSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField()
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'Количество ингредиента строго положительное и больше нуля')
        return value


class RecipeWriteSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    ingredients = IngredientWriteSerializer()
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'ingredients', 'author', 'image', 'name',
                  'text', 'cooking_time')

    def validate(self, data):
        ingredients = data['ingredients']
        ingredients_list = []
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            if ingredient_id in ingredients_list:
                raise serializers.ValidationError({
                    'ingredients': 'Ингредиенты должны быть уникальными'
                })
            ingredients_list.append(ingredient_id)
            amount = ingredient['amount']
            if int(amount) <= 0:
                raise serializers.ValidationError({
                    'amount': 'Количество ингредиента должно быть больше нуля'
                })

        tags = data['tags']
        if not tags:
            raise serializers.ValidationError({
                'tags': 'Нужно выбрать хотя бы один тэг'
            })
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise serializers.ValidationError({
                    'tags': 'Тэги должны быть уникальными'
                })
            tags_list.append(tag)

        cooking_time = data['cooking_time']
        if int(cooking_time) <= 0:
            raise serializers.ValidationError({
                'cooking_time': 'Время приготовления должно быть больше 0'
            })
        return data

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount'],
            )

    def create_tags(self, tags, recipe):
        recipe.tags.set(tags)

    def create(self, validated_data):
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.create_tags(tags, recipe)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        RecipeIngredient.objects.filter(recipe=instance).delete()
        self.create_tags(validated_data.pop('tags'), instance)
        self.create_ingredients(validated_data.pop('ingredients'), instance)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeReadSerializer(instance, context=context).data


class RecipeToRepresentationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = FavoriteRecipe
        fields = ('user', 'recipe')

    def validate(self, data):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        recipe = data['recipe']
        if FavoriteRecipe.objects.filter(
                user=request.user, recipe=recipe).exists():
            raise serializers.ValidationError({
                'status': 'Рецепт уже есть в избранном'
            })
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeToRepresentationSerializer(
            instance.recipe, context=context).data


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeToRepresentationSerializer(
            instance.recipe, context=context).data