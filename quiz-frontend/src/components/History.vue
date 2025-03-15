<template>
  <div class="history-container">
    <h2>クイズ履歴</h2>
    
    <div v-if="loading" class="loading">
      <p>読み込み中...</p>
    </div>
    
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
    </div>
    
    <div v-else-if="quizHistory && quizHistory.length > 0" class="history-list">
      <div 
        v-for="(attempt, index) in quizHistory" 
        :key="attempt?.id || index" 
        class="history-item"
      >
        <div class="history-header" @click="toggleDetails(index)">
          <div class="history-basic-info">
            <span class="category">{{ attempt?.category_name || 'カテゴリなし' }}</span>
            <span class="score">スコア: {{ attempt?.score || 0 }}/{{ attempt?.total_questions || 0 }}</span>
            <span class="percentage">{{ Math.round(attempt?.percentage || 0) }}%</span>
            <span class="date">{{ formatDate(attempt?.created_at) }}</span>
          </div>
          <div class="toggle-icon">{{ expandedItems[index] ? '▼' : '▶' }}</div>
        </div>
        
        <div v-if="expandedItems[index]" class="history-details">
          <!-- 詳細内容 -->
          <div v-if="attempt?.responses && attempt.responses.length > 0">
            <div 
              v-for="(response, rIndex) in attempt.responses" 
              :key="response?.id || `response-${rIndex}`" 
              class="response-item"
            >
              <p class="question">{{ response?.question_text || '質問なし' }}</p>
              <p :class="['answer', response?.is_correct ? 'correct' : 'incorrect']">
                回答: {{ response?.selected_choice_text || '選択肢なし' }}
                <span v-if="response?.is_correct">✓</span>
                <span v-else>✗</span>
              </p>
            </div>
          </div>
          <div v-else class="no-details">
            詳細情報はありません
          </div>
        </div>
      </div>
    </div>
    
    <div v-else class="no-history">
      <p>履歴がありません。クイズに挑戦してみましょう！</p>
    </div>
  </div>
</template>

<script>
import api from '../utils/api';

export default {
  data() {
    return {
      loading: true,
      quizHistory: [],
      error: null,
      expandedItems: {}
    };
  },
  mounted() {
    this.fetchHistory();
  },
  methods: {
    async fetchHistory() {
      try {
        this.loading = true;
        console.log('履歴取得開始');
        const response = await api.get('/api/quiz/history/');
        console.log('履歴取得成功:', response.data);
        
        // レスポンスがページネーション形式かどうか確認
        let historyData;
        if (response.data && Array.isArray(response.data.results)) {
          // ページネーション形式の場合
          historyData = response.data.results;
          console.log('ページネーションデータから履歴を取得:', historyData);
        } else if (Array.isArray(response.data)) {
          // 単純な配列の場合
          historyData = response.data;
        } else {
          console.error('予期しない履歴データ形式:', response.data);
          this.error = '履歴データの形式が正しくありません';
          this.loading = false;
          return;
        }
        
        // データをバリデーション
        this.quizHistory = historyData.map((item, index) => {
          // nullチェックして安全なオブジェクトを返す
          if (!item) return {
            id: `empty-${index}`,
            score: 0,
            total_questions: 0,
            percentage: 0,
            category_name: 'カテゴリなし',
            created_at: new Date().toISOString()
          };
          
          // 各フィールドが存在することを確認
          const safeItem = {
            ...item,
            id: item.id || `history-${index}`,
            score: item.score || 0,
            total_questions: item.total_questions || 0,
            percentage: item.percentage || 0,
            category_name: item.category_name || 'カテゴリなし',
            created_at: item.created_at || new Date().toISOString()
          };
          
          // レスポンスデータがある場合の安全チェック
          if (item.responses) {
            safeItem.responses = item.responses.map((resp, rIndex) => ({
              ...resp,
              id: resp?.id || `resp-${index}-${rIndex}`,
              question_text: resp?.question_text || '質問なし',
              selected_choice_text: resp?.selected_choice_text || '選択肢なし',
              is_correct: !!resp?.is_correct
            }));
          } else {
            safeItem.responses = [];
          }
          
          return safeItem;
        });
        
        console.log('履歴データ設定完了:', this.quizHistory);
        this.loading = false;
      } catch (error) {
        console.error('履歴の取得に失敗しました:', error);
        if (error.response && error.response.status === 401) {
          this.error = 'ログインが必要です。再度ログインしてください。';
        } else {
          this.error = '履歴の取得に失敗しました。';
        }
        this.loading = false;
      }
    },
    formatDate(dateString) {
      if (!dateString) {
        return '日付なし'; // 日付がnullやundefinedの場合
      }
      
      try {
        const date = new Date(dateString);
        
        // 無効な日付かどうかチェック
        if (isNaN(date.getTime())) {
          return '無効な日付';
        }
        
        // 日付のフォーマット（年月日と時間）
        return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日 ${date.getHours()}:${date.getMinutes().toString().padStart(2, '0')}`;
      } catch (error) {
        console.error('日付の変換エラー:', error, dateString);
        return '無効な日付';
      }
    },
    toggleDetails(itemId) {
      this.expandedItems[itemId] = !this.expandedItems[itemId];
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