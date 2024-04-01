from rest_framework import serializers

from stats.models import State, Cities, Industry

	
class StateSerializer(serializers.ModelSerializer):

	class Meta:
		model = State
		fields = ['id', 'state']


class CitySerializer(serializers.ModelSerializer):

	class Meta:
		model = Cities
		fields = ['id', 'city']


class IndustrySerializer(serializers.ModelSerializer):

	class Meta:
		model = Industry
		fields = ['id', 'name']