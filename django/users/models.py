from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from users.utils import generate_random_nickname

class UserManager(BaseUserManager):
    use_in_migrations = True    
    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError('이메일 주소는 필수 입력 사항입니다.')                
        user = self.model(email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **kwargs):
        user = self.create_user(email=email, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
    
class User(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=255, unique=True)
    nickname = models.CharField(max_length=255, verbose_name='닉네임', unique=True, default=generate_random_nickname())    
    is_staff = models.BooleanField(default=False, verbose_name='운영진')
    is_down = models.BooleanField(default=False, verbose_name='휴면회원')
    is_active = models.BooleanField(default=True, verbose_name='활동회원')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='가입일자')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일자')

    objects = UserManager()

    username = None
    USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = ['nickname']

    LOGIN_KAKAO = 'kakao'

    login_method = models.CharField(max_length=20, default=LOGIN_KAKAO)

    def is_staff_member(self):
        # 사용자가 운영진인지 확인한다.
        return self.is_staff
    
    def save(self, *args, **kwargs):
        one_year_ago = timezone.now() - timezone.timedelta(days=365)
        if self.last_login and self.last_login < one_year_ago:
            self.is_down = True
            self.is_active = False

        super(User, self).save(*args, **kwargs)
    
    class Meta:
        db_table = 'Users'