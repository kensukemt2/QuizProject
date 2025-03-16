<template>
  <div class="leaderboard-container">
    <h2>リーダーボード</h2>
    
    <div class="filter-section">
      <label for="category-filter">カテゴリーフィルター:</label>
      <div class="select-wrapper">
        <select id="category-filter" v-model="selectedCategory" @change="onCategoryChange">
          <option :value="null">すべてのカテゴリー</option>
          <option v-for="category in categories" :key="category.id" :value="category.id">
            {{ category.name }}
          </option>
        </select>
        <div class="select-arrow">▼</div>
      </div>
    </div>
    
    <div v-if="loading" class="loading">
      <p>読み込み中...</p>
      <div class="loading-spinner"></div>
    </div>
    
    <div v-else-if="error" class="error-message">
      <p>{{ error }}</p>
      <button @click="fetchLeaderboard" class="retry-btn">再試行</button>
    </div>
    
    <div v-else-if="leaderboardData.length === 0" class="no-data">
      <div class="character">
        <div class="character-face"></div>
        <div class="character-eye left"></div>
        <div class="character-eye right"></div>
        <div class="character-mouth"></div>
      </div>
      <p>リーダーボードデータがありません。</p>
      <p>クイズに挑戦してランキングに参加しましょう！</p>
      <router-link to="/quiz" class="start-quiz-btn">クイズを始める</router-link>
    </div>
    
    <div v-else class="leaderboard-content">
      <div class="top-ranks" v-if="leaderboardData.length >= 3">
        <div class="rank-card second-place">
          <div class="medal silver">2</div>
          <div class="avatar">{{ leaderboardData[1]?.username?.charAt(0) || '?' }}</div>
          <div class="username">{{ leaderboardData[1]?.username || 'ユーザー不明' }}</div>
          <div class="score">{{ Math.round(selectedCategory ? (leaderboardData[1]?.category_percentage || 0) : (leaderboardData[1]?.avg_percentage || 0)) }}%</div>
        </div>
        
        <div class="rank-card first-place">
          <div class="medal gold">1</div>
          <div class="crown">👑</div>
          <div class="avatar">{{ leaderboardData[0]?.username?.charAt(0) || '?' }}</div>
          <div class="username">{{ leaderboardData[0]?.username || 'ユーザー不明' }}</div>
          <div class="score">{{ Math.round(selectedCategory ? (leaderboardData[0]?.category_percentage || 0) : (leaderboardData[0]?.avg_percentage || 0)) }}%</div>
        </div>
        
        <div class="rank-card third-place">
          <div class="medal bronze">3</div>
          <div class="avatar">{{ leaderboardData[2]?.username?.charAt(0) || '?' }}</div>
          <div class="username">{{ leaderboardData[2]?.username || 'ユーザー不明' }}</div>
          <div class="score">{{ Math.round(selectedCategory ? (leaderboardData[2]?.category_percentage || 0) : (leaderboardData[2]?.avg_percentage || 0)) }}%</div>
        </div>
      </div>
      
      <div class="leaderboard-table">
        <table>
          <thead>
            <tr>
              <th>順位</th>
              <th>ユーザー</th>
              <th>クイズ回数</th>
              <th>平均正答率</th>
              <th>総合スコア</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="(user, index) in leaderboardData" 
              :key="user?.id || `user-${index}`" 
              :class="{ 
                'current-user': user?.id === currentUserId,
                'top-three': index < 3
              }"
            >
              <td class="rank">
                <div class="rank-badge" :class="{
                  'gold': index === 0,
                  'silver': index === 1,
                  'bronze': index === 2
                }">{{ index + 1 }}</div>
              </td>
              <td class="username">
                <span class="user-avatar">{{ user?.username?.charAt(0) || '?' }}</span>
                {{ user?.username || 'ユーザー不明' }}
                <span v-if="user?.id === currentUserId" class="current-user-tag">あなた</span>
              </td>
              <td class="attempts">
                {{ selectedCategory ? (user?.category_attempts || 0) : (user?.total_attempts || 0) }}回
              </td>
              <td class="percentage">
                <div class="percentage-bar-container">
                  <div class="percentage-bar" :style="{ width: `${selectedCategory ? (user?.category_percentage || 0) : (user?.avg_percentage || 0)}%` }"></div>
                  <span class="percentage-text">{{ Math.round(selectedCategory ? (user?.category_percentage || 0) : (user?.avg_percentage || 0)) }}%</span>
                </div>
              </td>
              <td class="score">
                {{ selectedCategory ? (user?.category_score || 0) : (user?.total_score || 0) }} / 
                {{ selectedCategory ? (user?.category_questions || 0) : (user?.total_questions || 0) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div class="your-rank" v-if="currentUserRank !== null && currentUserRank !== undefined">
        <div class="your-rank-card">
          <div class="your-rank-title">あなたの順位</div>
          <div class="your-rank-value">{{ currentUserRank }}位</div>
          <div class="your-rank-total">{{ leaderboardData.length || 0 }}人中</div>
        </div>
      </div>
      
      <!-- ページネーションコントロール -->
      <div class="pagination-controls" v-if="pagination && pagination.count > 10">
        <button 
          @click="loadPreviousPage" 
          :disabled="!pagination.previous"
          class="pagination-btn prev"
        >
          前へ
        </button>
        <div class="pagination-info">{{ paginationText }}</div>
        <button 
          @click="loadNextPage" 
          :disabled="!pagination.next"
          class="pagination-btn next"
        >
          次へ
        </button>
      </div>
    </div>
  </div>
</template>
  
<script>
import api from '../utils/api';

export default {
  name: 'LeaderboardComponent',
  data() {
    return {
      leaderboardData: [],
      loading: true,
      error: null,
      selectedCategory: null,
      categories: [],  // この行を追加
      pagination: {
        count: 0,
        next: null,
        previous: null,
        currentPage: 1
      }
    };
  },
  computed: {
    isAuthenticated() {
      return this.$store.getters['auth/isAuthenticated'];
    },
    currentUser() {
      return this.$store.getters['auth/currentUser'];
    },
    currentUserId() {
      return this.currentUser ? this.currentUser.id : null;
    },
    currentUserRank() {
      if (!this.currentUserId || !Array.isArray(this.leaderboardData) || !this.leaderboardData.length) return null;
      
      const userIndex = this.leaderboardData.findIndex(user => user && user.id === this.currentUserId);
      return userIndex !== -1 ? userIndex + 1 : null;
    },
    paginationText() {
      const totalPages = Math.ceil(this.pagination.count / 10); // 10は1ページあたりのアイテム数
      return `ページ ${this.pagination.currentPage} / ${totalPages}`;
    }
  },
  created() {
    console.log('Leaderboardコンポーネントが作成されました');
    this.leaderboardData = [];
    this.error = null;
    
    // カテゴリ取得とリーダーボード表示は維持
    this.fetchCategories().then(() => {
      console.log('カテゴリ取得後、リーダーボードを取得します');
      this.fetchLeaderboard();
    }).catch(err => {
      console.error('初期化中にエラーが発生しました:', err);
      this.fetchLeaderboard();
    });
  },
  methods: {
    async fetchCategories() {
      try {
        console.log('カテゴリ取得開始...');
        
        // APIリクエストの詳細をログ出力
        console.log('APIリクエスト: GET /api/categories/');
        
        const response = await api.get('/api/categories/');
        console.log('カテゴリAPIの応答状態:', response.status);
        console.log('カテゴリ応答データ型:', typeof response.data, Array.isArray(response.data) ? '(配列)' : '');
        console.log('カテゴリ応答データ:', response.data);
        
        // レスポンスがページネーション形式かどうか確認
        if (response.data && Array.isArray(response.data.results)) {
          // ページネーション形式の場合
          this.categories = response.data.results;
          console.log(`${this.categories.length}件のカテゴリをページネーションから取得しました`);
        } else if (Array.isArray(response.data)) {
          // 単純な配列の場合
          this.categories = response.data;
          console.log(`${this.categories.length}件のカテゴリを配列から取得しました`);
        } else {
          console.warn('予期しないカテゴリフォーマット:', response.data);
          this.categories = [];
        }
        
        // 例としてカテゴリの最初の要素を表示
        if (this.categories.length > 0) {
          console.log('最初のカテゴリサンプル:', this.categories[0]);
        } else {
          console.warn('カテゴリデータがありません');
        }
        
      } catch (error) {
        console.error('カテゴリの取得に失敗しました:', error);
        console.error('エラー詳細:', error.response?.data || error.message);
        
        // APIエラーの場合、フォールバックとしてハードコードされたカテゴリを提供
        this.categories = [
          { id: 1, name: '地理' },
          { id: 2, name: '歴史' },
          { id: 3, name: '科学' },
          { id: 4, name: '一般常識' }
        ];
        console.log('デフォルトカテゴリを使用します');
      }
    },
    async fetchLeaderboard() {
      try {
        this.loading = true;
        
        // 認証状態をログ出力（デバッグ用）
        if (process.env.NODE_ENV === 'development') {
          console.log('認証状態:', this.isAuthenticated ? '認証済み' : '未認証');
          if (this.currentUser) {
            console.log('現在のユーザー:', this.currentUser.username);
          }
        }
        
        // APIエンドポイントを構築
        let endpoint = '/api/quiz/leaderboard/';
        if (this.selectedCategory) {
          endpoint += `?category=${this.selectedCategory}`;
        } else {
          endpoint += '?category=all';
        }
        
        console.log('リーダーボードAPIを呼び出し中:', endpoint);
        
        const response = await api.get(endpoint);
        console.log('リーダーボード応答:', response.data);
        
        // ページネーション情報を保存
        if (response.data && typeof response.data === 'object') {
          this.pagination = {
            count: response.data.count || 0,
            next: response.data.next,
            previous: response.data.previous,
            currentPage: this.pagination.currentPage
          };
        }
        
        // レスポンスデータの形式を確認
        let userData;
        if (response.data && Array.isArray(response.data.results)) {
          // ページネーション形式の場合
          userData = response.data.results;
        } else if (Array.isArray(response.data)) {
          // 単純な配列の場合
          userData = response.data;
          // ページネーション情報をリセット
          this.pagination = {
            count: userData.length,
            next: null,
            previous: null,
            currentPage: 1
          };
        } else {
          // その他のフォーマットや無効なデータの場合
          console.warn('予期しないレスポンスフォーマット:', response.data);
          userData = [];
        }
        
        // 応答データを変換する前の安全チェック
        if (!Array.isArray(userData)) {
          console.error('ユーザーデータが配列ではありません');
          this.leaderboardData = [];
          return;
        }

        // より安全なマップ処理
        this.leaderboardData = userData
          .filter(user => user !== null && typeof user === 'object')
          .map(user => ({
            id: user.id || `tmp-${Math.random().toString(36).substring(2, 9)}`,
            username: user.username || 'Unknown',
            total_attempts: user.total_attempts || 0,
            total_score: user.total_score || 0,
            total_questions: user.total_questions || 0,
            category_attempts: user.category_attempts || 0,
            category_score: user.category_score || 0,
            category_questions: user.category_questions || 0,
            avg_percentage: user.avg_percentage ? Math.round(user.avg_percentage) : 0,
            category_percentage: user.category_percentage ? Math.round(user.category_percentage) : 0
          }));
        
        this.loading = false;
      } catch (error) {
        console.error('リーダーボードデータの取得に失敗しました:', error);
        this.loading = false;
        this.error = error.message || 'データの取得に失敗しました';
      }
    },
    
    // 履歴データからリーダーボードを生成する代替メソッド
    async generateLeaderboardFromHistory() {
      try {
        // 履歴APIを呼び出し
        const historyResponse = await api.get('/api/quiz/history/');
        console.log('履歴データ:', historyResponse.data);
        
        // ページネーション形式かどうか確認
        let historyData = [];
        if (historyResponse.data && Array.isArray(historyResponse.data.results)) {
          // ページネーション形式の場合
          historyData = historyResponse.data.results;
        } else if (Array.isArray(historyResponse.data)) {
          // 単純な配列の場合
          historyData = historyResponse.data;
        } else {
          console.warn('予期しない履歴データ形式:', historyResponse.data);
        }
        
        if (!historyData.length) {
          this.leaderboardData = [];
          return;
        }
        
        // 現在のユーザー情報の安全な取得
        let currentUser = null;
        if (this.isAuthenticated && this.currentUser) {
          currentUser = this.currentUser;
        } else {
          // 認証されていないかユーザー情報がない場合はデフォルト値を使用
          currentUser = { id: 'guest', username: 'ゲスト' };
        }
        
        // 複数のユーザーを含むリーダーボードを生成（ダミーユーザーを含む）
        const dummyUsers = [
          {
            id: currentUser.id || 1,
            username: currentUser.username || '現在のユーザー',
            total_attempts: historyData.length,
            total_score: historyData.reduce((sum, item) => sum + parseInt(item.score || 0, 10), 0),
            total_questions: historyData.reduce((sum, item) => sum + parseInt(item.total_questions || 0, 10), 0),
            avg_percentage: 0
          },
          {
            id: 2,
            username: 'エキスパートユーザー',
            total_attempts: Math.floor(historyData.length * 1.5),
            total_score: 0,
            total_questions: 0,
            avg_percentage: 85
          },
          {
            id: 3,
            username: '中級者ユーザー',
            total_attempts: Math.floor(historyData.length * 1.2),
            total_score: 0,
            total_questions: 0,
            avg_percentage: 70
          },
          {
            id: 4,
            username: '初心者ユーザー',
            total_attempts: Math.floor(historyData.length * 0.8),
            total_score: 0,
            total_questions: 0,
            avg_percentage: 55
          }
        ];
        
        // 各ユーザーのトータルスコアと質問数を計算
        dummyUsers.forEach(user => {
          if (user.id !== currentUser.id) {
            const attemptCount = user.total_attempts || 1;
            // 平均正答率から逆算してスコアと質問数を設定
            user.total_questions = attemptCount * 5;  // 平均5問/回と仮定
            user.total_score = Math.floor(user.total_questions * (user.avg_percentage / 100));
          } else {
            // 現在のユーザーは実際の履歴に基づいて計算
            user.avg_percentage = user.total_questions > 0 
              ? Math.round((user.total_score / user.total_questions) * 100)
              : 0;
          }
        });
        
        // 平均スコアで降順ソート
        this.leaderboardData = dummyUsers.sort((a, b) => b.avg_percentage - a.avg_percentage);
        
        console.log('生成したリーダーボード (複数ユーザー):', this.leaderboardData);
      } catch (error) {
        console.error('履歴データからのリーダーボード生成に失敗しました:', error);
        this.leaderboardData = [];
      }
    },
    
    // ページネーション用のメソッド
    async loadNextPage() {
      if (!this.pagination.next || typeof this.pagination.next !== 'string') return;
      
      try {
        this.loading = true;
        
        let relativePath;
        try {
          // URLから相対パスを抽出
          const url = new URL(this.pagination.next);
          relativePath = url.pathname + url.search;
        } catch (urlError) {
          // URL解析に失敗した場合は、そのまま使用
          console.warn('URL解析エラー:', urlError);
          relativePath = this.pagination.next;
        }
        
        const response = await api.get(relativePath);
        
        // ページネーション情報を更新
        if (response.data) {
          this.pagination = {
            ...this.pagination,
            next: response.data.next,
            previous: response.data.previous,
            currentPage: this.pagination.currentPage + 1
          };
          
          // データを更新
          if (Array.isArray(response.data.results)) {
            this.leaderboardData = response.data.results.map(user => {
              if (user.avg_percentage) user.avg_percentage = Math.round(user.avg_percentage);
              if (user.category_percentage) user.category_percentage = Math.round(user.category_percentage);
              return user;
            });
          }
        }
        
        this.loading = false;
      } catch (error) {
        console.error('次のページの読み込みに失敗しました:', error);
        this.loading = false;
      }
    },
    
    async loadPreviousPage() {
      if (!this.pagination.previous) return;
      
      try {
        this.loading = true;
        // URLから相対パスを抽出
        const url = new URL(this.pagination.previous);
        const relativePath = url.pathname + url.search;
        
        const response = await api.get(relativePath);
        
        // ページネーション情報を更新
        if (response.data) {
          this.pagination = {
            ...this.pagination,
            next: response.data.next,
            previous: response.data.previous,
            currentPage: this.pagination.currentPage - 1
          };
          
          // データを更新
          if (Array.isArray(response.data.results)) {
            this.leaderboardData = response.data.results.map(user => {
              if (user.avg_percentage) user.avg_percentage = Math.round(user.avg_percentage);
              if (user.category_percentage) user.category_percentage = Math.round(user.category_percentage);
              return user;
            });
          }
        }
        
        this.loading = false;
      } catch (error) {
        console.error('前のページの読み込みに失敗しました:', error);
        this.loading = false;
      }
    },
    
    onCategoryChange() {
      // ページネーション情報をリセット
      this.pagination = {
        count: 0,
        next: null,
        previous: null,
        currentPage: 1
      };
      
      // データを再取得
      this.fetchLeaderboard();
    }
  }
};
</script>
  
<style scoped>
.leaderboard-container {
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
.leaderboard-container::before {
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
.leaderboard-container::after {
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

/* フィルターセクション */
.filter-section {
  margin-bottom: 25px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 1;
}

.filter-section label {
  margin-right: 15px;
  font-weight: bold;
  font-size: 16px;
  color: #FFFFFF;
}

.select-wrapper {
  position: relative;
  display: inline-block;
}

.select-wrapper select {
  padding: 10px 40px 10px 15px;
  border-radius: 25px;
  border: 2px solid rgba(147, 197, 253, 0.5);
  background-color: rgba(30, 64, 175, 0.7);
  color: #FFFFFF;
  min-width: 200px;
  font-size: 15px;
  appearance: none;
  cursor: pointer;
  transition: all 0.3s;
  outline: none;
}

.select-wrapper select:focus {
  border-color: #F97316;
  box-shadow: 0 0 0 2px rgba(249, 115, 22, 0.3);
}

.select-arrow {
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  color: #F97316;
  font-size: 12px;
  pointer-events: none;
}

/* ローディングとエラー表示 */
.loading, .error-message, .no-data {
  text-align: center;
  margin: 50px 0;
  padding: 30px;
  position: relative;
  z-index: 1;
  background-color: rgba(30, 64, 175, 0.5);
  border-radius: 15px;
}

.loading p, .error-message p, .no-data p {
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
  text-decoration: none;
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

/* リーダーボードのコンテンツ */
.leaderboard-content {
  position: relative;
  z-index: 1;
}

/* TOP3のセクション */
.top-ranks {
  display: flex;
  justify-content: center;
  align-items: flex-end;
  margin-bottom: 30px;
  height: 240px;
}

.rank-card {
  width: 140px;
  background-color: rgba(59, 130, 246, 0.7);
  border-radius: 15px;
  padding: 15px;
  text-align: center;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  position: relative;
  transition: all 0.3s;
}

.rank-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
}

.first-place {
  height: 220px;
  z-index: 2;
  background: linear-gradient(to bottom, rgba(59, 130, 246, 0.8), rgba(30, 64, 175, 0.8));
  border: 2px solid #FACC15;
}

.second-place {
  height: 180px;
  margin-right: -10px;
  z-index: 1;
}

.third-place {
  height: 180px;
  margin-left: -10px;
  z-index: 1;
}

.medal {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 10px;
  font-weight: bold;
  font-size: 18px;
  color: #1E40AF;
}

.gold {
  background-color: #FFD700;
  box-shadow: 0 0 10px #FFD700;
}

.silver {
  background-color: #C0C0C0;
}

.bronze {
  background-color: #CD7F32;
}

.crown {
  position: absolute;
  top: -25px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 30px;
  filter: drop-shadow(0 0 5px rgba(0, 0, 0, 0.3));
  animation: float 2s ease-in-out infinite;
}

.avatar {
  width: 60px;
  height: 60px;
  background-color: #F97316;
  border-radius: 50%;
  margin: 10px auto;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: bold;
  color: #FFFFFF;
  border: 3px solid #FFFFFF;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
  text-transform: uppercase;
}

.first-place .avatar {
  width: 70px;
  height: 70px;
  font-size: 28px;
  border: 3px solid #FFD700;
}

.username {
  font-weight: bold;
  margin: 10px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 16px;
}

.score {
  font-size: 20px;
  font-weight: bold;
  color: #FACC15;
}

.first-place .score {
  font-size: 24px;
}

/* テーブルスタイル */
.leaderboard-table {
  margin-bottom: 30px;
  background-color: rgba(30, 64, 175, 0.5);
  border-radius: 15px;
  padding: 15px;
  overflow-x: auto;
  position: relative;
}

.leaderboard-table::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 5px;
  background-color: #F97316;
  border-radius: 2.5px 2.5px 0 0;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 5px;
}

th, td {
  padding: 15px;
  text-align: left;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

th {
  background-color: rgba(30, 64, 175, 0.7);
  font-weight: bold;
  color: #FFFFFF;
  position: sticky;
  top: 0;
}

th:first-child {
  border-top-left-radius: 10px;
}

th:last-child {
  border-top-right-radius: 10px;
}

tr:hover:not(.top-three) {
  background-color: rgba(59, 130, 246, 0.3);
}

tr.current-user {
  background-color: rgba(249, 115, 22, 0.3);
}

tr.current-user:hover {
  background-color: rgba(249, 115, 22, 0.4);
}

tr.top-three {
  background-color: rgba(250, 204, 21, 0.1);
}

.rank-badge {
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background-color: #2563EB;
  margin: 0 auto;
  font-weight: bold;
  color: white;
  font-size: 14px;
}

.rank-badge.gold {
  background-color: #FFD700;
  color: #1E40AF;
  box-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
}

.rank-badge.silver {
  background-color: #C0C0C0;
  color: #1E40AF;
}

.rank-badge.bronze {
  background-color: #CD7F32;
  color: #1E40AF;
}

.user-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  background-color: #2563EB;
  border-radius: 50%;
  margin-right: 10px;
  font-weight: bold;
  font-size: 14px;
  text-transform: uppercase;
}

.current-user-tag {
  display: inline-block;
  background-color: #F97316;
  color: white;
  font-size: 12px;
  padding: 3px 8px;
  border-radius: 12px;
  margin-left: 8px;
  font-weight: bold;
}
.percentage-bar-container {
  width: 100%;
  height: 15px;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 7.5px;
  overflow: hidden;
  position: relative;
}

.percentage-bar {
  height: 100%;
  background-color: #F97316;
  border-radius: 7.5px;
}

.percentage-text {
  position: absolute;
  top: 50%;
  right: 5px;
  transform: translateY(-50%);
  font-size: 12px;
  font-weight: bold;
  color: white;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
}

/* あなたの順位セクション */
.your-rank {
  display: flex;
  justify-content: center;
  margin: 30px 0;
}

.your-rank-card {
  background: linear-gradient(to bottom, #F97316, #EA580C);
  border-radius: 15px;
  padding: 15px 30px;
  color: white;
  text-align: center;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  position: relative;
  overflow: hidden;
}

.your-rank-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 5px;
  background-color: rgba(255, 255, 255, 0.3);
}

.your-rank-title {
  font-size: 16px;
  margin-bottom: 5px;
}

.your-rank-value {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 5px;
}

.your-rank-total {
  font-size: 14px;
  opacity: 0.8;
}

/* ページネーションコントロール */
.pagination-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 20px;
  gap: 15px;
}

.pagination-btn {
  padding: 8px 15px;
  background-color: rgba(30, 64, 175, 0.7);
  border: 1px solid rgba(147, 197, 253, 0.3);
  border-radius: 20px;
  cursor: pointer;
  color: white;
  font-weight: bold;
  transition: all 0.3s;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-btn:hover:not(:disabled) {
  background-color: #F97316;
  border-color: #F97316;
}

.pagination-btn.prev::before {
  content: '◀';
  margin-right: 5px;
  font-size: 10px;
}

.pagination-btn.next::after {
  content: '▶';
  margin-left: 5px;
  font-size: 10px;
}

.pagination-info {
  padding: 8px 15px;
  background-color: rgba(30, 64, 175, 0.7);
  border-radius: 20px;
  color: white;
  font-size: 14px;
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

/* レスポンシブ対応 */
@media (max-width: 768px) {
  .top-ranks {
    flex-direction: column;
    align-items: center;
    height: auto;
    margin-bottom: 30px;
  }
  
  .rank-card {
    width: 80%;
    max-width: 200px;
    height: auto;
    margin: 10px 0;
  }
  
  .first-place, .second-place, .third-place {
    order: 1;
    margin: 10px 0;
  }
  
  .filter-section {
    flex-direction: column;
  }
  
  .filter-section label {
    margin-right: 0;
    margin-bottom: 10px;
  }
  
  table {
    min-width: 600px;
  }
  
  .pagination-controls {
    flex-wrap: wrap;
  }
}

@media (max-width: 480px) {
  .leaderboard-container {
    padding: 15px;
    border-radius: 15px;
  }
  
  h2 {
    font-size: 24px;
    margin-bottom: 20px;
  }
  
  .select-wrapper select {
    min-width: 150px;
  }
  
  .your-rank-card {
    width: 90%;
  }
}

/* アニメーション */
@keyframes float {
  0% { transform: translateY(0) translateX(-50%); }
  50% { transform: translateY(-5px) translateX(-50%); }
  100% { transform: translateY(0) translateX(-50%); }
}
</style>