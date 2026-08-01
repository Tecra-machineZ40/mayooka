from django.test import TestCase
from django.urls import reverse

from accounts.models import NewsletterSubscriber


class NewsletterSubscriptionTests(TestCase):
    def test_subscribe_newsletter_creates_subscriber(self):
        response = self.client.post(
            reverse('accounts:newsletter'),
            {'name': 'Ada', 'email': 'ada@example.com'},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(NewsletterSubscriber.objects.filter(email='ada@example.com').exists())
