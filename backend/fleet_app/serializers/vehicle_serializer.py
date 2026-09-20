from rest_framework import serializers


class VehicleSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    plateNo = serializers.CharField(source='plate_no')
    type = serializers.CharField(source='vehicle_type')
    brandModel = serializers.CharField(source='brand_model')
    purchaseDate = serializers.DateField(source='purchase_date')
    insuranceExpireDate = serializers.DateField(source='insurance_expire_date')
    inspectionExpireDate = serializers.DateField(source='inspection_expire_date')
    status = serializers.CharField()
    mileage = serializers.IntegerField()
    tankCapacity = serializers.FloatField(source='tank_capacity')
    fuelConsumption = serializers.FloatField(source='fuel_consumption')
    loadCapacity = serializers.FloatField(source='load_capacity')
