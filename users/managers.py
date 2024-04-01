import random
from django.contrib.auth.models import BaseUserManager
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import authenticate


class UserManager(BaseUserManager):

    def create_user(self, **kwargs):
        """
        Creates and saves a User with the given email and password.
        """
        first_name = kwargs.get('first_name', '')
        last_name = kwargs.get('last_name', ' ')
        email_id = kwargs.get('email_id')
        password = kwargs.get('password', '')
        phone_number = kwargs.get('phone_number')
        is_candidate_user = kwargs.get('is_candidate_user', False)
        is_company_user = kwargs.get('is_company_user', False)
        
        if not email_id:
            raise ValueError('Users must have an email address')

        user = self.model(
            email_id=self.normalize_email(email_id),
        )

        user.set_password(password)
        user.first_name = first_name
        user.last_name = last_name
        user.email_id = email_id
        user.phone_number = phone_number
        user.is_candidate_user = is_candidate_user
        user.is_company_user = is_company_user
        user.is_active = kwargs.get('is_active', False)
        
        user.save()

        return user

    def create_superuser(self, email_id, password=None):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email_id=email_id,
            password=password,
        )
        user.is_admin = True
        user.is_active = True
        user.save()
        
        return user

    def get_user_model():
        pass