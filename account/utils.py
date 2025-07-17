import redis
import tempfile
import random
from config import settings
from PIL import Image


def generate_test_image():
    image = Image.new('RGB', (100, 100), color='red')
    tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
    image.save(tmp_file, format='JPEG')
    tmp_file.seek(0)
    return tmp_file


redis_client = redis.Redis(
    host=getattr(settings, "REDIS_HOST", "localhost"),
    port=getattr(settings, "REDIS_PORT", 6379),
    db=0,
    decode_responses=True
)


def set_otp(phone, otp, ttl=3*60):
    """Stores the OTP for a phone number in Redis"""
    redis_client.setex(f"otp:{phone}", ttl, otp)


def get_otp(phone):
    """Retrieves the OTP for a phone number from Redis"""
    return redis_client.get(f"otp:{phone}")


def generate_otp(digits=6):
    """Generate a numeric OTP of given length"""
    return ''.join(str(random.randint(0, 9)) for i in range(digits))


def delete_otp(phone):
    """Delete otp form Redis"""
    return redis_client.delete(f"otp:{phone}")
