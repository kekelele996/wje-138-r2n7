from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Vehicle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plate_no', models.CharField(max_length=32)),
                ('vehicle_type', models.CharField(max_length=32)),
                ('brand_model', models.CharField(max_length=80)),
                ('purchase_date', models.DateField(null=True)),
                ('insurance_expire_date', models.DateField(null=True)),
                ('inspection_expire_date', models.DateField(null=True)),
                ('status', models.CharField(max_length=24)),
                ('mileage', models.IntegerField(default=0)),
                ('tank_capacity', models.FloatField(default=0)),
                ('fuel_consumption', models.FloatField(default=0)),
                ('load_capacity', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Driver',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
                ('phone', models.CharField(max_length=32)),
                ('license_type', models.CharField(max_length=8)),
                ('license_expire_date', models.DateField(null=True)),
                ('hire_date', models.DateField(null=True)),
                ('status', models.CharField(max_length=24)),
                ('driving_hours', models.IntegerField(default=0)),
                ('violation_count', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='DispatchOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_no', models.CharField(max_length=40, unique=True)),
                ('origin', models.CharField(max_length=120)),
                ('destination', models.CharField(max_length=120)),
                ('plan_depart_at', models.DateTimeField(blank=True, null=True)),
                ('plan_arrive_at', models.DateTimeField(blank=True, null=True)),
                ('actual_depart_at', models.DateTimeField(blank=True, null=True)),
                ('actual_arrive_at', models.DateTimeField(blank=True, null=True)),
                ('cargo', models.CharField(max_length=160)),
                ('weight', models.FloatField(default=0)),
                ('freight', models.FloatField(default=0)),
                ('status', models.CharField(default='Assigned', max_length=24)),
                ('creator_id', models.IntegerField(default=1)),
                ('note', models.TextField(blank=True, default='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('assigned_at', models.DateTimeField(blank=True, null=True)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('cancelled_at', models.DateTimeField(blank=True, null=True)),
                ('driver', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='fleet_app.driver')),
                ('vehicle', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='fleet_app.vehicle')),
            ],
        ),
        migrations.CreateModel(
            name='DispatchStatusEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_status', models.CharField(blank=True, default='', max_length=24)),
                ('to_status', models.CharField(max_length=24)),
                ('remark', models.CharField(blank=True, default='', max_length=200)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to='fleet_app.dispatchorder')),
            ],
            options={'ordering': ['id']},
        ),
        migrations.CreateModel(
            name='MaintenanceRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('maintenance_type', models.CharField(max_length=24)),
                ('items', models.JSONField(default=list)),
                ('cost', models.FloatField(default=0)),
                ('vendor', models.CharField(max_length=120)),
                ('date', models.DateField(null=True)),
                ('next_mileage', models.IntegerField(default=0)),
                ('next_date', models.DateField(null=True)),
                ('status', models.CharField(max_length=24)),
                ('vehicle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fleet_app.vehicle')),
            ],
        ),
        migrations.CreateModel(
            name='FuelRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(null=True)),
                ('liters', models.FloatField(default=0)),
                ('unit_price', models.FloatField(default=0)),
                ('total_amount', models.FloatField(default=0)),
                ('mileage', models.IntegerField(default=0)),
                ('station', models.CharField(max_length=120)),
                ('payment_method', models.CharField(max_length=24)),
                ('vehicle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fleet_app.vehicle')),
            ],
        ),
    ]
