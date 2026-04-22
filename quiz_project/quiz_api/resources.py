# quiz_api/resources.py
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import Category, Question, Choice
from django.db import transaction

class CategoryResource(resources.ModelResource):
    class Meta:
        model = Category
        import_id_fields = ['id']
        fields = ['id', 'name']
        export_order = fields

class QuestionResource(resources.ModelResource):
    # カテゴリーを名前で参照できるようにする
    category = fields.Field(
        column_name='category',
        attribute='category',
        widget=ForeignKeyWidget(Category, 'name')
    )
    
    class Meta:
        model = Question
        import_id_fields = ['id']
        fields = ['id', 'text', 'category']
        export_order = fields

class ChoiceResource(resources.ModelResource):
    # 質問を参照できるようにする
    question = fields.Field(
        column_name='question',
        attribute='question',
        widget=ForeignKeyWidget(Question, 'text')
    )
    
    class Meta:
        model = Choice
        import_id_fields = ['id']
        fields = ['id', 'question', 'text', 'is_correct']
        export_order = fields


class UnifiedQuizResource(resources.ModelResource):
    """統一CSV形式でカテゴリー、質問、選択肢を一括インポートするリソース"""
    
    # CSV列の定義
    category = fields.Field(column_name='カテゴリー')
    question_text = fields.Field(column_name='質問')
    choice1 = fields.Field(column_name='選択肢1')
    choice2 = fields.Field(column_name='選択肢2')
    choice3 = fields.Field(column_name='選択肢3')
    choice4 = fields.Field(column_name='選択肢4')
    choice5 = fields.Field(column_name='選択肢5', default='')
    choice6 = fields.Field(column_name='選択肢6', default='')
    correct_answer = fields.Field(column_name='正解番号')
    
    class Meta:
        model = Question  # 主となるモデル
        skip_unchanged = True
        report_skipped = False
        import_id_fields = []
    
    def before_import_row(self, row, **kwargs):
        """インポート前の行データ処理"""
        # 空の選択肢を除去
        choices = []
        for i in range(1, 7):
            choice_key = f'選択肢{i}'
            if choice_key in row and row[choice_key].strip():
                choices.append(row[choice_key].strip())
        
        # 正解番号のバリデーション
        try:
            correct_num = int(row['正解番号'])
            if correct_num < 1 or correct_num > len(choices):
                raise ValueError(f"正解番号が無効です: {correct_num}")
        except (ValueError, KeyError):
            raise ValueError("正解番号は1以上の数字で入力してください")
        
        return row
    
    def import_row(self, row, instance_loader, **kwargs):
        """行データのインポート処理"""
        with transaction.atomic():
            # カテゴリーの作成または取得
            category_name = row['カテゴリー'].strip()
            category, created = Category.objects.get_or_create(name=category_name)
            
            # 質問の作成
            question_text = row['質問'].strip()
            question, created = Question.objects.get_or_create(
                text=question_text,
                category=category
            )
            
            # 既存の選択肢を削除（重複インポート対策）
            if not created:
                question.choices.all().delete()
            
            # 選択肢の作成
            choices = []
            for i in range(1, 7):
                choice_key = f'選択肢{i}'
                if choice_key in row and row[choice_key].strip():
                    choices.append(row[choice_key].strip())
            
            correct_num = int(row['正解番号'])
            
            for i, choice_text in enumerate(choices, 1):
                Choice.objects.create(
                    question=question,
                    text=choice_text,
                    is_correct=(i == correct_num)
                )
        
        # 成功したインポートの結果を返す
        return question
    
    def export_data(self, queryset=None):
        """統一CSV形式でエクスポート"""
        if queryset is None:
            # 全ての質問を取得
            questions = Question.objects.all().select_related('category').prefetch_related('choices')
        else:
            questions = queryset.select_related('category').prefetch_related('choices')
        
        # CSV用のデータを準備
        data = []
        headers = ['カテゴリー', '質問', '選択肢1', '選択肢2', '選択肢3', '選択肢4', '選択肢5', '選択肢6', '正解番号']
        
        # ヘッダーを追加
        data.append(headers)
        
        for question in questions:
            choices = list(question.choices.all())
            if not choices:
                continue
                
            row = [question.category.name, question.text]
            
            # 選択肢を追加（最大6個）
            for i in range(6):
                if i < len(choices):
                    row.append(choices[i].text)
                else:
                    row.append('')
            
            # 正解番号を見つける
            correct_answer = 1
            for i, choice in enumerate(choices, 1):
                if choice.is_correct:
                    correct_answer = i
                    break
            
            row.append(str(correct_answer))
            data.append(row)
        
        return data