# quiz_api/admin.py
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Category, Question, Choice
from .resources import CategoryResource, QuestionResource, ChoiceResource, UnifiedQuizResource
from django import forms
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib import messages
from import_export import resources
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.utils import timezone
from datetime import timedelta
import csv
import io

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


class AdvancedBulkQuestionForm(forms.Form):
    """高度な一括質問作成フォーム"""
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        label="カテゴリー",
        help_text="質問を追加するカテゴリーを選択"
    )
    
    FORMAT_CHOICES = [
        ('simple', 'シンプル形式（質問と選択肢を*で区切り）'),
        ('json', 'JSON形式（構造化データ）'),
        ('yaml', 'YAML形式（読みやすい構造）'),
    ]
    
    format_type = forms.ChoiceField(
        choices=FORMAT_CHOICES,
        initial='simple',
        widget=forms.RadioSelect,
        label="入力形式"
    )
    
    questions_data = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 20, 'cols': 80}),
        label="質問データ",
        help_text="""
        選択した形式に応じて質問データを入力してください。
        
        シンプル形式の例:
        2+2は？
        2
        3
        4*
        5
        
        空行で次の質問
        
        JSON形式の例:
        [
          {
            "question": "2+2は？",
            "choices": [
              {"text": "2", "correct": false},
              {"text": "4", "correct": true}
            ]
          }
        ]
        """
    )


class ChoiceInline(admin.TabularInline):
    """選択肢のインライン管理"""
    model = Choice
    extra = 4  # デフォルトで4つの選択肢フォームを表示
    min_num = 2  # 最低2つの選択肢が必要
    max_num = 6  # 最大6つまで
    fields = ['text', 'is_correct']
    
    class Media:
        css = {
            'all': ('admin/css/choice_inline.css',)
        }
        js = ('admin/js/choice_inline.js',)


class QuestionWithChoicesForm(forms.ModelForm):
    """質問と選択肢を同時に編集するフォーム"""
    choice1_text = forms.CharField(max_length=200, required=True, label="選択肢1")
    choice1_correct = forms.BooleanField(required=False, label="正解")
    choice2_text = forms.CharField(max_length=200, required=True, label="選択肢2")
    choice2_correct = forms.BooleanField(required=False, label="正解")
    choice3_text = forms.CharField(max_length=200, required=False, label="選択肢3")
    choice3_correct = forms.BooleanField(required=False, label="正解")
    choice4_text = forms.CharField(max_length=200, required=False, label="選択肢4")
    choice4_correct = forms.BooleanField(required=False, label="正解")
    choice5_text = forms.CharField(max_length=200, required=False, label="選択肢5")
    choice5_correct = forms.BooleanField(required=False, label="正解")
    choice6_text = forms.CharField(max_length=200, required=False, label="選択肢6")
    choice6_correct = forms.BooleanField(required=False, label="正解")
    
    class Meta:
        model = Question
        fields = ['text', 'image']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # 既存の選択肢をフォームに読み込み
            choices = list(self.instance.choices.all())
            for i, choice in enumerate(choices[:6], 1):
                self.fields[f'choice{i}_text'].initial = choice.text
                self.fields[f'choice{i}_correct'].initial = choice.is_correct
    
    def clean(self):
        cleaned_data = super().clean()
        
        # 正解が1つだけ選択されているかチェック
        correct_count = sum(1 for i in range(1, 7) 
                          if cleaned_data.get(f'choice{i}_correct') and cleaned_data.get(f'choice{i}_text'))
        
        if correct_count == 0:
            raise forms.ValidationError("少なくとも1つの正解を選択してください。")
        elif correct_count > 1:
            raise forms.ValidationError("正解は1つだけ選択してください。")
        
        # 最低2つの選択肢が必要
        choice_count = sum(1 for i in range(1, 7) if cleaned_data.get(f'choice{i}_text'))
        if choice_count < 2:
            raise forms.ValidationError("最低2つの選択肢が必要です。")
        
        return cleaned_data
    
    def save(self, commit=True):
        question = super().save(commit)
        
        if commit:
            # 既存の選択肢を削除
            question.choices.all().delete()
            
            # 新しい選択肢を作成
            for i in range(1, 7):
                text = self.cleaned_data.get(f'choice{i}_text')
                if text:
                    Choice.objects.create(
                        question=question,
                        text=text,
                        is_correct=self.cleaned_data.get(f'choice{i}_correct', False)
                    )
        
        return question


class SimpleQuestionInline(admin.TabularInline):
    """シンプルな質問のインライン管理"""
    model = Question
    extra = 1
    fields = ['text', 'image']
    
    class Media:
        css = {
            'all': ('admin/css/choice_inline.css',)
        }


class UnifiedQuizImportForm(forms.Form):
    """統一CSV形式インポート用フォーム"""
    csv_file = forms.FileField(
        label="CSVファイル",
        help_text="カテゴリー,質問,選択肢1,選択肢2,選択肢3,選択肢4,正解番号 の形式のCSVファイル"
    )
    preview_only = forms.BooleanField(
        label="プレビューのみ",
        required=False,
        help_text="チェックすると実際のインポートは行わず、プレビューのみ表示します"
    )


@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin):
    resource_class = CategoryResource
    list_display = ['name', 'question_count']
    search_fields = ['name']
    actions = ['unified_export_selected']
    inlines = [SimpleQuestionInline]  # カテゴリー内で質問を直接編集
    
    def question_count(self, obj):
        """カテゴリーに属する質問数を表示"""
        return obj.questions.count()
    question_count.short_description = '質問数'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('unified-import/', self.admin_site.admin_view(self.unified_import_view), 
                 name='quiz_api_category_unified_import'),
            path('unified-export/', self.admin_site.admin_view(self.unified_export_view), 
                 name='quiz_api_category_unified_export'),
        ]
        return custom_urls + urls
    
    def unified_import_view(self, request):
        """統一CSV形式でのインポート画面"""
        if request.method == 'POST':
            form = UnifiedQuizImportForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = request.FILES['csv_file']
                
                try:
                    # CSVファイルをデコード
                    import io
                    import csv
                    
                    # ファイルを読み込み
                    file_data = csv_file.read()
                    
                    # BOMを除去
                    if file_data.startswith(b'\xef\xbb\xbf'):
                        file_data = file_data[3:]
                    
                    # エンコーディングを試行
                    decoded_data = None
                    encoding_used = None
                    
                    for encoding in ['utf-8-sig', 'utf-8', 'shift_jis', 'cp932', 'iso-2022-jp']:
                        try:
                            decoded_data = file_data.decode(encoding)
                            encoding_used = encoding
                            break
                        except UnicodeDecodeError:
                            continue
                    
                    if decoded_data is None:
                        decoded_data = file_data.decode('utf-8', errors='ignore')
                        encoding_used = 'utf-8 (with errors ignored)'
                    
                    # デバッグ: エンコーディング情報を追加
                    messages.info(request, f"ファイルエンコーディング: {encoding_used}")
                    
                    # 改行コードを統一
                    decoded_data = decoded_data.replace('\r\n', '\n').replace('\r', '\n')
                    
                    # CSVを解析（複数の区切り文字を試行）
                    csv_reader = None
                    delimiter_used = None
                    
                    for delimiter in [',', ';', '\t']:
                        try:
                            test_reader = csv.DictReader(io.StringIO(decoded_data), delimiter=delimiter)
                            test_rows = list(test_reader)
                            if len(test_rows) > 0 and len(test_rows[0]) >= 5:  # 最低5列必要
                                csv_reader = csv.DictReader(io.StringIO(decoded_data), delimiter=delimiter)
                                delimiter_used = delimiter
                                break
                        except:
                            continue
                    
                    if csv_reader is None:
                        csv_reader = csv.DictReader(io.StringIO(decoded_data))
                        delimiter_used = ','
                    
                    messages.info(request, f"CSV区切り文字: '{delimiter_used}'")
                    
                    # UnifiedQuizResourceを使用してインポート
                    resource = UnifiedQuizResource()
                    
                    # データを一旦全て読み込んで重複チェック
                    rows = list(csv_reader)
                    
                    # CSV内での重複質問チェック
                    seen_questions = set()
                    duplicate_warnings = []
                    
                    for row_num, row in enumerate(rows, 1):
                        question_key = f"{row.get('カテゴリー', '').strip()}:{row.get('質問', '').strip()}"
                        if question_key in seen_questions:
                            duplicate_warnings.append(f"行{row_num}: 重複する質問があります - {row.get('質問', '')}")
                        else:
                            seen_questions.add(question_key)
                    
                    # 重複警告を表示
                    if duplicate_warnings:
                        warning_msg = "CSV内で重複する質問が見つかりました:\n" + "\n".join(duplicate_warnings[:5])
                        if len(duplicate_warnings) > 5:
                            warning_msg += f"\n...他{len(duplicate_warnings)-5}件の重複"
                        messages.warning(request, warning_msg)
                    
                    # プレビューモードの場合
                    if form.cleaned_data.get('preview_only'):
                        preview_data = []
                        validation_errors = []
                        
                        for row_num, row in enumerate(rows[:10], 1):  # 最初の10行のみプレビュー
                            try:
                                # バリデーションのみ実行
                                resource.before_import_row(row)
                                preview_data.append({
                                    'row_num': row_num,
                                    'category': row.get('カテゴリー', ''),
                                    'question': row.get('質問', ''),
                                    'choices': [row.get(f'選択肢{i}', '') for i in range(1, 7) if row.get(f'選択肢{i}', '').strip()],
                                    'correct_answer': row.get('正解番号', ''),
                                    'status': 'OK'
                                })
                            except Exception as e:
                                validation_errors.append(f"行{row_num}: {str(e)}")
                                preview_data.append({
                                    'row_num': row_num,
                                    'category': row.get('カテゴリー', ''),
                                    'question': row.get('質問', ''),
                                    'choices': [],
                                    'correct_answer': row.get('正解番号', ''),
                                    'status': f'エラー: {str(e)}'
                                })
                        
                        return render(request, 'admin/quiz_api/category/unified_import.html', {
                            'form': form,
                            'title': '統一CSV形式インポート - プレビュー',
                            'preview_data': preview_data,
                            'total_rows': len(rows),
                            'validation_errors': validation_errors,
                            'duplicate_warnings': duplicate_warnings,
                            'help_text': '''
CSVファイルの形式:
カテゴリー,質問,選択肢1,選択肢2,選択肢3,選択肢4,正解番号

例:
数学,2+2は?,2,3,4,5,3
数学,3×3は?,6,9,12,15,2
英語,appleの意味は?,りんご,みかん,バナナ,ぶどう,1

※選択肢5,選択肢6も使用可能です
※正解番号は1から始まる数字で指定してください
                            '''
                        })
                    
                    # 実際のインポート実行
                    imported_count = 0
                    errors = []
                    
                    # デバッグ: CSVの内容を確認
                    if len(rows) == 0:
                        messages.error(request, "CSVファイルにデータが見つかりませんでした。ヘッダー行のみの可能性があります。")
                        return render(request, 'admin/quiz_api/category/unified_import.html', {
                            'form': form,
                            'title': '統一CSV形式インポート',
                        })
                    
                    # デバッグ情報をメッセージに追加
                    debug_msg = f"CSVファイル解析結果: {len(rows)}行のデータを検出しました"
                    if len(rows) > 0:
                        first_row = rows[0]
                        debug_msg += f"\n最初の行の内容: {dict(first_row)}"
                        debug_msg += f"\nCSVヘッダー: {list(first_row.keys())}"
                    else:
                        # CSVの生データも表示
                        debug_msg += f"\nCSVファイルの内容（最初の500文字）:\n{decoded_data[:500]}"
                    messages.info(request, debug_msg)
                    
                    for row_num, row in enumerate(rows, 1):
                        try:
                            # デバッグ: 各行の処理状況をログ
                            print(f"Processing row {row_num}: {dict(row)}")
                            resource.import_row(row, None)
                            imported_count += 1
                        except Exception as e:
                            error_detail = f"行{row_num}: {str(e)} (データ: {dict(row)})"
                            errors.append(error_detail)
                            print(f"Error in row {row_num}: {e}")
                    
                    if errors:
                        error_msg = "一部のデータでエラーが発生しました:\n" + "\n".join(errors[:5])
                        if len(errors) > 5:
                            error_msg += f"\n...他{len(errors)-5}件のエラー"
                        messages.warning(request, error_msg)
                    
                    success_msg = f"{imported_count}問の問題を正常にインポートしました（総処理行数: {len(rows)}行）"
                    messages.success(request, success_msg)
                    
                    return HttpResponseRedirect('..')
                    
                except Exception as e:
                    messages.error(request, f"CSVファイルの処理中にエラーが発生しました: {str(e)}")
        else:
            form = UnifiedQuizImportForm()
        
        return render(request, 'admin/quiz_api/category/unified_import.html', {
            'form': form,
            'title': '統一CSV形式インポート',
            'help_text': '''
CSVファイルの形式:
カテゴリー,質問,選択肢1,選択肢2,選択肢3,選択肢4,正解番号

例:
数学,2+2は?,2,3,4,5,3
数学,3×3は?,6,9,12,15,2
英語,appleの意味は?,りんご,みかん,バナナ,ぶどう,1

※選択肢5,選択肢6も使用可能です
※正解番号は1から始まる数字で指定してください
            '''
        })
    
    def unified_export_view(self, request):
        """統一CSV形式でのエクスポート"""
        resource = UnifiedQuizResource()
        data = resource.export_data()
        
        # CSVレスポンスを作成
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="unified_quiz_export.csv"'
        
        # BOMを追加してExcelで正しく開けるようにする
        response.write('\ufeff')
        
        writer = csv.writer(response)
        for row in data:
            writer.writerow(row)
        
        return response
    
    def unified_export_selected(self, request, queryset):
        """選択されたカテゴリーの問題を統一CSV形式でエクスポート"""
        from django.db.models import Q
        
        # 選択されたカテゴリーに属する質問を取得
        questions = Question.objects.filter(category__in=queryset).select_related('category').prefetch_related('choices')
        
        resource = UnifiedQuizResource()
        data = resource.export_data(questions)
        
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="selected_categories_export.csv"'
        response.write('\ufeff')
        
        writer = csv.writer(response)
        for row in data:
            writer.writerow(row)
        
        return response
    
    unified_export_selected.short_description = "選択されたカテゴリーを統一CSV形式でエクスポート"

@admin.register(Question)
class QuestionAdmin(ImportExportModelAdmin):
    resource_class = QuestionResource
    list_display = ['text', 'category', 'choice_count', 'has_correct_answer']
    list_filter = ['category']
    search_fields = ['text']
    inlines = [ChoiceInline]  # 質問編集時に選択肢を直接編集
    
    def get_form(self, request, obj=None, **kwargs):
        """フォームを取得（統合フォームか通常フォームかを判断）"""
        if 'unified' in request.GET:
            kwargs['form'] = QuestionWithChoicesForm
        return super().get_form(request, obj, **kwargs)
    
    def choice_count(self, obj):
        """質問に属する選択肢数を表示"""
        return obj.choices.count()
    choice_count.short_description = '選択肢数'
    
    def has_correct_answer(self, obj):
        """正解が設定されているかを表示"""
        return obj.choices.filter(is_correct=True).exists()
    has_correct_answer.short_description = '正解設定'
    has_correct_answer.boolean = True
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('bulk-add/', self.admin_site.admin_view(self.bulk_add_view), name='quiz_api_question_bulk_add'),
            path('advanced-bulk-add/', self.admin_site.admin_view(self.advanced_bulk_add_view), name='quiz_api_question_advanced_bulk_add'),
            path('unified-add/', self.admin_site.admin_view(self.unified_add_view), name='quiz_api_question_unified_add'),
            path('<int:object_id>/unified/', self.admin_site.admin_view(self.unified_change_view), name='quiz_api_question_unified_change'),
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
    
    def advanced_bulk_add_view(self, request):
        """高度な一括追加機能"""
        if request.method == 'POST':
            form = AdvancedBulkQuestionForm(request.POST)
            if form.is_valid():
                category = form.cleaned_data['category']
                format_type = form.cleaned_data['format_type']
                questions_data = form.cleaned_data['questions_data']
                
                try:
                    created_count = 0
                    errors = []
                    
                    if format_type == 'simple':
                        created_count, errors = self._process_simple_format(category, questions_data)
                    elif format_type == 'json':
                        created_count, errors = self._process_json_format(category, questions_data)
                    elif format_type == 'yaml':
                        created_count, errors = self._process_yaml_format(category, questions_data)
                    
                    if errors:
                        error_msg = "一部のデータでエラーが発生しました:\n" + "\n".join(errors[:5])
                        if len(errors) > 5:
                            error_msg += f"\n...他{len(errors)-5}件のエラー"
                        messages.warning(request, error_msg)
                    
                    if created_count > 0:
                        success_msg = f"{created_count}問の問題を正常に追加しました"
                        messages.success(request, success_msg)
                    
                    return redirect('..')
                    
                except Exception as e:
                    messages.error(request, f"データ処理中にエラーが発生しました: {str(e)}")
        else:
            form = AdvancedBulkQuestionForm()
        
        return render(request, 'admin/quiz_api/question/advanced_bulk_add.html', {
            'form': form,
            'title': '高度な問題一括追加'
        })
    
    def _process_simple_format(self, category, data):
        """シンプル形式のデータを処理"""
        question_blocks = [q.strip() for q in data.split('\n\n') if q.strip()]
        created_count = 0
        errors = []
        
        for i, block in enumerate(question_blocks, 1):
            try:
                lines = [line.strip() for line in block.strip().split('\n') if line.strip()]
                if len(lines) < 3:  # 問題文 + 最低2つの選択肢
                    errors.append(f"ブロック{i}: 問題文と最低2つの選択肢が必要です")
                    continue
                
                question_text = lines[0]
                choices_data = lines[1:]
                
                # 正解を特定
                correct_index = -1
                processed_choices = []
                
                for j, choice in enumerate(choices_data):
                    if choice.endswith('*'):
                        if correct_index != -1:
                            errors.append(f"ブロック{i}: 複数の正解が指定されています")
                            break
                        correct_index = j
                        processed_choices.append(choice[:-1].strip())
                    else:
                        processed_choices.append(choice)
                
                if correct_index == -1:
                    errors.append(f"ブロック{i}: 正解が指定されていません（*を付けてください）")
                    continue
                
                # 質問を作成
                question = Question.objects.create(
                    text=question_text,
                    category=category
                )
                
                # 選択肢を作成
                for j, choice_text in enumerate(processed_choices):
                    Choice.objects.create(
                        question=question,
                        text=choice_text,
                        is_correct=(j == correct_index)
                    )
                
                created_count += 1
                
            except Exception as e:
                errors.append(f"ブロック{i}: {str(e)}")
        
        return created_count, errors
    
    def _process_json_format(self, category, data):
        """JSON形式のデータを処理"""
        import json
        
        try:
            questions_list = json.loads(data)
        except json.JSONDecodeError as e:
            return 0, [f"JSON形式エラー: {str(e)}"]
        
        created_count = 0
        errors = []
        
        for i, q_data in enumerate(questions_list, 1):
            try:
                question_text = q_data.get('question', '').strip()
                choices_data = q_data.get('choices', [])
                
                if not question_text:
                    errors.append(f"質問{i}: 問題文が空です")
                    continue
                
                if len(choices_data) < 2:
                    errors.append(f"質問{i}: 最低2つの選択肢が必要です")
                    continue
                
                correct_count = sum(1 for c in choices_data if c.get('correct', False))
                if correct_count != 1:
                    errors.append(f"質問{i}: 正解は1つだけ指定してください")
                    continue
                
                # 質問を作成
                question = Question.objects.create(
                    text=question_text,
                    category=category
                )
                
                # 選択肢を作成
                for choice_data in choices_data:
                    Choice.objects.create(
                        question=question,
                        text=choice_data.get('text', ''),
                        is_correct=choice_data.get('correct', False)
                    )
                
                created_count += 1
                
            except Exception as e:
                errors.append(f"質問{i}: {str(e)}")
        
        return created_count, errors
    
    def _process_yaml_format(self, category, data):
        """YAML形式のデータを処理"""
        try:
            import yaml
        except ImportError:
            return 0, ["YAMLライブラリがインストールされていません"]
        
        try:
            questions_list = yaml.safe_load(data)
        except yaml.YAMLError as e:
            return 0, [f"YAML形式エラー: {str(e)}"]
        
        # JSON形式と同じ処理ロジックを使用
        import json
        return self._process_json_format(category, json.dumps(questions_list))
    
    def unified_add_view(self, request):
        """統合フォームで新規作成"""
        if request.method == 'POST':
            form = QuestionWithChoicesForm(request.POST)
            if form.is_valid():
                question = form.save()
                messages.success(request, f'質問「{question.text}」を作成しました')
                return redirect('/quiz-admin/quiz_api/question/')
        else:
            form = QuestionWithChoicesForm()
        
        return render(request, 'admin/quiz_api/question/unified_form.html', {
            'form': form,
            'title': '統合フォームで質問作成',
            'is_popup': False,
            'save_as': False,
            'has_delete_permission': False,
            'has_change_permission': True,
        })
    
    def unified_change_view(self, request, object_id):
        """統合フォームで編集"""
        question = Question.objects.get(pk=object_id)
        
        if request.method == 'POST':
            form = QuestionWithChoicesForm(request.POST, instance=question)
            if form.is_valid():
                question = form.save()
                messages.success(request, f'質問「{question.text}」を更新しました')
                return redirect('/quiz-admin/quiz_api/question/')
        else:
            form = QuestionWithChoicesForm(instance=question)
        
        return render(request, 'admin/quiz_api/question/unified_form.html', {
            'form': form,
            'title': f'統合フォームで質問編集: {question.text}',
            'object_id': object_id,
            'original': question,
            'is_popup': False,
            'save_as': False,
            'has_delete_permission': True,
            'has_change_permission': True,
        })
    
    actions = ['export_as_csv']

@admin.register(Choice)
class ChoiceAdmin(ImportExportModelAdmin):
    resource_class = ChoiceResource
    list_display = ['text', 'question', 'question_category', 'is_correct']
    list_filter = ['is_correct', 'question__category']
    search_fields = ['text', 'question__text']
    list_select_related = ['question__category']  # パフォーマンス最適化
    
    def question_category(self, obj):
        """質問のカテゴリーを表示"""
        return obj.question.category.name
    question_category.short_description = 'カテゴリー'
    question_category.admin_order_field = 'question__category__name'


class QuizAdminSite(admin.AdminSite):
    """カスタム管理サイト"""
    site_header = "クイズ管理システム"
    site_title = "クイズ管理"
    index_title = "クイズ管理ダッシュボード"
    
    def index(self, request, extra_context=None):
        """管理画面トップページのカスタマイズ"""
        from .models import QuizAttempt
        
        extra_context = extra_context or {}
        
        # 統計データ
        extra_context.update({
            'category_count': Category.objects.count(),
            'question_count': Question.objects.count(),
            'choice_count': Choice.objects.count(),
            'quiz_attempts': QuizAttempt.objects.count(),
        })
        
        # 最近の活動（過去7日間）
        week_ago = timezone.now() - timedelta(days=7)
        recent_questions = Question.objects.filter(id__gte=1).order_by('-id')[:5]
        recent_categories = Category.objects.filter(id__gte=1).order_by('-id')[:3]
        
        activities = []
        
        # 最近作成された質問
        for q in recent_questions:
            activities.append({
                'icon': '❓',
                'title': f'質問「{q.text[:30]}...」が作成されました',
                'time': timezone.now() - timedelta(hours=1),  # 仮の時間
            })
        
        # 最近作成されたカテゴリー
        for c in recent_categories:
            activities.append({
                'icon': '📁',
                'title': f'カテゴリー「{c.name}」が作成されました',
                'time': timezone.now() - timedelta(hours=2),  # 仮の時間
            })
        
        # 時間順でソート
        activities.sort(key=lambda x: x['time'], reverse=True)
        extra_context['recent_activities'] = activities[:10]
        
        return super().index(request, extra_context)
    
    def get_urls(self):
        """カスタムURLを追加"""
        from django.urls import path
        
        urls = super().get_urls()
        custom_urls = [
            path('quiz-stats-api/', self.admin_view(self.stats_api), name='quiz_api_stats_api'),
        ]
        return custom_urls + urls
    
    def stats_api(self, request):
        """統計データAPI"""
        from .models import QuizAttempt
        
        data = {
            'categories': Category.objects.count(),
            'questions': Question.objects.count(),
            'choices': Choice.objects.count(),
            'attempts': QuizAttempt.objects.count(),
        }
        return JsonResponse(data)


# カスタム管理サイトを使用
quiz_admin_site = QuizAdminSite(name='quiz_admin')

# モデルを再登録
quiz_admin_site.register(Category, CategoryAdmin)
quiz_admin_site.register(Question, QuestionAdmin)
quiz_admin_site.register(Choice, ChoiceAdmin)

# デフォルト管理画面の設定もカスタマイズ
admin.site.site_header = "クイズ管理システム"
admin.site.site_title = "クイズ管理"
admin.site.index_title = "クイズ管理ダッシュボード"

# デフォルト管理画面にカスタム統計情報を追加するためのContext Processor
def admin_context_processor(request):
    """管理画面用のコンテキストプロセッサ"""
    if not request.path.startswith('/admin/'):
        return {}
    
    from .models import QuizAttempt
    
    return {
        'category_count': Category.objects.count(),
        'question_count': Question.objects.count(), 
        'choice_count': Choice.objects.count(),
        'quiz_attempts': QuizAttempt.objects.count(),
    }
