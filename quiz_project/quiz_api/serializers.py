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
    user = UserSerializer()  # ユーザー情報を明示的に含める
    category_name = serializers.CharField(source='category.name', read_only=True)
    created_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%SZ')  # ISO形式を明示
    
    class Meta:
        model = QuizAttempt
        fields = ['id', 'user', 'category', 'category_name', 'score', 'total_questions', 'percentage', 'created_at']

class ResponseSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    selected_choice_id = serializers.IntegerField()
    is_correct = serializers.BooleanField()

class SaveQuizResultSerializer(serializers.Serializer):
    category_id = serializers.IntegerField()
    score = serializers.IntegerField()
    total_questions = serializers.IntegerField()
    responses = ResponseSerializer(many=True)  # ResponseSerializerのリスト
    
    def create(self, validated_data):
        user = self.context['request'].user
        responses_data = validated_data.pop('responses')
        
        # スコアと質問数
        score = validated_data['score']
        total_questions = validated_data['total_questions']
        
        # パーセンテージを計算
        percentage = (score / total_questions * 100) if total_questions > 0 else 0
        
        # QuizAttemptの作成（percentageフィールドを含める）
        quiz_attempt = QuizAttempt.objects.create(
            user=user,
            category_id=validated_data['category_id'],
            score=score,
            total_questions=total_questions,
            percentage=percentage  # この行を追加
        )
        
        # 各回答の保存処理（オプション）
        for response_data in responses_data:
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
    """リーダーボード用のユーザー集計データシリアライザー"""
    total_attempts = serializers.IntegerField(read_only=True)
    total_score = serializers.IntegerField(read_only=True)
    total_questions = serializers.IntegerField(read_only=True)
    avg_percentage = serializers.FloatField(read_only=True)
    
    # カテゴリ別フィールドはオプショナル
    category_attempts = serializers.IntegerField(read_only=True, required=False)
    category_score = serializers.IntegerField(read_only=True, required=False)
    category_questions = serializers.IntegerField(read_only=True, required=False)
    category_percentage = serializers.FloatField(read_only=True, required=False)
    
    class Meta:
        model = User
        # 必要最小限のフィールドだけを含める
        fields = [
            'id', 'username', 
            'total_attempts', 'total_score', 'total_questions', 'avg_percentage',
            'category_attempts', 'category_score', 'category_questions', 'category_percentage'
        ]

#ユーザープロフィールとパフォーマンス統計
# quiz_api/serializers.py に追加
class UserStatsSerializer(serializers.Serializer):
    total_attempts = serializers.IntegerField()
    total_categories_played = serializers.IntegerField()
    best_category = serializers.CharField(allow_null=True)
    avg_percentage = serializers.FloatField()
    category_stats = serializers.ListField(child=serializers.DictField())