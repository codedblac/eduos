from rest_framework import serializers
from .models import SystemModule, ModulePermission, SchoolModule, Plan
from django.contrib.auth import get_user_model

User = get_user_model()


# -----------------------------------------------
# 1. ModulePermission Serializer
# -----------------------------------------------
class ModulePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModulePermission
        fields = ('id', 'name', 'codename', 'module')


# -----------------------------------------------
# 2. SystemModule Serializer
# -----------------------------------------------
class SystemModuleSerializer(serializers.ModelSerializer):
    permissions = ModulePermissionSerializer(many=True, read_only=True)

    class Meta:
        model = SystemModule
        fields = (
            'id',
            'name',
            'app_label',
            'description',
            'linked_group',
            'permissions',
            'is_default',
        )


# -----------------------------------------------
# 3. Plan Serializer
# -----------------------------------------------
class PlanSerializer(serializers.ModelSerializer):
    modules = SystemModuleSerializer(many=True, read_only=True)
    module_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=SystemModule.objects.all(), write_only=True, source='modules'
    )

    class Meta:
        model = Plan
        fields = ('id', 'name', 'description', 'is_custom', 'modules', 'module_ids')

    def create(self, validated_data):
        modules = validated_data.pop('modules', [])
        plan = Plan.objects.create(**validated_data)
        plan.modules.set(modules)
        return plan

    def update(self, instance, validated_data):
        modules = validated_data.pop('modules', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if modules is not None:
            instance.modules.set(modules)
        instance.save()
        return instance


# -----------------------------------------------
# 4. SchoolModule Serializer
# -----------------------------------------------
class SchoolModuleSerializer(serializers.ModelSerializer):
    module = SystemModuleSerializer(read_only=True)
    module_id = serializers.PrimaryKeyRelatedField(
        queryset=SystemModule.objects.all(), write_only=True, source='module'
    )

    class Meta:
        model = SchoolModule
        fields = ('id', 'institution', 'module', 'module_id', 'custom')


# -----------------------------------------------
# 5. User Module Access Serializer
# -----------------------------------------------
class UserModuleAccessSerializer(serializers.Serializer):
    """
    Returns all modules available to a user.
    Merges institution modules and user modules.
    """
    user_id = serializers.IntegerField()
    modules = serializers.SerializerMethodField()

    def get_modules(self, obj):
        user = User.objects.get(id=obj['user_id'])

        # Modules assigned via institution
        inst_modules = []
        if hasattr(user, 'institution') and user.institution:
            inst_modules = user.institution.allowed_modules.select_related('module').all()

        # Modules assigned directly to user
        user_modules = user.modules.all()

        # Merge both sets uniquely
        all_modules = set([sm.module for sm in inst_modules]) | set(user_modules)

        return SystemModuleSerializer(list(all_modules), many=True).data


# -----------------------------------------------
# 6. Assign Modules to Institution Serializer
# -----------------------------------------------
class AssignModulesSerializer(serializers.Serializer):
    """
    Assign modules to an institution.
    Can assign via plan or custom module IDs.
    """
    institution_id = serializers.UUIDField()
    module_ids = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=True, required=False
    )
    plan_id = serializers.IntegerField(required=False)

    def validate(self, data):
        from institutions.models import Institution

        # Validate institution
        try:
            data['institution'] = Institution.objects.get(id=data['institution_id'])
        except Institution.DoesNotExist:
            raise serializers.ValidationError("Institution does not exist.")

        # Validate plan if provided
        if 'plan_id' in data:
            try:
                data['plan'] = Plan.objects.get(id=data['plan_id'])
            except Plan.DoesNotExist:
                raise serializers.ValidationError("Plan does not exist.")
        else:
            data['plan'] = None

        # Validate modules if provided
        module_ids = data.get('module_ids', [])
        if module_ids:
            modules = SystemModule.objects.filter(id__in=module_ids)
            if not modules.exists():
                raise serializers.ValidationError("No valid modules found for provided IDs.")
            data['modules'] = modules
        else:
            data['modules'] = []

        return data

    def create(self, validated_data):
        inst = validated_data['institution']
        modules = []

        # Assign modules from plan if provided
        plan = validated_data.get('plan')
        if plan:
            modules = list(plan.modules.all())

        # Assign modules from explicit module_ids if provided (for custom plan)
        if validated_data.get('modules'):
            modules += list(validated_data['modules'])

        assigned = []
        for module in modules:
            sm, created = SchoolModule.objects.get_or_create(institution=inst, module=module)
            if created:
                sm.custom = True
                sm.save()
            assigned.append(sm)
        return assigned
