from rest_framework import serializers


class DriverSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    phone = serializers.CharField()
    licenseType = serializers.CharField(source='license_type')
    licenseExpireDate = serializers.DateField(source='license_expire_date')
    hireDate = serializers.DateField(source='hire_date')
    status = serializers.CharField()
    drivingHours = serializers.IntegerField(source='driving_hours')
    violationCount = serializers.IntegerField(source='violation_count')
