from django.db import models
from django.contrib.auth.models import User
from embed_video.fields import EmbedVideoField
from django.urls import reverse
from django.utils.text import slugify

# Create your models here.
class Profile(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE)
    phone=models.PositiveIntegerField(blank=False,null=False)
    image=models.ImageField( upload_to="profilesimages",blank=False,null=False)
    address=models.CharField( max_length=150,blank=False,null=False)
    slug = models.SlugField(blank=True, null=False)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.user.username)
        super(Profile, self).save(*args, **kwargs)

DONATION_CHOICES=("Myself","Myself"),("Nonprofit","Nonprofit")
class Petition(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    target=models.PositiveIntegerField(blank=False,null=False)
    title=models.CharField(max_length=200,blank=False,null=False)
    for_who=models.CharField(max_length=200,blank=False,null=False,choices=DONATION_CHOICES)
    zip_code=models.PositiveIntegerField()
    image=models.ImageField(blank=False,null=False,upload_to="media-petition")
    story=models.TextField(max_length=1000,blank=True,null=True)
    youtube= EmbedVideoField(blank=True)
    donated=models.PositiveIntegerField(blank=True,null=False,default=0)
    created=models.DateTimeField( auto_now_add=True)
    edited=models.DateTimeField( auto_now=True)
    follows = models.ManyToManyField(User, related_name="petitions")

    def total_follows(self):
        return self.follows.count()

    def get_absolute_url(self):
        return reverse("core:petition_detail", kwargs={"pk": self.pk})
    
    @property
    def meter(self):
        return int(self.donated/self.target*100)
    def __str__(self):
        return self.title
    


class History(models.Model):
    user = models.ForeignKey( User, on_delete=models.CASCADE)
    amount=models.IntegerField(blank=False,null=False)
    petition=models.ForeignKey( Petition, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user.username)+" donated "+str(self.amount)+"$  for "+ str(self.petition.title) + " (id): "+str(self.petition.id)
    