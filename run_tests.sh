#!/bin/bash

# テスト自動化スクリプト
# マジカルクイズアプリケーションの全テストを実行

set -e  # エラーが発生したら即座に終了

# カラー出力の設定
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ログ関数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# ヘッダー表示
echo ""
echo "=========================================="
echo "  マジカルクイズ 自動テストスイート"
echo "=========================================="
echo ""

# プロジェクトルートディレクトリ
PROJECT_ROOT="/home/kensukemt2/django"
BACKEND_DIR="$PROJECT_ROOT/quiz_project"
FRONTEND_DIR="$PROJECT_ROOT/quiz-frontend"
VENV_PATH="$PROJECT_ROOT/venv"

# テスト結果を保存
BACKEND_TEST_RESULT=0
FRONTEND_TEST_RESULT=0
API_TEST_RESULT=0

# ========================================
# 1. バックエンド (Django) テスト
# ========================================
echo ""
log_info "バックエンドテストを開始します..."
echo ""

cd "$BACKEND_DIR"

# 仮想環境をアクティベート
source "$VENV_PATH/bin/activate"

# テストを実行
log_info "Djangoユニットテストを実行中..."
if python manage.py test quiz_api.tests --verbosity=2; then
    log_success "バックエンドテスト: すべて合格 ✓"
else
    log_error "バックエンドテスト: 失敗"
    BACKEND_TEST_RESULT=1
fi

# ========================================
# 2. コードカバレッジ (オプション)
# ========================================
echo ""
log_info "コードカバレッジを計測します..."

if command -v coverage &> /dev/null; then
    coverage run --source='quiz_api' manage.py test quiz_api.tests
    coverage report
    coverage html
    log_success "カバレッジレポートが htmlcov/ に生成されました"
else
    log_warning "coverage がインストールされていません。スキップします。"
    log_info "インストールするには: pip install coverage"
fi

# ========================================
# 3. API統合テスト
# ========================================
echo ""
log_info "API統合テストを開始します..."
echo ""

# サーバーが起動しているか確認
if ! curl -s http://localhost:8000/api/categories/ > /dev/null 2>&1; then
    log_warning "Djangoサーバーが起動していません。統合テストをスキップします。"
    log_info "サーバーを起動してから再実行してください: python manage.py runserver"
else
    log_info "APIエンドポイントをテスト中..."

    # カテゴリAPI
    if curl -s -f http://localhost:8000/api/categories/ > /dev/null; then
        log_success "✓ カテゴリAPI: OK"
    else
        log_error "✗ カテゴリAPI: 失敗"
        API_TEST_RESULT=1
    fi

    # リーダーボードAPI (全体)
    if curl -s -f "http://localhost:8000/api/quiz/leaderboard/?category=all" > /dev/null; then
        log_success "✓ リーダーボードAPI (全体): OK"
    else
        log_error "✗ リーダーボードAPI (全体): 失敗"
        API_TEST_RESULT=1
    fi

    # リーダーボードAPI (カテゴリ別)
    if curl -s -f "http://localhost:8000/api/quiz/leaderboard/?category=1" > /dev/null; then
        log_success "✓ リーダーボードAPI (カテゴリ別): OK"
    else
        log_error "✗ リーダーボードAPI (カテゴリ別): 失敗"
        API_TEST_RESULT=1
    fi

    # 問題取得API
    if curl -s -f "http://localhost:8000/api/questions/session_questions/?category=1&limit=5" > /dev/null; then
        log_success "✓ 問題取得API: OK"
    else
        log_error "✗ 問題取得API: 失敗"
        API_TEST_RESULT=1
    fi
fi

# ========================================
# 4. フロントエンド (Vue.js) チェック
# ========================================
echo ""
log_info "フロントエンドをチェックします..."
echo ""

cd "$FRONTEND_DIR"

# ESLintチェック
log_info "ESLint を実行中..."
if npm run lint; then
    log_success "ESLint: エラーなし ✓"
else
    log_error "ESLint: エラーが見つかりました"
    FRONTEND_TEST_RESULT=1
fi

# ビルドテスト
log_info "本番ビルドをテスト中..."
if npm run build; then
    log_success "ビルド: 成功 ✓"
else
    log_error "ビルド: 失敗"
    FRONTEND_TEST_RESULT=1
fi

# ========================================
# 5. テスト結果サマリー
# ========================================
echo ""
echo "=========================================="
echo "  テスト結果サマリー"
echo "=========================================="
echo ""

TOTAL_FAILURES=0

if [ $BACKEND_TEST_RESULT -eq 0 ]; then
    log_success "バックエンドテスト: 合格 ✓"
else
    log_error "バックエンドテスト: 失敗 ✗"
    TOTAL_FAILURES=$((TOTAL_FAILURES + 1))
fi

if [ $API_TEST_RESULT -eq 0 ]; then
    log_success "API統合テスト: 合格 ✓"
else
    log_error "API統合テスト: 失敗 ✗"
    TOTAL_FAILURES=$((TOTAL_FAILURES + 1))
fi

if [ $FRONTEND_TEST_RESULT -eq 0 ]; then
    log_success "フロントエンド: 合格 ✓"
else
    log_error "フロントエンド: 失敗 ✗"
    TOTAL_FAILURES=$((TOTAL_FAILURES + 1))
fi

echo ""
echo "=========================================="
if [ $TOTAL_FAILURES -eq 0 ]; then
    log_success "全テスト合格! 🎉"
    echo "=========================================="
    exit 0
else
    log_error "$TOTAL_FAILURES 個のテストスイートが失敗しました"
    echo "=========================================="
    exit 1
fi
