<template>
  <div class="quiz-container">
    <div v-if="loading" class="loading">
      <p>読み込み中...</p>
    </div>
    
    <div v-else>
      <div class="category-selection" v-if="!currentQuestion">
        <h2>カテゴリを選択してください</h2>
        <div class="categories">
          <button 
            v-for="category in categories" 
            :key="category.id"
            @click="selectCategory(category.id)"
            class="category-btn"
          >
            {{ category.name }}
          </button>
        </div>
      </div>
      
      <div class="quiz" v-else>
        <div class="question-counter">質問 {{ questionIndex + 1 }} / {{ questions.length }}</div>
        <div class="score">スコア: {{ score }}</div>
        
        <div class="question">
          <h2>{{ currentQuestion.text }}</h2>
          
          <div class="choices">
            <button 
              v-for="choice in currentQuestion.choices" 
              :key="choice.id"
              @click="checkAnswer(choice)"
              :disabled="answered"
              :class="{ 
                'choice-btn': true,
                'correct': answered && choice.is_correct,
                'incorrect': answered && selectedChoice === choice && !choice.is_correct 
              }"
            >
              {{ choice.text }}
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
      
      <div class="results" v-if="quizCompleted">
        <h2>クイズ完了!</h2>
        <p>あなたのスコア: {{ score }} / {{ questions.length }}</p>
        <p>正答率: {{ Math.round((score / questions.length) * 100) }}%</p>
        <button @click="resetQuiz" class="reset-btn">もう一度挑戦する</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'QuizComponent',
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
      quizCompleted: false
    };
  },
  computed: {
    currentQuestion() {
      if (this.questions.length === 0) {
        return null;
      }
      return this.questionIndex < this.questions.length ? this.questions[this.questionIndex] : null;
    },
    correctAnswerText() {
      if (!this.currentQuestion) return '';
      const correctChoice = this.currentQuestion.choices.find(choice => choice.is_correct);
      return correctChoice ? correctChoice.text : '';
    },
    isLastQuestion() {
      return this.questionIndex === this.questions.length - 1;
    }
  },
  methods: {
    async fetchCategories() {
      try {
        const response = await axios.get('http://localhost:8000/api/categories/');
        this.categories = response.data;
        this.loading = false;
      } catch (error) {
        console.error('カテゴリの取得に失敗しました:', error);
        this.loading = false;
      }
    },
    async selectCategory(categoryId) {
      this.loading = true;
      try {
        const response = await axios.get(`http://localhost:8000/api/questions/?category=${categoryId}`);
        this.questions = this.shuffleArray(response.data);
        this.questionIndex = 0;
        this.score = 0;
        this.answered = false;
        this.quizCompleted = false;
        this.loading = false;
      } catch (error) {
        console.error('質問の取得に失敗しました:', error);
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
      this.answered = true;
      this.selectedChoice = choice;
      this.correct = choice.is_correct;
      
      if (choice.is_correct) {
        this.score++;
      }
       // 回答を記録
      this.allAnswers.push({
        question: this.currentQuestion,
        selectedChoice: choice,
        isCorrect: choice.is_correct
      });
    },
    nextQuestion() {
      if (this.isLastQuestion) {
      this.quizCompleted = true;
      // ユーザーがログインしている場合、結果を保存
      if (this.$store.getters['auth/isAuthenticated']) {
        this.saveQuizResult();
      }
    } else {
      this.questionIndex++;
      this.answered = false;
      this.selectedChoice = null;
    }
    },
    resetQuiz() {
      this.questions = [];
      this.questionIndex = 0;
      this.score = 0;
      this.answered = false;
      this.selectedChoice = null;
      this.quizCompleted = false;
      this.fetchCategories();
    },
    async saveQuizResult() {
      if (!this.quizCompleted) return;
      
      try {
        // レスポンスデータの準備
        const responseData = this.allAnswers.map(answer => ({
          question_id: answer.question.id,
          selected_choice_id: answer.selectedChoice.id,
          is_correct: answer.isCorrect
        }));
        
        // 結果を保存
        await axios.post('http://localhost:8000/api/quiz/save-result/', {
          category_id: this.selectedCategory.id,
          score: this.score,
          total_questions: this.questions.length,
          responses: responseData
        });
        
        this.$toast.success('クイズ結果が保存されました！');
      } catch (error) {
        console.error('結果の保存に失敗しました:', error);
        this.$toast.error('結果の保存に失敗しました');
      }
    },
  },
  created() {
    this.fetchCategories();
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
</style>