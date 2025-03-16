<template>
  <div class="history-container">
    <h2>クイズ履歴</h2>
    
    <div v-if="loading" class="loading">
      <p>読み込み中...</p>
      <div class="loading-spinner"></div>
    </div>
    
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button class="retry-btn" @click="fetchHistory">再試行</button>
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
            <div class="score-container">
              <span class="score">スコア: {{ attempt?.score || 0 }}/{{ attempt?.total_questions || 0 }}</span>
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: `${attempt?.percentage || 0}%` }"></div>
              </div>
              <span class="percentage">{{ Math.round(attempt?.percentage || 0) }}%</span>
            </div>
            <span class="date">{{ formatDate(attempt?.created_at) }}</span>
          </div>
          <div class="toggle-icon">{{ expandedItems[index] ? '▼' : '▶' }}</div>
        </div>
        
        <div v-if="expandedItems[index]" class="history-details">
          <!-- 詳細内容 -->
          <div v-if="attempt?.responses && attempt.responses.length > 0" class="responses-list">
            <div 
              v-for="(response, rIndex) in attempt.responses" 
              :key="response?.id || `response-${rIndex}`" 
              class="response-item"
              :class="{ 'correct': response?.is_correct, 'incorrect': !response?.is_correct }"
            >
              <p class="question">{{ response?.question_text || '質問なし' }}</p>
              <p class="answer">
                <span class="answer-label">回答:</span> 
                {{ response?.selected_choice_text || '選択肢なし' }}
                <span v-if="response?.is_correct" class="result-icon correct">✓</span>
                <span v-else class="result-icon incorrect">✗</span>
              </p>
            </div>
          </div>
          <div v-else class="no-details">
            <p>詳細情報はありません</p>
            <div class="magic-icon">✧</div>
          </div>
        </div>
      </div>
    </div>
    
    <div v-else class="no-history">
      <div class="character">
        <div class="character-face"></div>
        <div class="character-eye left"></div>
        <div class="character-eye right"></div>
        <div class="character-mouth"></div>
      </div>
      <p>履歴がありません。クイズに挑戦してみましょう！</p>
      <button class="start-quiz-btn" @click="goToQuiz">クイズを始める</button>
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
    },
    goToQuiz() {
      this.$router.push('/quiz');
    }
  }
};
</script>
  
<style scoped>
.history-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  background: linear-gradient(135deg, #3B82F6 0%, #1E40AF 100%);
  border-radius: 20px;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
  color: #FFFFFF;
  position: relative;
  overflow: hidden;
}

/* グリッド線の装飾 */
.history-container::before {
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

/* 装飾的な背景要素 */
.history-container::after {
  content: '';
  position: absolute;
  top: 10%;
  left: 50%;
  transform: translateX(-50%);
  width: 60%;
  height: 60%;
  background: radial-gradient(circle, rgba(147, 197, 253, 0.6) 0%, rgba(30, 64, 175, 0) 70%);
  z-index: 0;
  pointer-events: none;
}

h2 {
  text-align: center;
  margin: 0 0 30px 0;
  font-size: 28px;
  position: relative;
  color: #FFFFFF;
  font-weight: bold;
  z-index: 1;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  padding-bottom: 15px;
}

h2::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 40%;
  width: 20%;
  height: 3px;
  background-color: #F97316;
  border-radius: 1.5px;
}

.loading, .error, .no-history {
  text-align: center;
  margin: 50px 0;
  z-index: 1;
  position: relative;
}

.loading p, .error p, .no-history p {
  font-size: 18px;
  margin-bottom: 20px;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  margin: 20px auto;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top: 4px solid #F97316;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.retry-btn, .start-quiz-btn {
  display: inline-block;
  padding: 10px 22px;
  background: linear-gradient(to bottom, #F97316, #EA580C);
  color: white;
  border: none;
  border-radius: 22.5px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  position: relative;
  overflow: hidden;
  transition: all 0.3s;
}

.retry-btn::before, .start-quiz-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 5px;
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 2.5px 2.5px 0 0;
}

.retry-btn:hover, .start-quiz-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
}

.start-quiz-btn::after {
  content: '▶';
  display: inline-block;
  margin-left: 8px;
  font-size: 12px;
}

.history-list {
  position: relative;
  z-index: 1;
}

.history-item {
  background-color: rgba(59, 130, 246, 0.7);
  border-radius: 15px;
  padding: 15px;
  margin-bottom: 20px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  position: relative;
  overflow: hidden;
  transition: all 0.3s;
  cursor: pointer;
}

.history-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 5px;
  background-color: #F97316;
}

.history-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.25);
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 5px;
}

.history-basic-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.category {
  display: inline-block;
  background-color: #1E40AF;
  padding: 5px 12px;
  border-radius: 15px;
  font-size: 14px;
  font-weight: bold;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.score-container {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 8px 0;
}

.score {
  font-weight: bold;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: #F97316;
  border-radius: 4px;
  transition: width 0.5s;
}

.percentage {
  font-weight: bold;
  color: #FACC15;
  min-width: 45px;
  text-align: right;
}

.date {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
}

.toggle-icon {
  padding: 8px;
  color: #F97316;
  font-size: 16px;
  font-weight: bold;
  transition: transform 0.3s;
}

.history-item:hover .toggle-icon {
  transform: translateX(5px);
}

.history-details {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px dashed rgba(255, 255, 255, 0.3);
  animation: fadeIn 0.5s;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.responses-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.response-item {
  padding: 12px;
  border-radius: 8px;
  background-color: rgba(30, 64, 175, 0.7);
  position: relative;
}

.response-item.correct {
  border-left: 4px solid #10B981;
}

.response-item.incorrect {
  border-left: 4px solid #EF4444;
}

.question {
  font-weight: bold;
  margin-bottom: 8px;
  font-size: 15px;
  line-height: 1.4;
}

.answer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
}

.answer-label {
  font-weight: bold;
  color: rgba(255, 255, 255, 0.8);
  margin-right: 5px;
}

.result-icon {
  font-size: 18px;
  font-weight: bold;
  margin-left: 10px;
}

.result-icon.correct {
  color: #10B981;
}

.result-icon.incorrect {
  color: #EF4444;
}

.no-details {
  text-align: center;
  padding: 20px;
  color: rgba(255, 255, 255, 0.8);
}

.magic-icon {
  font-size: 36px;
  margin: 10px 0;
  color: #F97316;
  animation: sparkle 1.5s infinite;
}

@keyframes sparkle {
  0% { transform: scale(1); opacity: 0.7; }
  50% { transform: scale(1.2); opacity: 1; }
  100% { transform: scale(1); opacity: 0.7; }
}

/* キャラクター装飾 */
.character {
  width: 100px;
  height: 100px;
  margin: 0 auto 20px;
  position: relative;
}

.character-face {
  width: 100px;
  height: 100px;
  background-color: #FACC15;
  border-radius: 50%;
  position: relative;
}

.character-eye {
  width: 20px;
  height: 20px;
  background-color: white;
  border-radius: 50%;
  position: absolute;
  top: 30px;
}

.character-eye::after {
  content: '';
  width: 10px;
  height: 10px;
  background-color: #1E40AF;
  border-radius: 50%;
  position: absolute;
  top: 5px;
  left: 7px;
}

.character-eye.left {
  left: 25px;
}

.character-eye.right {
  right: 25px;
}

.character-mouth {
  position: absolute;
  bottom: 25px;
  left: 50%;
  transform: translateX(-50%);
  width: 30px;
  height: 15px;
  border-bottom: 3px solid #1E40AF;
  border-radius: 0 0 30px 30px;
}

@media (max-width: 600px) {
  .history-container {
    padding: 15px;
    border-radius: 15px;
  }
  
  h2 {
    font-size: 24px;
    margin-bottom: 20px;
  }
  
  .history-item {
    padding: 12px;
  }
  
  .score-container {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .progress-bar {
    width: 100%;
    margin: 5px 0;
  }
}
</style>