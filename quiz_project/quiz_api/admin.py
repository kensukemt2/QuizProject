# quiz_api/admin.py
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Category, Question, Choice
from .resources import CategoryResource, QuestionResource, ChoiceResource
from django import forms
from django.shortcuts import render, redirect
from django.urls import path

class BulkQuestionForm(forms.Form):
    category = forms.ModelChoiceField(queryset=Category.objects.all())
    questions_data = forms.CharField(widget=forms.Textarea, help_text="""
    各問題を次の形式で入力してください:
    問題文
    選択肢1*（*は正解を示す）
    選択肢2
    選択肢3
    選択肢4

    空行で問題を区切ります。
    """)

@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin):
    resource_class = CategoryResource
    list_display = ['name']
    search_fields = ['name']

@admin.register(Question)
class QuestionAdmin(ImportExportModelAdmin):
    resource_class = QuestionResource
    list_display = ['text', 'category']
    list_filter = ['category']
    search_fields = ['text']
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('bulk-add/', self.admin_site.admin_view(self.bulk_add_view), name='quiz_api_question_bulk_add'),
        ]
        return custom_urls + urls
    
    def bulk_add_view(self, request):
        if request.method == 'POST':
            form = BulkQuestionForm(request.POST)
            if form.is_valid():
                category = form.cleaned_data['category']
                questions_data = form.cleaned_data['questions_data']
                
                # 問題ごとに分割
                question_blocks = [q.strip() for q in questions_data.split('\n\n') if q.strip()]
                
                for block in question_blocks:
                    lines = block.strip().split('\n')
                    if len(lines) >= 5:  # 問題文 + 少なくとも4つの選択肢
                        question_text = lines[0].strip()
                        # 問題を作成
                        question = Question.objects.create(
                            text=question_text,
                            category=category
                        )
                        
                        # 選択肢を追加
                        for i in range(1, min(5, len(lines))):
                            choice_text = lines[i].strip()
                            is_correct = False
                            if choice_text.endswith('*'):
                                choice_text = choice_text[:-1].strip()
                                is_correct = True
                            
                            Choice.objects.create(
                                question=question,
                                text=choice_text,
                                is_correct=is_correct
                            )
                
                self.message_user(request, f"{len(question_blocks)}問の問題を追加しました")
                return redirect('..')
        else:
            form = BulkQuestionForm()
        
        return render(request, 'admin/quiz_api/question/bulk_add.html', {
            'form': form,
            'title': '問題の一括追加'
        })
    
    actions = ['export_as_csv']

@admin.register(Choice)
class ChoiceAdmin(ImportExportModelAdmin):
    resource_class = ChoiceResource
    list_display = ['text', 'question', 'is_correct']
    list_filter = ['is_correct', 'question__category']
    search_fields = ['text', 'question__text']
