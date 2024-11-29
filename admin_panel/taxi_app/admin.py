from django.contrib import admin

from .models import (Direction, UserDirection, User, Car, CarImage, Rating, Comment, DirectionComment)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['name', 'username', 'telegram_id', 'phone', 'created_at', 'updated_at']
    ordering = ['name']
    search_fields = ['name', 'username', 'created_at']


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    def get_car_driver_name(self, obj):
        return obj.user.name if obj.user else None
    get_car_driver_name.short_description = 'car owner'

    list_display = ['model', 'number', 'get_car_driver_name', 'created_at', 'updated_at']
    ordering = ['model']
    search_fields = ['model', 'number', 'get_car_driver_name']


@admin.register(CarImage)
class CarImageAdmin(admin.ModelAdmin):
    def car_model(self, obj):
        return obj.car.model if obj.car else None
    car_model.short_description = 'model'

    def get_car_driver_name(self, obj):
        return obj.user.name if obj.user else None
    get_car_driver_name.short_description = 'car owner'


    list_display = ['get_car_driver_name', 'car_model']
    # ordering = ['car_model']
    # search_fields = ['car_model', 'get_car_driver_name']


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    def get_rating_driver_name(self, obj):
        return obj.user.name if obj.user else None
    get_rating_driver_name.short_description = 'Driver'

    # Corrected list_display with commas separating items
    list_display = ['get_rating_driver_name', 'grade', 'created_at', 'updated_at']
    # ordering = ['get_rating_driver_name', '-grade']
    # search_fields = ['get_rating_driver_name', 'grade']


@admin.register(Direction)
class DirectionAdmin(admin.ModelAdmin):
    def get_direction_driver_name(self, obj):
        return obj.driver.name if obj.driver else None
    get_direction_driver_name.short_description = 'driver'

    # list_display = ['start_time', 'from_place', 'to_place', 'comment', 'price', 'seats' ,'get_direction_driver_name' ,'created_at',
    #                 'updated_at']
    # ordering = ['from_place', 'price']
    # search_fields = ['from_place', 'to_place']
    

@admin.register(UserDirection)
class UserDirectionAdmin(admin.ModelAdmin):
    def get_car_driver_name(self, obj):
        return obj.user.name if obj.user else None
    get_car_driver_name.short_description = 'driver'

    def get_direction_from_place(self, obj):
        return obj.direction.from_place if obj.direction else None
    get_direction_from_place.short_description = 'from'

    def get_direction_to_place(self, obj):
        return obj.direction.to_place if obj.direction else None
    get_direction_to_place.short_description = 'to'

    list_display = ['get_direction_from_place', 'get_direction_to_place', 'get_car_driver_name',
                    'created_at', 'updated_at']
    # ordering = ['get_direction_from_place']
    # search_fields = ['direction.from_place', 'direction.to_place', 'get_car_driver_name']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    def get_comment_user_name(self, obj):
        return obj.user.name if obj.user else None
    get_comment_user_name.short_description = 'name'

    list_display = ['get_comment_user_name', 'comment', 'created_at', 'updated_at']
    ordering = ['created_at']
    # search_fields = ['get_comment_user_name', 'comment']


@admin.register(DirectionComment)
class DirectionCommentAdmin(admin.ModelAdmin):
    def get_comment_user_name(self, obj):
        return obj.comment.user.name if obj.comment and obj.comment.user else None
    get_comment_user_name.short_description = 'Name'

    def get_comment_text(self, obj):
        return obj.comment.comment if obj.comment else None
    get_comment_text.short_description = 'Comment Text'

    def get_direction_from_place(self, obj):
        return obj.direction.from_place if obj.direction else None
    get_direction_from_place.short_description = 'From'

    def get_direction_to_place(self, obj):
        return obj.direction.to_place if obj.direction else None
    get_direction_to_place.short_description = 'To'

    def get_car_driver_name(self, obj):
        return obj.direction.driver.name if obj.direction and obj.direction.driver else None
    get_car_driver_name.short_description = 'Driver'

    # Fixed list_display with proper commas
    list_display = [
        'get_comment_user_name',
        'get_comment_text',
        'get_direction_from_place',
        'get_direction_to_place',
        'get_car_driver_name',
        'created_at',
        'updated_at',
    ]

    ordering = ['-created_at']
    # search_fields = ['get_comment_user_name', 'get_comment_text', 'get_car_driver_name']