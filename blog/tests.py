from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from django.contrib.auth.models import User

from accounts.models import NewsletterSubscriber
from blog.models import Category, Post


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class PostPublishingTests(TestCase):
    def test_published_post_sends_mail_to_subscribers(self):
        NewsletterSubscriber.objects.create(email='reader@example.com', name='Reader')
        category = Category.objects.create(name='Tech')
        author = User.objects.create_user(username='author', password='secret123')

        post = Post.objects.create(
            category=category,
            title='Nouveau contenu',
            excerpt='Résumé',
            slug='nouveau-contenu',
            author=author,
            status='draft',
        )

        post.status = 'published'
        post.save()

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Nouveau contenu', mail.outbox[0].subject)
        self.assertEqual(mail.outbox[0].to, ['reader@example.com'])

    def test_homepage_shows_popular_posts_by_view_count(self):
        category = Category.objects.create(name='Tech')
        author = User.objects.create_user(username='author2', password='secret123')

        popular_post = Post.objects.create(
            category=category,
            title='Article le plus vu',
            excerpt='Résumé',
            slug='article-le-plus-vu',
            author=author,
            status='published',
            views=10,
        )
        less_popular_post = Post.objects.create(
            category=category,
            title='Article moins vu',
            excerpt='Résumé',
            slug='article-moins-vu',
            author=author,
            status='published',
            views=3,
        )

        response = self.client.get(reverse('blog:homepage'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Articles populaires')
        self.assertEqual([post.id for post in response.context['popular_posts']], [popular_post.id, less_popular_post.id])

    def test_article_page_displays_interaction_actions_and_toggles_state(self):
        category = Category.objects.create(name='Design')
        author = User.objects.create_user(username='author3', password='secret123')
        post = Post.objects.create(
            category=category,
            title='Article interactif',
            excerpt='Résumé',
            slug='article-interactif',
            author=author,
            status='published',
        )

        response = self.client.get(reverse('blog:post_single', kwargs={'post': post.slug}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Partager')
        self.assertContains(response, 'J’aime')
        self.assertContains(response, 'Enregistrer')

        self.client.post(reverse('blog:post_single', kwargs={'post': post.slug}), {'action': 'like'})
        self.assertIn(post.id, self.client.session['liked_posts'])

    def test_saved_posts_page_lists_auth_users_saved_articles(self):
        category = Category.objects.create(name='Design')
        author = User.objects.create_user(username='author4', password='secret123')
        user = User.objects.create_user(username='reader', password='secret123')
        post = Post.objects.create(
            category=category,
            title='Article sauvegardé',
            excerpt='Résumé',
            slug='article-sauvegarde',
            author=author,
            status='published',
        )
        post.saved_by.add(user)

        self.client.force_login(user)
        response = self.client.get(reverse('blog:saved_posts'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Article sauvegardé')

    def test_search_suggestions_returns_matching_posts(self):
        category = Category.objects.create(name='Design')
        author = User.objects.create_user(username='author5', password='secret123')
        Post.objects.create(
            category=category,
            title='Guide de recherche',
            excerpt='Résumé',
            slug='guide-de-recherche',
            author=author,
            status='published',
        )

        response = self.client.post(
            reverse('blog:post_search'),
            {'action': 'post', 'ss': 'recherche'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('Guide de recherche', response.content.decode())
