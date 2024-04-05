from rest_framework import serializers
from .models import User, LicenseCertification


class LicenseCertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LicenseCertification
        fields = ['id', 'user', 'name', 'issuing_organization', 'issue_date', 'expiration_date', 'credential_id',
                  'credential_url', 'created_at', 'updated_at']


class UserCertificationSerializer(serializers.ModelSerializer):
    candidate_license = LicenseCertificationSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email_id', 'phone_number', 'is_candidate_user', 'candidate_license', ]
