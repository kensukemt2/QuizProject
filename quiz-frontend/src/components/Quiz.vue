<template>
  <div class="quiz-container">
    <!-- ゲストモードバナー -->
    <div v-if="isGuestMode" class="guest-mode-banner">
      <div class="banner-content">
        <div class="guest-icon">👤</div>
        <span>ゲストモードでクイズを実行中</span>
      </div>
      <router-link to="/login" class="login-link">ログインして結果を保存する</router-link>
    </div>
    
    <!-- ローディング表示 -->
    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <p>読み込み中...</p>
    </div>
    
    <div v-else>
      <!-- カテゴリー選択画面 -->
      <div class="category-selection" v-if="!currentQuestion && !quizCompleted && !loading">
        <h2>カテゴリを選択してください</h2>
        <div class="sparkle sparkle-1"></div>
        <div class="sparkle sparkle-2"></div>
        
        <div class="categories">
          <button 
            v-for="(category, index) in categories" 
            :key="`cat-${index}`"
            @click="category ? selectCategory(category.id) : null"
            class="category-btn"
            :disabled="!category"
            :style="getCategoryColorStyle(index)"
          >
            <div class="category-icon">{{ category?.name?.charAt(0) || '?' }}</div>
            <span class="category-name">{{ category?.name || 'カテゴリなし' }}</span>
          </button>
        </div>
      </div>
      
      <!-- クイズ問題表示 -->
      <div class="quiz" v-else-if="currentQuestion">
        <div class="quiz-header">
          <div class="progress-container">
            <div class="progress-label">質問 {{ questionIndex + 1 }} / {{ questions.length }}</div>
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: `${(questionIndex + 1) / questions.length * 100}%` }"></div>
            </div>
          </div>
          
          <div class="score-display">
            <div class="score-label">スコア</div>
            <div class="score-value">{{ score }}</div>
          </div>
          
          <!-- セッション情報表示（開発時のみ） -->
          <div v-if="sessionInfo && sessionInfo.session_id" class="session-info">
            <div class="session-label">セッション</div>
            <div class="session-details">
              <div class="session-used">使用: {{ sessionInfo.used_count }}</div>
              <div class="session-remaining">残り: {{ sessionInfo.remaining }}</div>
            </div>
          </div>
        </div>
        
        <div class="question-card">
          <div class="question-text">
            <h2>{{ currentQuestion.text }}</h2>
          </div>
          
          <!-- 画像表示 -->
          <div v-if="currentQuestion.image" class="question-image">
            <img :src="getImageUrl(currentQuestion.image)" :alt="currentQuestion.text" />
          </div>
          
          <div class="choices">
            <button 
              v-for="(choice, index) in (currentQuestion?.choices || [])" 
              :key="`choice-${index}`"
              @click="checkAnswer(choice)"
              :disabled="answered"
              :class="{ 
                'choice-btn': true,
                'correct': answered && choice?.is_correct,
                'incorrect': answered && selectedChoice === choice && !choice?.is_correct 
              }"
            >
              <div class="choice-number">{{ ['A', 'B', 'C', 'D'][index] }}</div>
              <div class="choice-text">{{ choice?.text || '選択肢' }}</div>
            </button>
          </div>
          
          <!-- 回答後のフィードバック -->
          <div class="feedback" v-if="answered">
            <div v-if="correct" class="correct-feedback">
              <div class="feedback-icon">✓</div>
              <p>正解!</p>
            </div>
            <div v-else class="incorrect-feedback">
              <div class="feedback-icon">✗</div>
              <p>不正解! 正解は「{{ correctAnswerText }}」でした。</p>
            </div>
          </div>
          
          <button 
            v-if="answered" 
            @click="nextQuestion" 
            class="next-btn"
          >
            {{ isLastQuestion ? '結果を見る' : '次の問題' }}
            <span class="next-icon">{{ isLastQuestion ? '🏆' : '▶' }}</span>
          </button>
        </div>
      </div>

      <!-- エラー表示 -->
      <div v-else-if="error" class="error-message">
        <div class="error-icon">!</div>
        <p>{{ error }}</p>
        <button @click="resetQuiz" class="reset-btn">カテゴリー選択に戻る</button>
      </div>
      
      <!-- クイズ結果画面 -->
      <div class="quiz-results" v-if="quizCompleted && questions.length > 0">
        <h2>クイズ結果</h2>
        
        <div class="results-summary">
          <div class="result-item">
            <div class="result-label">スコア</div>
            <div class="result-value">{{ score }}/{{ questions.length }}</div>
          </div>
          
          <div class="result-item">
            <div class="result-label">正答率</div>
            <div class="result-value percentage">{{ Math.round((score / questions.length) * 100) }}%</div>
          </div>
        </div>
        
        <div class="result-chart">
          <div class="chart-bar">
            <div class="chart-fill" :style="{ width: `${Math.round((score / questions.length) * 100)}%` }"></div>
          </div>
          <div class="chart-scale">
            <span>0%</span>
            <span>50%</span>
            <span>100%</span>
          </div>
        </div>
        
        <p v-if="isGuestMode" class="guest-notice">
          <span class="notice-icon">ℹ️</span>
          ゲストモードです。結果を保存するには
          <router-link to="/login">ログイン</router-link>
          してください。
        </p>
        <p>スコア: {{ score }}/{{ questions.length }}</p>
        <p>正答率: {{ Math.round((score / questions.length) * 100) }}%</p>
        
        <div class="answers-review" v-if="allAnswers && allAnswers.length > 0">
          <h3>回答レビュー</h3>
          <div class="answers-list">
            <div 
              v-for="(answer, index) in validAnswers" 
              :key="'answer-' + index"
              class="answer-item"
              :class="{ 'correct-answer': answer.correct, 'incorrect-answer': !answer.correct }"
            >
              <div class="answer-number">{{ index + 1 }}</div>
              <div class="answer-content">
                <p class="question-text">{{ answer.question?.text || '質問' }}</p>
                <div class="answer-details">
                  <p class="user-answer">
                    <span class="answer-label">あなたの回答:</span> 
                    {{ answer.selectedChoice?.text || '未回答' }}
                    <span class="result-icon">{{ answer.correct ? '✓' : '✗' }}</span>
                  </p>
                  <p v-if="!answer.correct" class="correct-text">
                    <span class="answer-label">正解:</span> 
                    {{ answer.correctChoice?.text || '不明' }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="quiz-actions">
          <button @click="retakeCurrentQuiz" class="retake-btn">
            <span class="button-icon">🔁</span>
            同じクイズを実施する
          </button>
          
          <button @click="resetQuiz" class="restart-btn">
            <span class="button-icon">🔄</span>
            新しいクイズを始める
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useToast } from 'vue-toastification';
import axios from 'axios';
import api from '../utils/api';
import { mapGetters } from 'vuex'; // Vuexのマッピングを追加

export default {
  name: 'QuizPage',
  setup() {
    // Composition APIでtoastを設定
    const toast = useToast();
    return { toast };
  },
  data() {
    return {
      loading: true,
      categories: [],
      questions: [],
      questionIndex: 0,
      score: 0,
      answered: false,
      selectedChoice: null,
      correct: false,
      quizCompleted: false,
      allAnswers: [],
      selectedCategory: null,
      isGuestMode: false,
      showLoginPrompt: false,
      error: null, // エラーステートの追加
      sessionInfo: null, // セッション情報
      // カテゴリーの背景色用
      categoryColors: [
        { bg: '#F97316', text: '#FFFFFF' },
        { bg: '#10B981', text: '#FFFFFF' },
        { bg: '#FACC15', text: '#1E40AF' },
        { bg: '#EF4444', text: '#FFFFFF' },
        { bg: '#8B5CF6', text: '#FFFFFF' },
        { bg: '#3B82F6', text: '#FFFFFF' },
        { bg: '#EC4899', text: '#FFFFFF' },
        { bg: '#14B8A6', text: '#FFFFFF' }
      ]
    };
  },
  computed: {
    // Vuexのゲッターをマッピング
    ...mapGetters('auth', ['isAuthenticated', 'user']),
    
    currentQuestion() {
      // 質問がない場合や範囲外の場合はnullを返す
      if (!this.questions || !this.questions.length || this.questionIndex >= this.questions.length) {
        return null;
      }
      
      // 質問オブジェクトのディープコピーを作成（元データを変更しないため）
      try {
        const question = JSON.parse(JSON.stringify(this.questions[this.questionIndex]));
        
        // choicesプロパティの安全性チェック
        if (!question || !question.choices) {
          console.warn('質問データに問題があります:', question);
          return { ...question, choices: [], text: question?.text || '質問データエラー' };
        }
        
        // 各選択肢の処理
        question.choices = (question.choices || [])
          .filter(choice => choice !== null && choice !== undefined) // null/undefinedをフィルタリング
          .map((choice, index) => {
            if (!choice) return { id: `temp_${index}`, text: '選択肢データエラー', is_correct: false };
            if (!choice.id) choice.id = `temp_${index}`;
            return choice;
          });
        
        return question;
      } catch (error) {
        console.error('質問データの処理中にエラー:', error);
        return { id: 'error', text: 'データエラー', choices: [] };
      }
    },
    correctAnswerText() {
      if (!this.currentQuestion || !this.currentQuestion.choices) return '';
      const correctChoice = this.currentQuestion.choices.find(choice => choice?.is_correct);
      return correctChoice?.text || '';
    },
    isLastQuestion() {
      return this.questionIndex === this.questions.length - 1;
    },
    // 有効な回答だけをフィルタリングするcomputed property
    validAnswers() {
      return this.allAnswers.filter(answer => answer && answer.question);
    },
  },
  watch: {
    questions(newQuestions) {
      if (!newQuestions || newQuestions.length === 0) {
        this.error = this.error || 'このカテゴリには問題がありません';
      } else {
        this.error = null;
      }
    },
    currentQuestion(newQuestion) {
      // デバッグ用
      console.log('currentQuestion変更:', newQuestion ? `ID: ${newQuestion.id}` : 'null');
      
      if (!newQuestion && this.questions.length > 0 && !this.quizCompleted) {
        console.warn('質問データに問題があります。再設定します。');
        this.questionIndex = 0; // 安全にインデックスをリセット
      }
    },
    // ルートの変更を監視してカテゴリー変更に対応
    '$route'(newRoute, oldRoute) {
      console.log('Route changed:', newRoute.query);
      
      // カテゴリーパラメータが変更された場合
      const newCategoryId = newRoute.query.category;
      const oldCategoryId = oldRoute.query.category;
      
      if (newCategoryId && newCategoryId !== oldCategoryId) {
        console.log('Category parameter changed:', newCategoryId);
        this.startQuizFromCategory(newCategoryId);
      } else if (!newCategoryId && oldCategoryId) {
        // カテゴリーパラメータが削除された場合、カテゴリー選択画面に戻る
        console.log('Category parameter removed, returning to category selection');
        this.resetQuiz();
      }
    }
  },
  methods: {
    getCategoryColorStyle(index) {
      const colorIndex = index % this.categoryColors.length;
      const color = this.categoryColors[colorIndex];
      return {
        backgroundColor: color.bg,
        color: color.text
      };
    },
    async fetchCategories() {
      try {
        this.loading = true;
        console.log('カテゴリ取得開始');
        const response = await axios.get('/api/categories/');
        console.log('カテゴリ取得成功:', response.data);
        
        // レスポンスがページネーション形式かどうか確認
        let categoryData;
        if (response.data && Array.isArray(response.data.results)) {
          // ページネーション形式の場合
          categoryData = response.data.results;
          console.log('ページネーションデータから取得:', categoryData);
        } else if (Array.isArray(response.data)) {
          // 単純な配列の場合
          categoryData = response.data;
          console.log('単純な配列:', categoryData);
        } else {
          console.error('予期しないレスポース形式:', response.data);
          this.error = 'サーバーからの応答が正しくありません';
          this.categories = [];
          this.loading = false;
          return;
        }
        
        // データの検証と変換
        const validatedData = categoryData
          .filter(item => item !== null && item !== undefined)
          .map((item, index) => {
            if (!item) return { id: `temp-${index}`, name: 'データなし' };
            if (!item.id) item.id = `temp-${index}`;
            return item;
          });
        
        this.categories = validatedData;
        console.log('カテゴリ設定完了:', this.categories);
        this.loading = false;
      } catch (error) {
        console.error('カテゴリの取得に失敗しました:', error);
        this.loading = false;
        this.error = 'カテゴリの読み込みに失敗しました';
        this.categories = [];
      }
    },
    async selectCategory(categoryId) {
      if (!categoryId) {
        console.error('カテゴリIDが無効です');
        this.error = 'カテゴリの選択に問題が発生しました';
        this.loading = false;
        return;
      }
    
      console.log('Category selected:', categoryId);
      
      // ローディング状態を開始
      this.loading = true;
      this.error = null;
      
      // URLパラメータを更新（ページ遷移なし）
      this.$router.replace({
        path: '/quiz',
        query: { 
          category: categoryId,
          mode: this.isAuthenticated ? 'user' : 'guest'
        }
      });
      
      // 直接クイズを開始
      await this.startQuizFromCategory(categoryId);
    },
    async fetchQuestions(categoryId) {
      this.loading = true;
      this.error = null;
      
      try {
        // カテゴリIDのログ出力と型確認
        console.log('カテゴリID:', categoryId, 'タイプ:', typeof categoryId);
        
        // URLを構築する前に確実に数値であることを確認
        const categoryIdNum = Number(categoryId);
        if (isNaN(categoryIdNum)) {
          throw new Error(`無効なカテゴリID: ${categoryId}`);
        }
        
        // セッション管理による重複なしランダム問題取得を使用
        const sessionId = localStorage.getItem('quiz_session_id');
        let url;
        
        if (sessionId) {
          // 既存セッションを使用して継続取得
          url = `/api/questions/session_questions/?category=${categoryIdNum}&limit=10&session_id=${sessionId}`;
        } else {
          // 新しいセッションを開始
          url = `/api/questions/session_questions/?category=${categoryIdNum}&limit=10`;
        }
        
        console.log('リクエスト先URL:', url);
        console.log('使用セッションID:', sessionId || '新規');
        
        const response = await axios.get(url);
        console.log('API応答データ:', response.data);
        
        // セッション情報を保存
        if (response.data.session_id) {
          localStorage.setItem('quiz_session_id', response.data.session_id);
          console.log('セッションID保存:', response.data.session_id);
          
          // セッション情報をコンポーネントの状態に保存
          this.sessionInfo = {
            session_id: response.data.session_id,
            used_count: response.data.used_count || 0,
            remaining: response.data.remaining || 0,
            total_available: response.data.total_available || 0
          };
        }
        
        // セッション管理APIのレスポンス処理
        let questionsData;
        if (response.data && Array.isArray(response.data.results)) {
          // 新しいセッション管理APIの形式
          questionsData = response.data.results;
          console.log('セッション管理APIから質問を取得:', questionsData);
          console.log(`セッション情報: 使用済み${response.data.used_count}問、残り${response.data.remaining}問`);
          
          // セッション情報をログに記録
          if (response.data.message) {
            console.log('API Message:', response.data.message);
          }
        } else if (Array.isArray(response.data)) {
          // 旧API形式（フォールバック）
          questionsData = response.data;
          console.log('旧API形式から質問を取得:', questionsData);
        } else {
          console.error('予期しない質問データ形式:', response.data);
          this.error = '質問データの形式が正しくありません';
          this.loading = false;
          return;
        }
        
        if (!questionsData.length) {
          this.error = 'このカテゴリには問題がありません';
          this.loading = false;
          return;
        }
        
        // データの検証と修正
        const validatedQuestions = questionsData.map(question => {
          if (!question.choices || !Array.isArray(question.choices)) {
            question.choices = [];
          } else {
            // 選択肢の検証
            question.choices = question.choices
              .filter(choice => choice !== null && choice !== undefined)
              .map((choice, idx) => {
                if (!choice) return { id: `temp_${question.id}_${idx}`, text: '選択肢データなし', is_correct: false };
                if (!choice.id) choice.id = `temp_${question.id}_${idx}`;
                return choice;
              });
          }
          return question;
        });
        
        // セッション管理APIでは既にランダムなので、シャッフルは不要
        this.questions = validatedQuestions;
        this.questionIndex = 0;
        this.score = 0;
        this.quizCompleted = false; // 'completed'ではなく'quizCompleted'に統一
        this.answered = false;
        this.loading = false;
      } catch (error) {
        console.error('質問の取得に失敗しました:', error);
        this.error = '質問の読み込みに失敗しました';
        this.loading = false;
      }
    },
    shuffleArray(array) {
      // Fisher-Yates アルゴリズムを使った配列のシャッフル
      const newArray = [...array];
      for (let i = newArray.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [newArray[i], newArray[j]] = [newArray[j], newArray[i]];
      }
      return newArray;
    },
    checkAnswer(choice) {
      if (!choice) {
        console.error('選択された選択肢がnullです');
        return;
      }
    
      this.answered = true;
      this.selectedChoice = choice;
      this.correct = !!choice.is_correct;
      
      if (choice.is_correct) {
        this.score++;
      }
      
      // 回答を記録（プロパティ名を一致させる）
      const correctChoice = this.currentQuestion?.choices?.find(c => c?.is_correct) || null;
      
      this.allAnswers.push({
        question: this.currentQuestion,
        selectedChoice: choice,
        correct: !!choice.is_correct,  // is_correctではなくcorrectに統一
        correctChoice: correctChoice
      });
    },
    nextQuestion() {
      if (!this.currentQuestion) {
        console.warn('現在の質問がnullです');
        this.resetQuiz();
        return;
      }
      
      if (this.isLastQuestion) {
        this.quizCompleted = true;
        // ユーザーがログインしている場合、結果を保存
        if (this.$store.getters['auth/isAuthenticated']) {
          this.saveQuizResult();
        } else if (this.isGuestMode) {
          this.saveGuestScore();
        }
        
        // 結果画面にスクロール
        this.$nextTick(() => {
          this.scrollToResults();
        });
      } else {
        this.questionIndex++;
        this.answered = false;
        this.selectedChoice = null;
      }
    },
    // resetQuizの拡張
    resetQuiz() {
      this.questions = [];
      this.questionIndex = 0;
      this.score = 0;
      this.answered = false;
      this.selectedChoice = null;
      this.quizCompleted = false;
      this.allAnswers = [];
      this.selectedCategory = null;
      this.error = null;
      this.sessionInfo = null;
      
      // セッションIDをクリアして新しいセッションを開始
      localStorage.removeItem('quiz_session_id');
      console.log('クイズセッションをリセットしました');
      
      // URLパラメータもクリア（カテゴリー選択画面に戻る）
      if (this.$route.query.category) {
        this.$router.replace({
          path: '/quiz',
          query: { 
            mode: this.isAuthenticated ? 'user' : 'guest'
          }
        });
      }
      
      // カテゴリデータがない場合は再取得
      if (!this.categories || this.categories.length === 0) {
        this.fetchCategories();
      } else {
        this.loading = false;
      }
    },
    
    // セッションリセット用の新しいメソッド
    async resetQuizSession() {
      const sessionId = localStorage.getItem('quiz_session_id');
      if (sessionId && this.selectedCategory) {
        try {
          // セッションリセットAPIを呼び出し
          const categoryIdNum = Number(this.selectedCategory.id);
          const url = `/api/questions/session_questions/?category=${categoryIdNum}&limit=10&session_id=${sessionId}&reset=true`;
          
          console.log('セッションリセット中...', url);
          await axios.get(url);
          console.log('セッションがリセットされました');
        } catch (error) {
          console.warn('セッションリセットに失敗:', error);
          // エラーの場合はローカルストレージをクリア
          localStorage.removeItem('quiz_session_id');
        }
      }
    },
    async saveQuizResult() {
      if (!this.quizCompleted) return;
      
      try {
        // レスポンスデータの準備
        const responseData = this.allAnswers
          .filter(answer => answer && answer.question && answer.question.id)
          .map(answer => ({
            question_id: answer.question.id,
            selected_choice_id: answer.selectedChoice?.id || null,
            is_correct: !!answer.correct
          }));
        
        // 結果を保存
        await api.post('/api/quiz/save-result/', {
          category_id: this.selectedCategory?.id,
          score: this.score,
          total_questions: this.questions.length,
          responses: responseData
        });
        
        // 成功メッセージ
        this.toast.success('クイズ結果が保存されました！');
      } catch (error) {
        console.error('結果の保存に失敗しました:', error);
        // エラー処理...
      }
    },
    async saveGuestScore() {
      // ローカルストレージにゲストスコアを一時保存
      const guestScores = JSON.parse(localStorage.getItem('guestScores') || '[]');
      
      // カテゴリ情報を安全に取得
      const categoryId = this.selectedCategory?.id || 0;
      const categoryName = this.getCategoryName(this.selectedCategory);
      
      guestScores.push({
        id: Date.now(),
        category_id: categoryId,
        category_name: categoryName,
        score: this.score,
        total_questions: this.questions.length,
        percentage: (this.score / this.questions.length) * 100,
        created_at: new Date().toISOString()
      });
      
      // 最新10件だけ保存
      if (guestScores.length > 10) {
        guestScores.splice(0, guestScores.length - 10);
      }
      
      localStorage.setItem('guestScores', JSON.stringify(guestScores));
      
      // ゲストユーザーにログインを促すメッセージ
      this.toast.info('ログインすると、クイズの履歴が永続的に保存されます！');
    },
    getCategoryName(category) {
      if (!category) return 'カテゴリなし';
      return category.name || 'カテゴリなし';
    },
    getImageUrl(imagePath) {
      if (!imagePath) return '';
      // 相対パスの場合はDjangoサーバーのベースURLを追加
      if (imagePath.startsWith('http')) {
        return imagePath;
      }
      return `${imagePath.startsWith('/') ? '' : '/'}${imagePath}`;
    },
    initQuiz() {
      // コンポーネントの状態を初期化
      this.questions = [];
      this.questionIndex = 0;
      this.score = 0;
      this.answered = false;
      this.selectedChoice = null;
      this.quizCompleted = false;
      this.allAnswers = [];
      this.selectedCategory = null;
      this.sessionInfo = null;
      
      // ゲストモード状態の取得（認証済みの場合はゲストモードを無効にする）
      if (this.isAuthenticated) {
        this.isGuestMode = false;
        // ゲストモード関連のフラグをクリア
        this.$store.commit('quiz/SET_GUEST_MODE', false);
        localStorage.removeItem('quizMode');
      } else {
        this.isGuestMode = this.$store.getters['quiz/isGuestMode'] || 
                          localStorage.getItem('quizMode') === 'guest' ||
                          this.$route.query.mode === 'guest';
      }
      
      // URLクエリパラメータからカテゴリーIDを確認
      const categoryIdFromQuery = this.$route.query.category;
      
      if (categoryIdFromQuery) {
        console.log('URL from category ID detected:', categoryIdFromQuery);
        // カテゴリーが指定されている場合、直接そのカテゴリーのクイズを開始
        this.startQuizFromCategory(categoryIdFromQuery);
      } else {
        // カテゴリを取得してカテゴリー選択画面を表示
        this.fetchCategories();
      }
    },
    
    // URLから直接カテゴリーを指定してクイズを開始
    async startQuizFromCategory(categoryId) {
      console.log('Starting quiz for category:', categoryId);
      
      try {
        this.loading = true;
        this.error = null;
        
        // まずカテゴリー情報を取得
        const categoriesResponse = await axios.get('/api/categories/');
        let categoriesData = [];
        
        if (Array.isArray(categoriesResponse.data)) {
          categoriesData = categoriesResponse.data;
        } else if (categoriesResponse.data && Array.isArray(categoriesResponse.data.results)) {
          categoriesData = categoriesResponse.data.results;
        }
        
        // 指定されたカテゴリーを見つける
        const targetCategory = categoriesData.find(cat => cat.id == categoryId);
        
        if (!targetCategory) {
          console.error('指定されたカテゴリーが見つかりません:', categoryId);
          this.error = '指定されたカテゴリーが見つかりません';
          this.loading = false;
          return;
        }
        
        console.log('Found category:', targetCategory);
        this.selectedCategory = targetCategory;
        
        // そのカテゴリーの問題を取得
        await this.fetchQuestions(categoryId);
        
      } catch (error) {
        console.error('カテゴリー指定クイズの開始に失敗:', error);
        this.error = 'クイズの開始に失敗しました';
        this.loading = false;
      }
    },
    scrollToResults() {
      // 結果セクションにスムーズにスクロール
      const resultsElement = document.querySelector('.quiz-results');
      if (resultsElement) {
        resultsElement.scrollIntoView({ 
          behavior: 'smooth',
          block: 'start'
        });
      }
    },
    async retakeCurrentQuiz() {
      if (!this.selectedCategory) {
        console.error('選択されたカテゴリーがありません');
        this.error = 'カテゴリー情報が見つかりません';
        return;
      }
      
      // クイズセッションをリセット（新しい問題セットを取得するため）
      await this.resetQuizSession();
      
      // 状態をリセット（ただしカテゴリー情報は保持）
      this.questions = [];
      this.questionIndex = 0;
      this.score = 0;
      this.answered = false;
      this.selectedChoice = null;
      this.quizCompleted = false;
      this.allAnswers = [];
      this.error = null;
      this.sessionInfo = null;
      
      // 同じカテゴリーで新しいクイズを開始
      console.log('同じカテゴリーでクイズを再開始:', this.selectedCategory.id);
      await this.startQuizFromCategory(this.selectedCategory.id);
    }
  },
  created() {
    console.log('Quizコンポーネント作成...');
    
    // ナビゲーションガードが処理するので、ここではクイズ初期化だけを行う
    this.initQuiz();
  },
  mounted() {
    // マウント後に認証チェック（Vuexストアの値が確実に利用可能）
    if (!this.isGuestMode && !this.isAuthenticated) {
      console.log('認証されていないユーザー。ログインページにリダイレクト');
      this.$router.push('/login');
    } else {
      console.log('認証済みまたはゲストモード。クイズ表示OK');
    }
  }
};
</script>

<style scoped>
/* ── ベース ── */
.quiz-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px 20px;
  color: #f5f0e8;
}

/* ゲストバナー */
.guest-mode-banner {
  background: #0e0e12;
  border: 1px solid #1a1a1a;
  border-left: 4px solid #f5e642;
  padding: 12px 20px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.banner-content { display: flex; align-items: center; gap: 8px; color: #f5e642; font-size: 13px; }
.guest-icon { font-size: 16px; }
.login-link {
  background: #e8001c;
  color: #fff;
  padding: 6px 16px;
  text-decoration: none;
  font-size: 11px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  clip-path: polygon(0 0, 100% 0, 94% 100%, 0 100%);
  transition: background 0.15s;
}
.login-link:hover { background: #ff1a35; }

/* ローディング */
.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  color: #555;
  gap: 20px;
}
.loading-spinner {
  width: 40px; height: 40px;
  border: 3px solid #1a1a1a;
  border-top: 3px solid #e8001c;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── カテゴリ選択 ── */
.category-selection {
  background: #0e0e12;
  border: 1px solid #1a1a1a;
  border-left: 4px solid #e8001c;
  padding: 30px;
  position: relative;
  overflow: hidden;
}

.category-selection::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image: radial-gradient(circle, rgba(255,255,255,0.03) 1px, transparent 1px);
  background-size: 24px 24px;
  pointer-events: none;
}

.category-selection::after {
  content: '';
  position: absolute;
  top: 0; right: 0;
  width: 0; height: 0;
  border-style: solid;
  border-width: 0 40px 40px 0;
  border-color: transparent #060608 transparent transparent;
}

.category-selection h2 {
  font-size: 24px;
  letter-spacing: 0.08em;
  color: #f5f0e8;
  margin-bottom: 24px;
  text-align: center;
  position: relative;
  z-index: 2;
  text-transform: uppercase;
}

/* スパークル非表示 */
.sparkle { display: none; }

.categories {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 2px;
  position: relative;
  z-index: 2;
}

.category-btn {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 10px;
  padding: 18px 16px;
  background: rgba(255,255,255,0.03);
  border: 1px solid #1a1a1a;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
  overflow: hidden;
  text-align: left;
}

.category-btn::before {
  content: '';
  position: absolute;
  left: 0; top: 0; bottom: 0;
  width: 3px;
  background: currentColor;
  opacity: 0.6;
  transform: scaleY(0);
  transform-origin: bottom;
  transition: transform 0.2s;
}

.category-btn:hover { background: rgba(255,255,255,0.06); transform: translateX(4px); }
.category-btn:hover::before { transform: scaleY(1); }
.category-btn:disabled { opacity: 0.3; cursor: not-allowed; transform: none; }

.category-icon {
  width: 52px;
  height: 52px;
  background: #0a0a0e;
  border: 1px solid #1e1e22;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  font-weight: 700;
  color: #f5f0e8;
  clip-path: polygon(0 0, 100% 0, 78% 100%, 0 100%);
  flex-shrink: 0;
  transition: all 0.15s;
  position: relative;
}

.category-btn:hover .category-icon {
  background: #e8001c;
  border-color: #e8001c;
}

.category-name {
  font-size: 13px;
  letter-spacing: 0.04em;
  color: #f5f0e8;
  font-weight: 700;
  line-height: 1.3;
}

/* ── クイズ画面 ── */
.quiz {
  background: #0e0e12;
  border: 1px solid #1a1a1a;
  border-left: 4px solid #e8001c;
  padding: 28px;
  position: relative;
  overflow: hidden;
}

.quiz::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image: radial-gradient(circle, rgba(255,255,255,0.025) 1px, transparent 1px);
  background-size: 24px 24px;
  pointer-events: none;
}

.quiz::after {
  content: '';
  position: absolute;
  top: 0; right: 0;
  width: 0; height: 0;
  border-style: solid;
  border-width: 0 40px 40px 0;
  border-color: transparent #060608 transparent transparent;
}

/* HUD（ヘッダー部分） */
.quiz-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
  position: relative;
  z-index: 1;
}

.progress-container { flex: 1; display: flex; flex-direction: column; gap: 8px; }

.progress-label {
  font-size: 14px;
  letter-spacing: 0.1em;
  color: #e8001c;
  text-transform: uppercase;
}

.progress-bar {
  height: 3px;
  background: #1a1a1a;
  position: relative;
  overflow: visible;
}

.progress-fill {
  height: 100%;
  background: #e8001c;
  transition: width 0.4s;
  position: relative;
}

.progress-fill::after {
  content: '';
  position: absolute;
  right: -4px; top: 50%;
  transform: translateY(-50%) rotate(45deg);
  width: 7px; height: 7px;
  background: #e8001c;
  box-shadow: 0 0 6px #e8001c;
}

.score-display {
  background: #0a0a0e;
  border: 1px solid #1a1a1a;
  border-top: 2px solid #e8001c;
  padding: 8px 16px;
  text-align: center;
  min-width: 72px;
  clip-path: polygon(0 0, 100% 0, 94% 100%, 0 100%);
}

.score-label { font-size: 10px; letter-spacing: 0.15em; color: #444; text-transform: uppercase; margin-bottom: 2px; }
.score-value { font-size: 22px; letter-spacing: 0.05em; color: #e8001c; line-height: 1; }

/* セッション情報 */
.session-info {
  background: #0a0a0e;
  border: 1px solid #1a1a1a;
  border-top: 2px solid #333;
  padding: 8px 12px;
  text-align: center;
  min-width: 80px;
}
.session-label { font-size: 10px; letter-spacing: 0.1em; color: #333; text-transform: uppercase; }
.session-details { font-size: 11px; }
.session-used { color: #f5e642; }
.session-remaining { color: #22c55e; }

/* 問題カード */
.question-card {
  background: rgba(255,255,255,0.02);
  border: 1px solid #1a1a1a;
  padding: 24px;
  position: relative;
  z-index: 1;
}

.question-text { margin-bottom: 20px; }
.question-text h2 {
  font-size: 18px;
  line-height: 1.6;
  color: #f5f0e8;
  font-family: 'Hiragino Kaku Gothic ProN', 'Noto Sans JP', 'Meiryo', sans-serif !important;
  font-weight: 600;
}

/* 問題画像 */
.question-image { margin: 16px 0; text-align: center; }
.question-image img { max-width: 100%; max-height: 360px; border: 1px solid #1a1a1a; object-fit: contain; }

/* 選択肢 */
.choices { display: flex; flex-direction: column; gap: 6px; margin-bottom: 20px; }

.choice-btn {
  display: flex;
  align-items: center;
  background: #0a0a0e;
  border: 1px solid #1e1e22;
  cursor: pointer;
  transition: all 0.15s;
  position: relative;
  overflow: hidden;
  padding: 0;
}

.choice-btn::before {
  content: '';
  position: absolute;
  left: 0; top: 0; bottom: 0;
  width: 0;
  background: #e8001c;
  opacity: 0.06;
  transition: width 0.2s;
}

.choice-btn:hover:not([disabled])::before,
.choice-btn.correct::before { width: 100%; }
.choice-btn:hover:not([disabled]) { border-color: #e8001c; }
.choice-btn.correct { border-color: #22c55e; }
.choice-btn.correct::before { background: #22c55e; }
.choice-btn.incorrect { border-color: #ef4444; }

.choice-number {
  width: 50px; height: 50px;
  background: #111;
  border-right: 1px solid #1e1e22;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 700;
  color: #333;
  flex-shrink: 0;
  transition: all 0.15s;
  clip-path: polygon(0 0, 100% 0, 82% 100%, 0 100%);
}

.choice-btn:hover:not([disabled]) .choice-number { background: #e8001c; color: #fff; }
.choice-btn.correct .choice-number { background: #22c55e; color: #fff; }
.choice-btn.incorrect .choice-number { background: #ef4444; color: #fff; }

.choice-text {
  flex: 1;
  padding: 0 18px;
  font-size: 15px;
  color: #f5f0e8;
  font-family: 'Hiragino Kaku Gothic ProN', 'Noto Sans JP', 'Meiryo', sans-serif !important;
  font-weight: 500;
  position: relative;
  z-index: 1;
  line-height: 50px;
}

/* フィードバック */
.feedback { margin: 16px 0; }
.correct-feedback, .incorrect-feedback {
  display: flex;
  align-items: center;
  padding: 14px 16px;
  gap: 12px;
}
.correct-feedback { border-left: 3px solid #22c55e; background: rgba(34,197,94,0.06); }
.incorrect-feedback { border-left: 3px solid #ef4444; background: rgba(239,68,68,0.06); }

.feedback-icon {
  width: 28px; height: 28px;
  border-radius: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 14px;
  flex-shrink: 0;
  clip-path: polygon(0 0, 100% 0, 85% 100%, 0 100%);
}
.correct-feedback .feedback-icon { background: #22c55e; color: #fff; }
.incorrect-feedback .feedback-icon { background: #ef4444; color: #fff; }

/* 次へボタン */
.next-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 14px;
  background: #e8001c;
  color: #fff;
  border: none;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  cursor: pointer;
  transition: all 0.15s;
  clip-path: polygon(0 0, 100% 0, 98% 100%, 0 100%);
  box-shadow: 4px 4px 0 rgba(232,0,28,0.3);
  margin-top: 16px;
}
.next-btn:hover { background: #ff1a35; transform: translate(-2px,-2px); box-shadow: 6px 6px 0 rgba(232,0,28,0.4); }
.next-icon { margin-left: 8px; font-size: 12px; }

/* エラー */
.error-message {
  background: #0e0e12;
  border: 1px solid #1a1a1a;
  border-left: 4px solid #ef4444;
  padding: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: #ef4444;
}
.error-icon {
  width: 36px; height: 36px;
  background: #ef4444;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 18px;
  clip-path: polygon(0 0, 100% 0, 85% 100%, 0 100%);
}
.reset-btn {
  background: transparent;
  border: 1px solid #333;
  color: #555;
  padding: 8px 18px;
  cursor: pointer;
  font-size: 12px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  transition: all 0.15s;
  clip-path: polygon(0 0, 100% 0, 94% 100%, 0 100%);
}
.reset-btn:hover { border-color: #e8001c; color: #e8001c; }

/* ── 結果画面 ── */
.quiz-results {
  background: #0e0e12;
  border: 1px solid #1a1a1a;
  border-left: 4px solid #e8001c;
  padding: 30px;
  position: relative;
  overflow: hidden;
}

.quiz-results::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image: radial-gradient(circle, rgba(255,255,255,0.025) 1px, transparent 1px);
  background-size: 24px 24px;
  pointer-events: none;
}

.quiz-results::after {
  content: '';
  position: absolute;
  top: 0; right: 0;
  width: 0; height: 0;
  border-style: solid;
  border-width: 0 40px 40px 0;
  border-color: transparent #060608 transparent transparent;
}

.quiz-results h2 {
  text-align: center;
  font-size: 24px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #f5f0e8;
  margin-bottom: 20px;
  position: relative;
  z-index: 1;
  text-shadow: 3px 3px 0 #e8001c;
}

.results-summary {
  display: flex;
  justify-content: center;
  gap: 2px;
  margin: 20px 0;
  position: relative;
  z-index: 1;
}

.result-item {
  background: #0a0a0e;
  border: 1px solid #1a1a1a;
  border-top: 2px solid #e8001c;
  padding: 16px 20px;
  text-align: center;
  min-width: 110px;
  clip-path: polygon(0 0, 100% 0, 94% 100%, 0 100%);
}
.result-label { font-size: 10px; letter-spacing: 0.12em; color: #444; text-transform: uppercase; margin-bottom: 4px; }
.result-value { font-size: 22px; color: #f5f0e8; line-height: 1; }
.result-value.percentage { color: #e8001c; }

.result-chart { margin: 24px 0; position: relative; z-index: 1; }
.chart-bar { height: 6px; background: #1a1a1a; position: relative; }
.chart-fill { height: 100%; background: linear-gradient(to right, #22c55e, #f5e642); transition: width 1s ease-out; }
.chart-scale { display: flex; justify-content: space-between; font-size: 11px; color: #444; margin-top: 6px; }

/* ゲスト通知 */
.guest-notice {
  background: rgba(245,166,35,0.08);
  border-left: 3px solid #f5a623;
  padding: 12px 16px;
  font-size: 13px;
  color: #888;
  position: relative;
  z-index: 1;
  margin: 16px 0;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
}
.notice-icon { margin-right: 6px; }
.guest-notice a { color: #f5e642; text-decoration: none; font-weight: 700; }

/* 回答レビュー */
.answers-review {
  background: rgba(255,255,255,0.02);
  border: 1px solid #1a1a1a;
  padding: 20px;
  margin: 24px 0;
  position: relative;
  z-index: 1;
}
.answers-review h3 {
  font-size: 14px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #f5f0e8;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #1a1a1a;
}
.answers-list { display: flex; flex-direction: column; gap: 6px; }
.answer-item {
  display: flex;
  background: #0a0a0e;
  border: 1px solid #1a1a1a;
  overflow: hidden;
}
.answer-item.correct-answer { border-left: 3px solid #22c55e; }
.answer-item.incorrect-answer { border-left: 3px solid #ef4444; }
.answer-number {
  width: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  background: rgba(255,255,255,0.03);
  color: #444;
  flex-shrink: 0;
}
.answer-content { flex: 1; padding: 12px 14px; }
.answer-content .question-text { font-size: 13px; font-weight: 600; color: #888; margin-bottom: 6px; }
.answer-details { display: flex; flex-direction: column; gap: 3px; }
.user-answer, .correct-text { font-size: 12px; color: #555; display: flex; align-items: center; gap: 4px; }
.answer-label { color: #333; min-width: 80px; }
.result-icon { font-weight: 700; }

/* アクションボタン */
.quiz-actions {
  display: flex;
  flex-direction: column;
  gap: 6px;
  position: relative;
  z-index: 1;
  margin-top: 20px;
}
.retake-btn, .restart-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 14px;
  color: #fff;
  border: none;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  cursor: pointer;
  transition: all 0.15s;
  clip-path: polygon(0 0, 100% 0, 98% 100%, 0 100%);
}
.retake-btn { background: #1d4ed8; box-shadow: 4px 4px 0 rgba(29,78,216,0.3); }
.retake-btn:hover { background: #2563eb; transform: translate(-2px,-2px); }
.restart-btn { background: #059669; box-shadow: 4px 4px 0 rgba(5,150,105,0.3); }
.restart-btn:hover { background: #10b981; transform: translate(-2px,-2px); }
.button-icon { margin-right: 8px; font-size: 16px; }

/* レスポンシブ */
@media (max-width: 768px) {
  .categories { grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); }
  .results-summary { flex-direction: column; align-items: center; }
  .quiz-header { flex-wrap: wrap; }
}
@media (max-width: 480px) {
  .quiz-container { padding: 10px; }
  .category-selection, .quiz, .quiz-results { padding: 16px; }
  .categories { grid-template-columns: 1fr 1fr; }
  .choice-text { font-size: 13px; }
}
</style>
