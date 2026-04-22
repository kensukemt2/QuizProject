# 画像アップロード機能ガイド

## テスト結果概要

✅ **画像アップロード機能は正常に動作しています**

### 検証結果
- ✓ Pillow (PIL) インストール済み (v11.2.1)
- ✓ メディアディレクトリ設定正常
- ✓ 画像保存ディレクトリ存在確認
- ✓ 画像アップロード・保存機能動作確認済み
- ✓ 画像URL生成機能動作確認済み

### 現在の設定

```python
# settings.py
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# models.py
class Question(models.Model):
    image = models.ImageField(upload_to='question_images/', blank=True, null=True)
```

### 保存先
- **ディレクトリ**: `/home/kensukemt2/django/quiz_project/media/question_images/`
- **URL**: `http://localhost:8000/media/question_images/[ファイル名]`

## 管理画面での画像アップロード手順

### 方法1: Django管理画面から

1. **管理画面にアクセス**
   ```
   http://localhost:8000/admin/
   ```

2. **Question (質問) セクションに移動**
   - 左メニューから「Quiz api」→「Questions」をクリック

3. **新規質問の作成 または 既存質問の編集**
   - 新規作成: 右上の「ADD QUESTION +」ボタンをクリック
   - 編集: 既存の質問をクリック

4. **画像フィールドにファイルをアップロード**
   - 「Image」フィールドの「Choose File」ボタンをクリック
   - アップロードしたい画像ファイルを選択
   - 対応形式: JPG, PNG, GIF など

5. **保存**
   - 画面下部の「SAVE」ボタンをクリック

### 方法2: カスタム管理画面から

1. **カスタム管理画面にアクセス**
   ```
   http://localhost:8000/quiz-admin/
   ```

2. 上記と同じ手順で画像をアップロード

## API経由での画像取得

### エンドポイント
```
GET /api/questions/
GET /api/questions/{id}/
GET /api/questions/random_questions/
```

### レスポンス例
```json
{
  "id": 19,
  "text": "どこの国でしょう",
  "image": "/media/question_images/71pnm6LK3nL.__AC_SY445_SX342_QL70_ML2_.jpg",
  "choices": [...]
}
```

### フロントエンドでの表示方法

#### Vue.js (現在のプロジェクト)
```vue
<template>
  <div class="question-container">
    <h3>{{ question.text }}</h3>
    <img
      v-if="question.image"
      :src="`http://localhost:8000${question.image}`"
      :alt="question.text"
      class="question-image"
    />
    <div class="choices">
      <!-- 選択肢の表示 -->
    </div>
  </div>
</template>

<style scoped>
.question-image {
  max-width: 100%;
  height: auto;
  margin: 20px 0;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
</style>
```

#### React
```jsx
function QuestionComponent({ question }) {
  return (
    <div className="question-container">
      <h3>{question.text}</h3>
      {question.image && (
        <img
          src={`http://localhost:8000${question.image}`}
          alt={question.text}
          className="question-image"
        />
      )}
      <div className="choices">
        {/* 選択肢の表示 */}
      </div>
    </div>
  );
}
```

## トラブルシューティング

### 画像がアップロードできない場合

#### 1. Pillowがインストールされているか確認
```bash
cd quiz_project
source venv/bin/activate
pip list | grep -i pillow
```

インストールされていない場合:
```bash
pip install Pillow
```

#### 2. メディアディレクトリの権限確認
```bash
ls -la /home/kensukemt2/django/quiz_project/media/
ls -la /home/kensukemt2/django/quiz_project/media/question_images/
```

権限がない場合:
```bash
chmod 755 /home/kensukemt2/django/quiz_project/media/
chmod 755 /home/kensukemt2/django/quiz_project/media/question_images/
```

#### 3. settings.pyの設定確認
```python
# quiz_project/settings.py
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

#### 4. urls.pyの設定確認 (開発環境のみ)
```python
# quiz_project/urls.py
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### 画像が表示されない場合

#### 1. 開発サーバーが起動しているか確認
```bash
cd quiz_project
source venv/bin/activate
python manage.py runserver
```

#### 2. 画像URLが正しいか確認
- 正しい: `http://localhost:8000/media/question_images/image.jpg`
- 間違い: `http://localhost:8000/question_images/image.jpg`

#### 3. ブラウザの開発者ツールでネットワークエラーを確認
- F12キーを押して開発者ツールを開く
- Networkタブで画像リクエストの状態を確認
- 404エラーの場合: URLパスを確認
- 403エラーの場合: ファイル権限を確認

## 現在の状況

### データベース内の画像
- 総質問数: **332問**
- 画像付き質問: **1問**
  - ID: 19
  - 質問: "どこの国でしょう"
  - 画像: `question_images/71pnm6LK3nL.__AC_SY445_SX342_QL70_ML2_.jpg`
  - ファイルサイズ: 18,104 bytes

### テスト結果
✅ プログラムによる画像アップロードテスト成功
- テスト画像の作成・保存・削除が正常に完了
- 画像URLの生成が正常に動作

## 推奨事項

### 本番環境への移行時

1. **静的ファイルサーバーの利用**
   - AWS S3
   - Google Cloud Storage
   - Azure Blob Storage

2. **django-storagesの導入**
   ```bash
   pip install django-storages
   pip install boto3  # AWS S3の場合
   ```

3. **settings.pyの設定例 (AWS S3)**
   ```python
   # settings.py
   INSTALLED_APPS += ['storages']

   AWS_ACCESS_KEY_ID = 'your-access-key'
   AWS_SECRET_ACCESS_KEY = 'your-secret-key'
   AWS_STORAGE_BUCKET_NAME = 'your-bucket-name'
   AWS_S3_REGION_NAME = 'ap-northeast-1'

   DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
   ```

### 画像最適化

1. **画像サイズ制限の追加**
   ```python
   # models.py
   from django.core.validators import FileExtensionValidator
   from django.core.exceptions import ValidationError

   def validate_image_size(image):
       filesize = image.size
       max_size = 5 * 1024 * 1024  # 5MB
       if filesize > max_size:
           raise ValidationError("画像サイズは5MB以下にしてください")

   class Question(models.Model):
       image = models.ImageField(
           upload_to='question_images/',
           blank=True,
           null=True,
           validators=[
               FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif']),
               validate_image_size
           ]
       )
   ```

2. **画像の自動リサイズ**
   ```python
   # models.py
   from PIL import Image
   import os

   class Question(models.Model):
       # ...

       def save(self, *args, **kwargs):
           super().save(*args, **kwargs)

           if self.image:
               img = Image.open(self.image.path)

               # 最大幅を設定
               max_width = 800
               if img.width > max_width:
                   ratio = max_width / img.width
                   new_height = int(img.height * ratio)
                   img = img.resize((max_width, new_height), Image.LANCZOS)
                   img.save(self.image.path)
   ```

## まとめ

✅ **画像アップロード機能は完全に動作しています**

- Pillowライブラリ: インストール済み
- メディアディレクトリ: 設定済み・存在確認済み
- アップロード機能: テスト済み・正常動作
- URL設定: 正常に構成済み

管理画面から画像を自由にアップロードできます。問題が発生した場合は、上記のトラブルシューティングセクションを参照してください。
