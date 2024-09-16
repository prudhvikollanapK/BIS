from rest_framework import serializers
from .models import BlockedDomain

class BlockedDomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockedDomain
        fields = ['id', 'domain', 'description', 'user', 'added_on']
        read_only_fields = ['id', 'user', 'added_on']
