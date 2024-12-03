from django.db import models


# users model
class User(models.Model):
    username = models.CharField(max_length=255)
    telegram_id = models.BigIntegerField(unique=True)
    name = models.CharField(max_length=300)
    surname = models.CharField(max_length=300)
    phone = models.CharField(max_length=100, unique=True)
    type = models.CharField(max_length=1, default='u')  # u - user, d - driver
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        db_table = "users"

    def __str__(self):
        return self.name


# cars model
class Car(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    model = models.CharField(max_length=255)
    number = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['model']
        db_table = 'cars'

    def __str__(self):
        return self.model


# car image model
class CarImage(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    file_url = models.CharField(max_length=300)
    file_path = models.ImageField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        db_table = 'car_images'

    def __str__(self):
        return self.car.model


#  rating model
class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    grade = models.SmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['grade']
        db_table = "ratings"

    def __str__(self):
        return self.user.name


# direction model
class Direction(models.Model):
    driver = models.ForeignKey(User, on_delete=models.CASCADE)
    from_region_id = models.SmallIntegerField(default=0)
    from_district_id = models.SmallIntegerField(default=0)
    to_region_id = models.SmallIntegerField(default=0)
    to_district_id = models.SmallIntegerField(default=0)
    start_time = models.DateTimeField()
    seats = models.SmallIntegerField()
    price = models.BigIntegerField()
    comment = models.CharField(max_length=500, default="")
    status = models.SmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        db_table = "directions"

    def __str__(self):
        return f"{self.from_region_id} - {self.to_region_id})"


# user direction model
class UserDirection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    direction = models.ForeignKey(Direction, on_delete=models.CASCADE)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        db_table = "user_directions"

    def __str__(self):
        return f"{self.direction.from_place} - {self.direction.to_place})"


# comment model
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        db_table = "comments"

    def __str__(self):
        if len(self.comment) > 20:
            return self.comment[:20] + "..."
        return self.comment


class DirectionComment(models.Model):
    direction = models.ForeignKey(Direction, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Topic(models.Model):
    region_id = models.SmallIntegerField(default=0)
    topic_id = models.BigIntegerField()
    name = models.CharField(max_length=300, unique='')

    class Meta:
        ordering = ['name']
        db_table = "topics"
