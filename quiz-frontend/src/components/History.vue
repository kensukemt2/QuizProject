<template>
    <div class="history-container">
      <h2>クイズ履歴</h2>
      
      <div v-if="loading" class="loading">
        <p>読み込み中...</p>
      </div>
      
      <div v-else-if="quizHistory.length === 0" class="no-history">
        <p>クイズ履歴がありません。クイズに挑戦して記録を残しましょう！</p>
        <router-link to="/quiz" class="start-quiz-btn">クイズを始める</router-link>
      </div>
      
      <div v-else class="history-list">
        <div v-for="attempt in quizHistory" :key="attempt.id" class="history-item">
          <div class="history-header">
            <h3>{{ attempt.category_name }}</h3>
            <span class="date">{{ formatDate(attempt.created_at) }}</span>
          </div>
          
          <div class="score-info">
            <div class="score">
              <strong>スコア:</strong> {{ attempt.score }}/{{ attempt.total_questions }}
            </div>
            <div class="percentage">
              <strong>正答率:</strong> {{ Math.round(attempt.percentage) }}%
            </div>
          </div>
          
          <button @click="toggleDetails(attempt.id)" class="details-btn">
            {{ expandedAttempt === attempt.id ? '詳細を隠す' : '詳細を表示' }}
          </button>
          
          <div v-if="expandedAttempt === attempt.id" class="details">
            <h4>回答詳細:</h4>
            <ul class="responses-list">
              <li 
                v-for="response in attempt.responses" 
                :key="response.id"
                :class="{ 'correct': response.is_correct, 'incorrect': !response.is_correct }"
              >
                <div class="question-text">{{ response.question_text }}</div>
                <div class="answer-text">
                  回答: {{ response.selected_choice_text }}
                  <span class="result-icon">{{ response.is_correct ? '✓' : '✗' }}</span>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    name: 'HistoryComponent',
    data() {
      return {
        quizHistory: [],
        loading: true,
        expandedAttempt: null
      };
    },
    created() {
      this.fetchHistory();
    },
    methods: {
      async fetchHistory() {
        try {
          const response = await axios.get('http://localhost:8000/api/quiz/history/');
          this.quizHistory = response.data;
          this.loading = false;
        } catch (error) {
          console.error('履歴の取得に失敗しました:', error);
          this.loading = false;
        }
      },
      formatDate(dateString) {
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('ja-JP', {
          year: 'numeric',
          month: 'long',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        }).format(date);
      },
      toggleDetails(attemptId) {
        if (this.expandedAttempt === attemptId) {
          this.expandedAttempt = null;
        } else {
          this.expandedAttempt = attemptId;
        }
      }
    }
  };
  </script>
  
  <style scoped>
  .history-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
  }
  
  h2 {
    text-align: center;
    margin-bottom: 20px;
  }
  
  .loading, .no-history {
    text-align: center;
    margin-top: 50px;
  }
  
  .start-quiz-btn {
    display: inline-block;
    margin-top: 20px;
    padding: 10px 15px;
    background-color: #4CAF50;
    color: white;
    text-decoration: none;
    border-radius: 4px;
  }
  
  .history-item {
    background-color: #f5f5f5;
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 15px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  }
  
  .history-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
  }
  
  .history-header h3 {
    margin: 0;
  }
  
  .date {
    color: #777;
    font-size: 0.9em;
  }
  
  .score-info {
    display: flex;
    margin-bottom: 15px;
  }
  
  .score, .percentage {
    margin-right: 20px;
  }
  
  .details-btn {
    background-color: #2196F3;
    color: white;
    border: none;
    padding: 8px 12px;
    border-radius: 4px;
    cursor: pointer;
  }
  
  .details {
    margin-top: 15px;
    border-top: 1px solid #ddd;
    padding-top: 15px;
  }
  
  .responses-list {
    list-style-type: none;
    padding: 0;
  }
  
  .responses-list li {
    border-left: 4px solid #ddd;
    padding: 10px;
    margin-bottom: 10px;
  }
  
  .responses-list li.correct {
    border-left-color: #4CAF50;
  }
  
  .responses-list li.incorrect {
    border-left-color: #f44336;
  }
  
  .question-text {
    font-weight: bold;
    margin-bottom: 5px;
  }
  
  .answer-text {
    display: flex;
    justify-content: space-between;
  }
  
  .result-icon {
    font-weight: bold;
  }
  
  .correct .result-icon {
    color: #4CAF50;
  }
  
  .incorrect .result-icon {
    color: #f44336;
  }
  </style>