from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dir = ""  # models.CharField(max_length=100, default=".")
    dataset_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} Profile"
    
    # def save(self, *args, **kwargs):
    #     super().save(args, kwargs)


class Obj(models.Model):
    name = models.CharField(max_length=100, default='New Obj')
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    extension = models.CharField(max_length=20, default='obj')
    model_file_size = models.IntegerField(default=0)
    model_vertices = models.IntegerField(default=0)
    model_height = models.IntegerField(default=0)
    model_width = models.IntegerField(default=0)
    model_depth = models.IntegerField(default=0)
    view_profile = models.ImageField(upload_to='objs')
    blob_str = models.CharField(max_length=100, default='')
    tags = models.TextField(default='[]')    # list of tags
    view_ym = models.CharField(max_length=240, default='')
    view_yp = models.CharField(max_length=240, default='')
    view_xp = models.CharField(max_length=240, default='')
    view_xm = models.CharField(max_length=240, default='')
    view_zp = models.CharField(max_length=240, default='')
    view_zm = models.CharField(max_length=240, default='')



class Dataset(models.Model):
    # private info
    name = models.CharField(max_length=200, default='dataset')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    last_modified = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(default=timezone.now)
    # image generation settings
    objects_per_image = models.IntegerField(default=5)
    job_generated = models.BooleanField(default=False)
    objs_list_json_str = models.TextField(default='[]')
    no_images = models.IntegerField(default=10)
    image_height = models.IntegerField(default=100)
    image_width = models.IntegerField(default=100)
    image_extension = models.CharField(max_length=8, choices=(('JPEG', 'JPEG'),), default='JPEG')
    color_mode = models.CharField(max_length=8, choices=(('RGB','RGB'),), default='RGB')
    json_label = models.BooleanField(default=True)
    segmented_labelling = models.BooleanField(default=False)
