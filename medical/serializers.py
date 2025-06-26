from rest_framework import serializers
from .models import (
    MedicineInventory,
    MedicalVisit,
    DispensedMedicine,
    HealthAlert,
    ClassHealthTrend,
)
from students.models import Student


class MedicineInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicineInventory
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class DispensedMedicineSerializer(serializers.ModelSerializer):
    medicine_name = serializers.CharField(source='medicine.name', read_only=True)

    class Meta:
        model = DispensedMedicine
        fields = ['id', 'medicine', 'medicine_name', 'quantity_dispensed', 'notes']


class MedicalVisitSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.__str__', read_only=True)
    attended_by_name = serializers.CharField(source='attended_by.get_full_name', read_only=True)
    medicines_dispensed = DispensedMedicineSerializer(many=True, required=False)

    class Meta:
        model = MedicalVisit
        fields = [
            'id', 'student', 'student_name', 'attended_by', 'attended_by_name',
            'date_visited', 'symptoms', 'diagnosis', 'treatment',
            'is_emergency', 'referred', 'referral_notes', 'notes',
            'medicines_dispensed',
        ]
        read_only_fields = ['id', 'date_visited', 'attended_by']

    def create(self, validated_data):
        medicines_data = self.initial_data.get('medicines_dispensed', [])
        validated_data['attended_by'] = self.context['request'].user
        visit = MedicalVisit.objects.create(**validated_data)

        for med in medicines_data:
            medicine = MedicineInventory.objects.get(id=med['medicine'])
            quantity = med['quantity_dispensed']

            # Update inventory quantity
            if medicine.quantity < quantity:
                raise serializers.ValidationError(f"Not enough stock for {medicine.name}.")
            medicine.quantity -= quantity
            medicine.save()

            DispensedMedicine.objects.create(
                visit=visit,
                medicine=medicine,
                quantity_dispensed=quantity,
                notes=med.get('notes', '')
            )

        return visit


class HealthAlertSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.__str__', read_only=True)

    class Meta:
        model = HealthAlert
        fields = ['id', 'student', 'student_name', 'triggered_by_ai', 'alert_type', 'message', 'date_created', 'resolved']
        read_only_fields = ['id', 'date_created', 'triggered_by_ai']


class ClassHealthTrendSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassHealthTrend
        fields = ['id', 'institution', 'class_level', 'stream_name', 'most_common_illness', 'trend_notes', 'generated_on']
        read_only_fields = ['id', 'generated_on']
