from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import NFCBatch, NFCItem, Moment
from .utils.nfc_generator import generate_secure_token, generate_activation_code, hash_activation_code, check_activation_code
import secrets


class NFCGeneratorTests(TestCase):
    def test_generate_secure_token_length(self):
        self.assertEqual(len(generate_secure_token()), 12)

    def test_generate_activation_code_format(self):
        code = generate_activation_code()
        parts = code.split('-')
        self.assertEqual(len(parts), 2)
        self.assertTrue(parts[0].isalpha())
        self.assertTrue(parts[1].isdigit())

    def test_hash_and_check_activation_code(self):
        plain = "AMOR-8372"
        hashed = hash_activation_code(plain)
        self.assertTrue(check_activation_code(plain, hashed))
        self.assertFalse(check_activation_code("WRONG-0000", hashed))


class NFCBatchModelTests(TestCase):
    def setUp(self):
        self.batch = NFCBatch.objects.create(name="Test Batch", support_type="pulsera", quantity=5)

    def test_batch_creation(self):
        self.assertEqual(str(self.batch), "Test Batch (pulsera) - 5 unidades")

    def test_item_creation(self):
        token = generate_secure_token()
        code = generate_activation_code()
        item = NFCItem.objects.create(
            batch=self.batch, public_token=token,
            activation_code_hash=hash_activation_code(code),
        )
        self.assertEqual(item.status, 'inactive')
        self.assertIn("identylog.com/t/", item.public_url)


class MomentModelTests(TestCase):
    def setUp(self):
        batch = NFCBatch.objects.create(name="Test Batch", support_type="tarjeta", quantity=1)
        item = NFCItem.objects.create(
            batch=batch, public_token=generate_secure_token(),
            activation_code_hash=hash_activation_code("TEST-1234"),
            user=User.objects.create_user(username="testuser", password=secrets.token_urlsafe(12))
        )
        self.moment = Moment.objects.create(
            nfc_item=item, title="Test Moment",
            youtube_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        )

    def test_youtube_id_extraction(self):
        self.assertEqual(self.moment.youtube_video_id, "dQw4w9WgXcQ")
        self.assertEqual(self.moment.youtube_embed_url, "https://www.youtube.com/embed/dQw4w9WgXcQ")


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        batch = NFCBatch.objects.create(name="Batch", support_type="pulsera", quantity=1)
        self.token = generate_secure_token()
        self.item = NFCItem.objects.create(
            batch=batch, public_token=self.token,
            activation_code_hash=hash_activation_code("AMOR-1234"),
            status='active',
            user=User.objects.create_user(username="owner", password=secrets.token_urlsafe(12))
        )
        self.moment = Moment.objects.create(nfc_item=self.item, title="My Moment")

    def test_landing_publica_returns_200(self):
        self.assertEqual(self.client.get(f'/t/{self.token}/').status_code, 200)

    def test_landing_publica_inactive_redirects(self):
        inactive_token = generate_secure_token()
        NFCItem.objects.create(
            batch=NFCBatch.objects.create(name="Batch2", support_type="pulsera", quantity=1),
            public_token=inactive_token,
            activation_code_hash=hash_activation_code("INACT-9999")
        )
        self.assertRedirects(self.client.get(f'/t/{inactive_token}/'), f'/activar/{inactive_token}/')

    def test_landing_inicio_returns_200(self):
        self.assertEqual(self.client.get('/').status_code, 200)

    def test_login_view_returns_200(self):
        self.assertEqual(self.client.get('/login/').status_code, 200)

    def test_register_view_returns_200(self):
        self.assertEqual(self.client.get('/registro/').status_code, 200)

    def test_user_registration(self):
        pwd = secrets.token_urlsafe(12)
        response = self.client.post('/registro/', {
            'username': 'newuser',
            'password1': pwd,
            'password2': pwd,
        })
        self.assertRedirects(response, '/dashboard/')
        self.assertTrue(User.objects.filter(username='newuser').exists())
