import redis
import tempfile
import random
from decouple import config
from config import settings
from PIL import Image
from kavenegar import KavenegarAPI, APIException, HTTPException


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


def send_sms_verification_code(code: str, phone_number: str):
    try:
        api = KavenegarAPI(config('KAVENEGAR_API'))
        params = {
            'sender': config('KAVENEGAR_SENDER'),
            'receptor': phone_number,
            'message': f'Your code is: {code}'
            }
        response = api.sms_send(params)
        print(response)
    except APIException as e:
        print(f"APIException: {e}")
    except HTTPException as e:
        print(f"HTTPException: {e}")


class HitLimitMixin:

    def hit_limit(self, method_name, time, max_hit):
        """Define times a user can hit an endpoint within a specific time"""
        print(method_name)
        current_count = redis_client.get(name=f"{method_name}-count")
        if current_count is None:
            current_count = 0
        current_count = int(current_count) + 1
        redis_client.setex(
            name=f"{method_name}-count", time=time, value=current_count)
        print(current_count, max_hit)
        return current_count > max_hit

