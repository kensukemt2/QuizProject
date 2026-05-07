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
.quiz-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  font-family: Arial, sans-serif;
  position: relative;
}

/* ゲストモードバナー */
.guest-mode-banner {
  background: linear-gradient(to right, #FEF3C7, #FBBF24);
  border-radius: 10px;
  padding: 12px 20px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.banner-content {
  display: flex;
  align-items: center;
}

.guest-icon {
  font-size: 20px;
  margin-right: 10px;
}

.login-link {
  background-color: #F97316;
  color: white;
  padding: 8px 15px;
  border-radius: 20px;
  text-decoration: none;
  font-weight: bold;
  transition: all 0.3s;
}

.login-link:hover {
  background-color: #EA580C;
  transform: translateY(-2px);
}

/* ローディング */
.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 5px solid rgba(59, 130, 246, 0.3);
  border-top: 5px solid #F97316;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* カテゴリー選択 */
.category-selection {
  background: linear-gradient(135deg, #3B82F6 0%, #1E40AF 100%);
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  color: white;
  position: relative;
  overflow: hidden;
}

.category-selection::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background:
    linear-gradient(90deg, transparent 19%, rgba(147, 197, 253, 0.2) 20%, transparent 21%),
    linear-gradient(90deg, transparent 39%, rgba(147, 197, 253, 0.2) 40%, transparent 41%),
    linear-gradient(90deg, transparent 59%, rgba(147, 197, 253, 0.2) 60%, transparent 61%),
    linear-gradient(90deg, transparent 79%, rgba(147, 197, 253, 0.2) 80%, transparent 81%),
    linear-gradient(0deg, transparent 19%, rgba(147, 197, 253, 0.2) 20%, transparent 21%),
    linear-gradient(0deg, transparent 39%, rgba(147, 197, 253, 0.2) 40%, transparent 41%),
    linear-gradient(0deg, transparent 59%, rgba(147, 197, 253, 0.2) 60%, transparent 61%),
    linear-gradient(0deg, transparent 79%, rgba(147, 197, 253, 0.2) 80%, transparent 81%);
  background-size: 20% 20%;
  z-index: 0;
}

.category-selection h2 {
  text-align: center;
  margin-bottom: 30px;
  position: relative;
  font-size: 28px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  z-index: 2;
}

.sparkle {
  position: absolute;
  pointer-events: none;
  opacity: 0.6;
  z-index: 1;
}

.sparkle::before {
  content: '✦';
  font-size: 24px;
  color: #FACC15;
}

.sparkle-1 {
  top: 40px;
  right: 60px;
  animation: float 3s ease-in-out infinite;
}

.sparkle-2 {
  bottom: 50px;
  left: 40px;
  animation: float 4s ease-in-out infinite;
}

@keyframes float {
  0% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-10px) rotate(5deg); }
  100% { transform: translateY(0) rotate(0deg); }
}

.categories {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  margin-top: 20px;
  position: relative;
  z-index: 2;
}

.category-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  border: none;
  border-radius: 15px;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
}

.category-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 5px;
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 2.5px 2.5px 0 0;
}

.category-btn:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
}

.category-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.category-icon {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  margin-bottom: 15px;
  font-size: 24px;
  font-weight: bold;
}

.category-name {
  font-weight: bold;
  font-size: 16px;
}

/* クイズ部分 */
.quiz {
  background: linear-gradient(135deg, #3B82F6 0%, #1E40AF 100%);
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  color: white;
  position: relative;
  overflow: hidden;
}

.quiz::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background:
    linear-gradient(90deg, transparent 19%, rgba(147, 197, 253, 0.2) 20%, transparent 21%),
    linear-gradient(90deg, transparent 39%, rgba(147, 197, 253, 0.2) 40%, transparent 41%),
    linear-gradient(90deg, transparent 59%, rgba(147, 197, 253, 0.2) 60%, transparent 61%),
    linear-gradient(90deg, transparent 79%, rgba(147, 197, 253, 0.2) 80%, transparent 81%),
    linear-gradient(0deg, transparent 19%, rgba(147, 197, 253, 0.2) 20%, transparent 21%),
    linear-gradient(0deg, transparent 39%, rgba(147, 197, 253, 0.2) 40%, transparent 41%),
    linear-gradient(0deg, transparent 59%, rgba(147, 197, 253, 0.2) 60%, transparent 61%),
    linear-gradient(0deg, transparent 79%, rgba(147, 197, 253, 0.2) 80%, transparent 81%);
  background-size: 20% 20%;
  z-index: 0;
}

.quiz-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  position: relative;
  z-index: 1;
}

.progress-container {
  flex: 1;
  margin-right: 20px;
}

.progress-label {
  margin-bottom: 5px;
  font-weight: bold;
}

.progress-bar {
  height: 10px;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 5px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: #F97316;
  border-radius: 5px;
  transition: width 0.3s ease;
}

.score-display {
  background-color: rgba(255, 255, 255, 0.1);
  padding: 10px 15px;
  border-radius: 15px;
  text-align: center;
  min-width: 80px;
}

.score-label {
  font-size: 12px;
  opacity: 0.8;
  margin-bottom: 3px;
}

.score-value {
  font-size: 22px;
  font-weight: bold;
  color: #FACC15;
}

/* セッション情報表示 */
.session-info {
  background-color: rgba(255, 255, 255, 0.1);
  padding: 8px 12px;
  border-radius: 10px;
  text-align: center;
  min-width: 100px;
  margin-left: 10px;
}

.session-label {
  font-size: 10px;
  opacity: 0.8;
  margin-bottom: 3px;
}

.session-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.session-used, .session-remaining {
  font-size: 11px;
  opacity: 0.9;
}

.session-used {
  color: #FACC15;
}

.session-remaining {
  color: #10B981;
}

.question-card {
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 15px;
  padding: 25px;
  position: relative;
  z-index: 1;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.question-text {
  margin-bottom: 25px;
}

.question-text h2 {
  font-size: 20px;
  line-height: 1.5;
}

.question-image {
  margin: 20px 0;
  text-align: center;
}

.question-image img {
  max-width: 100%;
  max-height: 400px;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  object-fit: contain;
}

.choices {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

/* 選択肢ボタンのスタイル改善 */
.choice-btn {
  display: flex;
  align-items: center;
  padding: 0;
  background-color: rgba(255, 255, 255, 0.25); /* 背景色を濃くする (0.1→0.25) */
  border: 2px solid rgba(255, 255, 255, 0.4); /* ボーダーをより明確に (0.2→0.4) */
  border-radius: 10px;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s;
  overflow: hidden;
  margin-bottom: 5px; /* 選択肢間のスペースを追加 */
}

.choice-btn:hover:not([disabled]) {
  background-color: rgba(255, 255, 255, 0.35); /* ホバー時の背景を濃く (0.2→0.35) */
  transform: translateX(5px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2); /* ホバー時に影を追加 */
}

.choice-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 50px;
  height: 50px;
  background-color: rgba(255, 255, 255, 0.3); /* 番号背景を濃く (0.15→0.3) */
  color: white; /* 番号の色を明確に */
  font-weight: bold;
  font-size: 18px;
  flex-shrink: 0;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3); /* テキストに影を追加 */
}

.choice-text {
  flex: 1;
  padding: 15px;
  font-size: 16px;
  color: white; /* テキスト色を明確に */
  font-weight: 500; /* やや太く */
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2); /* 読みやすさのために影を追加 */
}

.choice-btn.correct {
  background-color: rgba(16, 185, 129, 0.2);
  border-color: #10B981;
}

.choice-btn.incorrect {
  background-color: rgba(239, 68, 68, 0.2);
  border-color: #EF4444;
}

.feedback {
  margin: 20px 0;
  padding: 15px;
  border-radius: 10px;
  display: flex;
  align-items: center;
}

.correct-feedback, .incorrect-feedback {
  display: flex;
  align-items: center;
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 15px;
  width: 100%;
}

.correct-feedback {
  border-left: 5px solid #10B981;
}

.incorrect-feedback {
  border-left: 5px solid #EF4444;
}

.feedback-icon {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  font-weight: bold;
  font-size: 16px;
}

.correct-feedback .feedback-icon {
  background-color: #10B981;
  color: white;
}

.incorrect-feedback .feedback-icon {
  background-color: #EF4444;
  color: white;
}

.next-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 15px;
  background: linear-gradient(to bottom, #F97316, #EA580C);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
  margin-top: 20px;
}

.next-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 5px;
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 2.5px 2.5px 0 0;
}

.next-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
}

.next-icon {
  margin-left: 10px;
  font-size: 14px;
}

/* エラーメッセージ */
.error-message {
  background-color: rgba(239, 68, 68, 0.1);
  border-left: 5px solid #EF4444;
  padding: 20px;
  border-radius: 10px;
  margin: 30px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.error-icon {
  width: 40px;
  height: 40px;
  background-color: #EF4444;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 20px;
  margin-bottom: 15px;
}

.error-message p {
  margin-bottom: 15px;
  text-align: center;
  color: #EF4444;
  font-weight: bold;
}

.reset-btn {
  background: linear-gradient(to bottom, #3B82F6, #2563EB);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 20px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
}

.reset-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 10px rgba(0, 0, 0, 0.2);
}

/* クイズ結果 */
.quiz-results {
  background: linear-gradient(135deg, #3B82F6 0%, #1E40AF 100%);
  border-radius: 20px;
  padding: 30px;
  color: white;
  position: relative;
  overflow: hidden;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

.quiz-results::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background:
    linear-gradient(90deg, transparent 19%, rgba(147, 197, 253, 0.2) 20%, transparent 21%),
    linear-gradient(90deg, transparent 39%, rgba(147, 197, 253, 0.2) 40%, transparent 41%),
    linear-gradient(90deg, transparent 59%, rgba(147, 197, 253, 0.2) 60%, transparent 61%),
    linear-gradient(90deg, transparent 79%, rgba(147, 197, 253, 0.2) 80%, transparent 81%),
    linear-gradient(0deg, transparent 19%, rgba(147, 197, 253, 0.2) 20%, transparent 21%),
    linear-gradient(0deg, transparent 39%, rgba(147, 197, 253, 0.2) 40%, transparent 41%),
    linear-gradient(0deg, transparent 59%, rgba(147, 197, 253, 0.2) 60%, transparent 61%),
    linear-gradient(0deg, transparent 79%, rgba(147, 197, 253, 0.2) 80%, transparent 81%);
  background-size: 20% 20%;
  z-index: 0;
}

.quiz-results h2 {
  text-align: center;
  margin-bottom: 20px;
  position: relative;
  font-size: 28px;
  z-index: 1;
}

.results-summary {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin: 20px 0;
  position: relative;
  z-index: 1;
}

.result-item {
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  padding: 20px;
  text-align: center;
  min-width: 120px;
}

.result-label {
  font-size: 14px;
  opacity: 0.8;
  margin-bottom: 5px;
}

.result-value {
  font-size: 24px;
  font-weight: bold;
}

.result-value.percentage {
  color: #FACC15;
}

.result-chart {
  margin: 30px 0;
  position: relative;
  z-index: 1;
}

.chart-bar {
  height: 25px;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 12.5px;
  overflow: hidden;
  margin-bottom: 10px;
}

.chart-fill {
  height: 100%;
  background: linear-gradient(to right, #10B981, #FACC15);
  border-radius: 12.5px;
  transition: width 1s ease-out;
}

.chart-scale {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  opacity: 0.7;
}

.guest-notice {
  background-color: rgba(249, 115, 22, 0.2);
  border-left: 5px solid #F97316;
  padding: 15px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  position: relative;
  z-index: 1;
  margin: 20px 0;
}

.notice-icon {
  margin-right: 10px;
  font-size: 20px;
}

.guest-notice a {
  color: #FACC15;
  text-decoration: none;
  font-weight: bold;
  margin: 0 5px;
}

.guest-notice a:hover {
  text-decoration: underline;
}

.answers-review {
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 15px;
  padding: 20px;
  margin: 30px 0;
  position: relative;
  z-index: 1;
}

.answers-review h3 {
  margin-bottom: 20px;
  font-size: 20px;
  position: relative;
  display: inline-block;
}

.answers-review h3::after {
  content: '';
  position: absolute;
  bottom: -5px;
  left: 0;
  width: 100%;
  height: 2px;
  background-color: #F97316;
}

.answers-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.answer-item {
  display: flex;
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  overflow: hidden;
}

.answer-number {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  background-color: rgba(255, 255, 255, 0.15);
  font-size: 16px;
}

.answer-content {
  flex: 1;
  padding: 15px;
}

.answer-item.correct-answer {
  border-left: 4px solid #10B981;
}

.answer-item.incorrect-answer {
  border-left: 4px solid #EF4444;
}

.question-text {
  font-weight: bold;
  margin-bottom: 10px;
}

.answer-details {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.user-answer, .correct-text {
  display: flex;
  align-items: center;
  font-size: 14px;
}

.answer-label {
  margin-right: 5px;
  opacity: 0.7;
  min-width: 80px;
}

.result-icon {
  margin-left: 10px;
  font-weight: bold;
}

/* Quiz actions container */
.quiz-actions {
  display: flex;
  gap: 15px;
  flex-direction: column;
  position: relative;
  z-index: 1;
}

.retake-btn, .restart-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 15px;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
}

.retake-btn {
  background: linear-gradient(to bottom, #3B82F6, #2563EB);
}

.restart-btn {
  background: linear-gradient(to bottom, #10B981, #059669);
}

.retake-btn::before, .restart-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 5px;
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 2.5px 2.5px 0 0;
}

.retake-btn:hover {
  background: linear-gradient(to bottom, #2563EB, #1D4ED8);
  transform: translateY(-3px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
}

.restart-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
}

.button-icon {
  margin-right: 10px;
  font-size: 18px;
}

/* レスポンシブデザイン */
@media (max-width: 768px) {
  .categories {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  }
  
  .results-summary {
    flex-direction: column;
    gap: 15px;
  }
  
  .answer-item {
    flex-direction: column;
  }
  
  .answer-number {
    width: 100%;
    height: 30px;
  }
  
  .quiz-actions {
    gap: 10px;
  }
}

@media (max-width: 480px) {
  .quiz-container {
    padding: 10px;
  }
  
  .category-selection, .quiz, .quiz-results {
    padding: 20px;
  }
  
  .categories {
    grid-template-columns: 1fr;
  }
  
  .quiz-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .progress-container {
    width: 100%;
    margin-right: 0;
    margin-bottom: 10px;
  }
  
  .score-display {
    align-self: flex-end;
  }
  
  .choice-btn {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .choice-number {
    width: 100%;
    height: 30px;
  }
}
</style>