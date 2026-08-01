from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from mptt.models import TreeForeignKey, MPTTModel
from accounts.models import NewsletterSubscriber
#from django_ckeditor_5.fields import CKEditor5Field



def user_directory_path(instance, filename):
    return 'posts/{0}/{1}'.format(instance.id, filename)

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Post(models.Model):

    class NewManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset() .filter(status='published')

    options = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, default=1)
    title = models.CharField(max_length=250)
    #text=CKEditor5Field('Text', config_name='extends')
    content = models.TextField(blank=True, default='')
    excerpt = models.TextField(null=True)
    image = models.ImageField(upload_to=user_directory_path, default='posts/soleil.jpeg')
    image_alt = models.CharField(max_length=180, blank=True, default='')
    views = models.PositiveIntegerField(default=0)
    slug = models.SlugField(max_length=250, unique_for_date='publish')
    seo_title = models.CharField(max_length=70, blank=True, default='')
    seo_description = models.CharField(max_length=170, blank=True, default='')
    canonical_url = models.URLField(blank=True, default='')
    publish = models.DateField(default=timezone.now)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='blog_posts')
    status = models.CharField(max_length=10, choices=options, default='draft')
    saved_by = models.ManyToManyField(User, related_name='saved_posts', blank=True)
    objects = models.Manager()  # default manager
    newmanager = NewManager()  # custom manager

    def get_absolute_url(self):
        return reverse('blog:post_single', args=[self.slug])

    class Meta:
        ordering = ('-publish',)

    def __str__(self):
        return self.title

class Comment(MPTTModel):

    """ class Comment(models.Model): """

    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='comments')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    name = models.CharField(max_length=50)
    email = models.EmailField()
    content = models.TextField()
    publish = models.DateField(auto_now_add=True)
    status = models.BooleanField(default=True)

    class MPTTMeta:

        order_insertion_by = ['publish']

        """ class Meta:
            ordering = ('publish',) """

    def __str__(self):
        return f'Comment by {self.name}'


@receiver(pre_save, sender=Post)
def remember_post_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._previous_status = Post.objects.get(pk=instance.pk).status
        except Post.DoesNotExist:
            instance._previous_status = None
    else:
        instance._previous_status = None


@receiver(post_save, sender=Post)
def notify_subscribers_on_publish(sender, instance, **kwargs):
    previous_status = getattr(instance, '_previous_status', None)
    if previous_status == 'published' or instance.status != 'published':
        return

    subscribers = NewsletterSubscriber.objects.exclude(email='').exclude(email__isnull=True)
    if not subscribers.exists():
        return

    recipient_list = [subscriber.email for subscriber in subscribers]
    subject = f'Nouvel article publié : {instance.title}'
    message = (
        f'Bonjour,\n\n'
        f'Un nouvel article a été publié : {instance.title}\n\n'
        f'{instance.excerpt or "Découvrez-le dès maintenant."}\n\n'
        f'Lien : {getattr(settings, "SITE_URL", "http://127.0.0.1:8000")}{instance.get_absolute_url()}'
    )
    send_mail(subject, message, getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@mayooka.local'), recipient_list, fail_silently=False)

