# quiz_api/serializers.py
from rest_framework import serializers
from .models import Category, Question, Choice, QuizAttempt, QuestionResponse
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text', 'is_correct']

class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'text', 'choices']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']
        
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "パスワードが一致しません"})
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
# 過去のクイズ結果の保存
class QuestionResponseSerializer(serializers.ModelSerializer):
    question_text = serializers.SerializerMethodField()
    selected_choice_text = serializers.SerializerMethodField()
    
    class Meta:
        model = QuestionResponse
        fields = ['id', 'question_text', 'selected_choice_text', 'is_correct']
    
    def get_question_text(self, obj):
        return obj.question.text
    
    def get_selected_choice_text(self, obj):
        return obj.selected_choice.text

class QuizAttemptSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()
    responses = QuestionResponseSerializer(many=True, read_only=True)
    
    class Meta:
        model = QuizAttempt
        fields = ['id', 'category_name', 'score', 'total_questions', 'percentage', 'created_at', 'responses']
    
    def get_category_name(self, obj):
        return obj.category.name

class SaveQuizResultSerializer(serializers.Serializer):
    category_id = serializers.IntegerField()
    score = serializers.IntegerField()
    total_questions = serializers.IntegerField()
    responses = serializers.ListField(
        child=serializers.DictField(
            child=serializers.Field()
        )
    )
    
    def create(self, validated_data):
        user = self.context['request'].user
        category_id = validated_data['category_id']
        score = validated_data['score']
        total_questions = validated_data['total_questions']
        responses = validated_data['responses']
        
        # クイズ結果の保存
        percentage = (score / total_questions) * 100 if total_questions > 0 else 0
        quiz_attempt = QuizAttempt.objects.create(
            user=user,
            category_id=category_id,
            score=score,
            total_questions=total_questions,
            percentage=percentage
        )
        
        # 質問ごとの回答を保存
        for response_data in responses:
            QuestionResponse.objects.create(
                quiz_attempt=quiz_attempt,
                question_id=response_data['question_id'],
                selected_choice_id=response_data['selected_choice_id'],
                is_correct=response_data['is_correct']
            )
        
        return quiz_attempt
# リーダーボード
# quiz_api/serializers.py に追加
class UserLeaderboardSerializer(serializers.ModelSerializer):
    total_attempts = serializers.IntegerField(read_only=True)
    total_score = serializers.IntegerField(read_only=True)
    total_questions = serializers.IntegerField(read_only=True)
    avg_percentage = serializers.FloatField(read_only=True)
    category_attempts = serializers.IntegerField(read_only=True, required=False)
    category_score = serializers.IntegerField(read_only=True, required=False)
    category_questions = serializers.IntegerField(read_only=True, required=False)
    category_percentage = serializers.FloatField(read_only=True, required=False)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'total_attempts', 'total_score', 'total_questions', 
            'avg_percentage', 'category_attempts', 'category_score', 
            'category_questions', 'category_percentage'
        ]
#ユーザープロフィールとパフォーマンス統計
# quiz_api/serializers.py に追加
class UserStatsSerializer(serializers.Serializer):
    total_attempts = serializers.IntegerField()
    total_categories_played = serializers.IntegerField()
    best_category = serializers.CharField(allow_null=True)
    avg_percentage = serializers.FloatField()
    category_stats = serializers.ListField(child=serializers.DictField())