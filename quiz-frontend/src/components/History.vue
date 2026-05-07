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
  name: 'QuizHistory',
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
        const response = await api.get('/api/quiz/history/');
        
        // レスポンスがページネーション形式かどうか確認
        let historyData;
        if (response.data && Array.isArray(response.data.results)) {
          // ページネーション形式の場合
          historyData = response.data.results;
        } else if (Array.isArray(response.data)) {
          // 単純な配列の場合
          historyData = response.data;
        } else {
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
  padding: 32px 20px;
  color: #f5f0e8;
}

.history-container h2 {
  font-size: 24px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #f5f0e8;
  text-shadow: 3px 3px 0 #e8001c;
  margin-bottom: 28px;
  padding-bottom: 12px;
  border-bottom: 1px solid #1a1a1a;
  position: relative;
}
.history-container h2::after {
  content: '';
  position: absolute;
  bottom: -1px; left: 0;
  width: 80px; height: 2px;
  background: #e8001c;
}

/* ローディング */
.loading {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; min-height: 200px; gap: 16px; color: #555;
}
.loading-spinner {
  width: 36px; height: 36px;
  border: 3px solid #1a1a1a;
  border-top: 3px solid #e8001c;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.error {
  background: #0e0e12;
  border-left: 4px solid #ef4444;
  padding: 16px 20px;
  color: #ef4444;
  font-size: 13px;
}
.retry-btn {
  background: transparent;
  border: 1px solid #333;
  color: #555;
  padding: 6px 16px;
  font-size: 11px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  cursor: pointer;
  margin-top: 10px;
  transition: all 0.15s;
  clip-path: polygon(0 0, 100% 0, 94% 100%, 0 100%);
}
.retry-btn:hover { border-color: #e8001c; color: #e8001c; }

/* 履歴リスト */
.history-list { display: flex; flex-direction: column; gap: 2px; }

.history-item {
  background: #0e0e12;
  border: 1px solid #1a1a1a;
  overflow: hidden;
  transition: border-color 0.15s;
}
.history-item:hover { border-color: rgba(255,255,255,0.08); }

.history-header {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 18px;
  cursor: pointer;
  position: relative;
}

.history-header::before {
  content: '';
  position: absolute;
  left: 0; top: 0; bottom: 0;
  width: 3px;
  background: #e8001c;
  transform: scaleY(0);
  transform-origin: bottom;
  transition: transform 0.2s;
}
.history-item:hover .history-header::before { transform: scaleY(1); }

.history-basic-info {
  display: flex;
  flex: 1;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.category {
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.04em;
  color: #f5f0e8;
  min-width: 120px;
}

.score-container {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
}
.score {
  font-size: 12px;
  color: #555;
  letter-spacing: 0.05em;
  white-space: nowrap;
}
.progress-bar {
  height: 3px;
  background: #1a1a1a;
  flex: 1;
  min-width: 60px;
  position: relative;
}
.progress-fill {
  height: 100%;
  background: #e8001c;
  transition: width 0.4s;
}
.percentage {
  font-size: 13px;
  font-weight: 700;
  color: #e8001c;
  letter-spacing: 0.05em;
  white-space: nowrap;
  font-family: 'Reggae One', sans-serif;
}

.date {
  font-size: 11px;
  color: #333;
  letter-spacing: 0.05em;
  white-space: nowrap;
}

.toggle-icon {
  font-size: 12px;
  color: #444;
  flex-shrink: 0;
  transition: color 0.15s;
}
.history-item:hover .toggle-icon { color: #e8001c; }

/* 詳細 */
.history-details {
  border-top: 1px solid #1a1a1a;
  padding: 16px 18px;
  background: rgba(255,255,255,0.01);
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 2px;
  margin-bottom: 16px;
}
.detail-item {
  background: #0a0a0e;
  border: 1px solid #1a1a1a;
  border-top: 2px solid #333;
  padding: 12px 14px;
  clip-path: polygon(0 0, 100% 0, 95% 100%, 0 100%);
}
.detail-label { font-size: 10px; letter-spacing: 0.1em; color: #333; text-transform: uppercase; margin-bottom: 4px; }
.detail-value { font-size: 18px; color: #f5f0e8; line-height: 1; }
.detail-value.highlight { color: #e8001c; }

/* 回答詳細 */
.answers-section h4 {
  font-size: 12px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #444;
  margin-bottom: 10px;
  padding-bottom: 6px;
  border-bottom: 1px solid #1a1a1a;
}
.answer-list { display: flex; flex-direction: column; gap: 4px; }
.answer-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  background: rgba(255,255,255,0.02);
  font-size: 12px;
  color: #555;
}
.answer-row.correct { border-left: 2px solid #22c55e; }
.answer-row.incorrect { border-left: 2px solid #ef4444; }
.answer-num {
  width: 20px; height: 20px;
  display: flex; align-items: center; justify-content: center;
  font-size: 10px; font-weight: 700;
  background: rgba(255,255,255,0.04);
  flex-shrink: 0;
  color: #444;
}
.answer-q { flex: 1; color: #888; }
.answer-result { font-size: 11px; font-weight: 700; flex-shrink: 0; }
.answer-row.correct .answer-result { color: #22c55e; }
.answer-row.incorrect .answer-result { color: #ef4444; }

/* 空状態 */
.no-history {
  background: #0e0e12;
  border: 1px solid #1a1a1a;
  border-left: 4px solid #333;
  padding: 40px 24px;
  text-align: center;
  color: #444;
}
.no-history p { font-size: 14px; margin-bottom: 16px; letter-spacing: 0.05em; }
.start-quiz-btn {
  display: inline-block;
  padding: 10px 24px;
  background: #e8001c;
  color: #fff;
  text-decoration: none;
  font-size: 12px;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  clip-path: polygon(0 0, 100% 0, 94% 100%, 0 100%);
  box-shadow: 4px 4px 0 rgba(232,0,28,0.3);
  transition: all 0.15s;
}
.start-quiz-btn:hover { background: #ff1a35; transform: translate(-2px,-2px); }

@media (max-width: 600px) {
  .history-basic-info { flex-direction: column; align-items: flex-start; gap: 8px; }
  .score-container { width: 100%; }
}
</style>
