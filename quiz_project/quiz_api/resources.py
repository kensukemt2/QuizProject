# quiz_api/resources.py
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import Category, Question, Choice

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