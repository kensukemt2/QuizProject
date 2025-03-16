<template>
  <div class="quiz-container">
    <div v-if="isGuestMode" class="guest-mode-banner">
      <span>👤 ゲストモードでクイズを実行中</span>
      <router-link to="/login" class="login-link">ログインして結果を保存する</router-link>
    </div>
    <div v-if="loading" class="loading">
      <p>読み込み中...</p>
    </div>
    
    <div v-else>
      <div v-if="isGuestMode" class="guest-mode-indicator">
        ゲストモードでプレイ中
        <router-link to="/login" class="login-link">ログイン</router-link>
      </div>
      <div class="category-selection" v-if="!currentQuestion">
        <h2>カテゴリを選択してください</h2>
        <div class="categories">
          <button 
            v-for="(category, index) in categories" 
            :key="`cat-${index}`"
            @click="category ? selectCategory(category.id) : null"
            class="category-btn"
            :disabled="!category"
          >
            {{ category?.name || 'カテゴリなし' }}
          </button>
        </div>
      </div>
      
      <div class="quiz" v-else-if="currentQuestion">
        <div class="question-counter">質問 {{ questionIndex + 1 }} / {{ questions.length }}</div>
        <div class="score">スコア: {{ score }}</div>
        
        <div class="question">
          <h2>{{ currentQuestion.text }}</h2>
          
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
              {{ choice?.text || '選択肢' }}
            </button>
          </div>
          
          <div class="feedback" v-if="answered">
            <p v-if="correct" class="correct-feedback">正解!</p>
            <p v-else class="incorrect-feedback">
              不正解! 正解は「{{ correctAnswerText }}」でした。
            </p>
          </div>
          
          <button 
            v-if="answered" 
            @click="nextQuestion" 
            class="next-btn"
          >
            {{ isLastQuestion ? '結果を見る' : '次の問題' }}
          </button>
        </div>
      </div>

      <div v-else-if="error" class="error-message">
        <p>{{ error }}</p>
        <button @click="resetQuiz" class="reset-btn">カテゴリー選択に戻る</button>
      </div>
      
      <div class="quiz-results" v-if="quizCompleted && questions.length > 0">
        <h2>クイズ結果</h2>
        <p v-if="isGuestMode" class="guest-notice">
          ゲストモードです。結果を保存するには
          <router-link to="/login">ログイン</router-link>
          してください。
        </p>
        <p>スコア: {{ score }}/{{ questions.length }}</p>
        <p>正答率: {{ Math.round((score / questions.length) * 100) }}%</p>
        
        <div class="answers-review" v-if="allAnswers && allAnswers.length > 0">
          <h3>回答レビュー:</h3>
          <template v-for="(answer, index) in allAnswers" :key="'answer-' + index">
            <div v-if="answer && answer.question" class="answer-item">
              <p class="question-text">{{ answer.question?.text || '質問' }}</p>
              <p :class="['answer-text', answer.correct ? 'correct' : 'incorrect']">
                あなたの回答: {{ answer.selectedChoice?.text || '未回答' }}
                <span class="result">{{ answer.correct ? '✓' : '✗' }}</span>
              </p>
              <p v-if="!answer.correct" class="correct-answer">
                正解: {{ answer.correctChoice?.text || '不明' }}
              </p>
            </div>
          </template>
        </div>
        
        <button @click="resetQuiz" class="restart-btn">新しいクイズを始める</button>
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
    }
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
    }
  },
  methods: {
    async fetchCategories() {
      try {
        this.loading = true;
        console.log('カテゴリ取得開始');
        const response = await axios.get('http://localhost:8000/api/categories/');
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
    
      this.loading = true;
      this.error = null;
      
      try {
        // カテゴリ情報を保存
        const selectedCategory = this.categories.find(c => c.id === categoryId);
        
        if (!selectedCategory) {
          console.error('選択したカテゴリが見つかりません:', categoryId);
          this.error = 'カテゴリが見つかりません';
          this.loading = false;
          return;
        }
        
        this.selectedCategory = selectedCategory;
        this.questions = [];  // クリアして古いデータが表示されないようにする
        
        await this.fetchQuestions(categoryId);
      } catch (error) {
        console.error('質問の取得に失敗しました:', error);
        this.error = '質問の取得に失敗しました';
        this.loading = false;
      }
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
        
        // 正しいURLを構築
        const url = `http://localhost:8000/api/questions/?category=${categoryIdNum}`;
        console.log('リクエスト先URL:', url);
        
        const response = await axios.get(url);
        console.log('API応答データ:', response.data);
        
        // レスポンスがページネーション形式かどうか確認
        let questionsData;
        if (response.data && Array.isArray(response.data.results)) {
          // ページネーション形式の場合
          questionsData = response.data.results;
          console.log('ページネーションデータから質問を取得:', questionsData);
        } else if (Array.isArray(response.data)) {
          // 単純な配列の場合
          questionsData = response.data;
          console.log('ページネーションデータから質問を取得:', questionsData);
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
        
        this.questions = this.shuffleArray(validatedQuestions);
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
      
      // カテゴリデータがない場合は再取得
      if (!this.categories || this.categories.length === 0) {
        this.fetchCategories();
      } else {
        this.loading = false;
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
      
      // ゲストモード状態の取得
      this.isGuestMode = this.$store.getters['quiz/isGuestMode'] || 
                        localStorage.getItem('quizMode') === 'guest' ||
                        this.$route.query.mode === 'guest';
                        
      console.log('クイズ初期化完了:', {
        isGuestMode: this.isGuestMode,
        isAuthenticated: this.isAuthenticated
      });
      
      // カテゴリを取得
      this.fetchCategories();
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
}

.category-selection, .quiz, .results {
  background-color: #f5f5f5;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.categories {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 20px;
}

.category-btn {
  padding: 10px 15px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.category-btn:hover {
  background-color: #45a049;
}

.question-counter, .score {
  margin-bottom: 10px;
  font-weight: bold;
}

.question {
  margin-top: 20px;
}

.choices {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 20px;
}

.choice-btn {
  padding: 15px;
  background-color: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 5px;
  cursor: pointer;
  text-align: left;
  transition: background-color 0.3s;
}

.choice-btn:hover:not([disabled]) {
  background-color: #e0e0e0;
}

.choice-btn.correct {
  background-color: #4CAF50;
  color: white;
}

.choice-btn.incorrect {
  background-color: #f44336;
  color: white;
}

.feedback {
  margin-top: 20px;
  padding: 10px;
  border-radius: 5px;
}

.correct-feedback {
  color: #4CAF50;
  font-weight: bold;
}

.incorrect-feedback {
  color: #f44336;
  font-weight: bold;
}

.next-btn, .reset-btn {
  margin-top: 20px;
  padding: 10px 15px;
  background-color: #2196F3;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.next-btn:hover, .reset-btn:hover {
  background-color: #0b7dda;
}

.results {
  text-align: center;
  margin-top: 20px;
}

.loading {
  text-align: center;
  margin-top: 50px;
}

.guest-mode-indicator {
  background-color: #fff3cd;
  color: #856404;
  padding: 8px 12px;
  margin-bottom: 15px;
  border-radius: 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.login-link {
  color: #0056b3;
  text-decoration: underline;
  font-weight: bold;
}

.guest-notice {
  background-color: #f8d7da;
  color: #721c24;
  padding: 10px;
  border-radius: 4px;
  margin: 10px 0;
}

.guest-mode-banner {
  background-color: #fff3cd;
  color: #856404;
  border: 1px solid #ffeeba;
  padding: 10px 15px;
  margin-bottom: 20px;
  border-radius: 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}
</style>