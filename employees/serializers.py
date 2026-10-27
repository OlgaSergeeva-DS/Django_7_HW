from rest_framework import serializers

from .models import EmployeeImage, EmployeeSkill, User


class EmployeeSkillSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(source="skill.name", read_only=True)

    class Meta:
        model = EmployeeSkill
        fields = ["id", "skill_name", "level"]


class EmployeeImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeImage
        fields = ["id", "image", "order"]


class UserSerializer(serializers.ModelSerializer):
    skills = EmployeeSkillSerializer(
        source="employeeskill_set", many=True, read_only=True
    )
    images = EmployeeImageSerializer(many=True, read_only=True)
    experience_days = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "patronymic",
            "gender",
            "hire_date",
            "bio",
            "experience_days",
            "skills",
            "images",
        ]
        read_only_fields = ["id", "experience_days"]
