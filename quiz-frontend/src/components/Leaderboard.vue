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
  padding: 32px 20px;
  color: #f5f0e8;
}

.leaderboard-container h2 {
  font-size: 24px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #f5f0e8;
  text-shadow: 3px 3px 0 #e8001c;
  margin-bottom: 24px;
  padding-bottom: 12px;
  border-bottom: 1px solid #1a1a1a;
  position: relative;
}
.leaderboard-container h2::after {
  content: '';
  position: absolute;
  bottom: -1px; left: 0;
  width: 80px; height: 2px;
  background: #e8001c;
}

/* フィルター */
.filter-section {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
}
.filter-section label {
  font-size: 11px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #444;
  flex-shrink: 0;
}
.select-wrapper {
  position: relative;
  flex: 1;
  max-width: 280px;
}
.filter-select {
  width: 100%;
  padding: 10px 36px 10px 14px;
  background: #0a0a0e;
  border: 1px solid #1e1e22;
  color: #f5f0e8;
  font-size: 13px;
  outline: none;
  appearance: none;
  cursor: pointer;
  transition: border-color 0.15s;
}
.filter-select:focus { border-color: #e8001c; }
.select-arrow {
  position: absolute;
  right: 12px; top: 50%;
  transform: translateY(-50%);
  font-size: 10px;
  color: #444;
  pointer-events: none;
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

.error-message {
  background: #0e0e12;
  border-left: 4px solid #ef4444;
  padding: 16px 20px;
  color: #ef4444;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 12px;
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
  transition: all 0.15s;
  clip-path: polygon(0 0, 100% 0, 94% 100%, 0 100%);
}
.retry-btn:hover { border-color: #e8001c; color: #e8001c; }

/* 空状態 */
.no-data {
  background: #0e0e12;
  border: 1px solid #1a1a1a;
  border-left: 4px solid #333;
  padding: 40px;
  text-align: center;
  color: #444;
}
.character { display: none; }
.character-face, .character-eye, .character-mouth { display: none; }
.no-data p { font-size: 14px; margin-bottom: 16px; }
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

/* トップ3 */
.leaderboard-content { display: flex; flex-direction: column; gap: 16px; }

.top-ranks {
  display: grid;
  grid-template-columns: 1fr 1.1fr 1fr;
  gap: 2px;
  align-items: end;
}

.rank-card {
  background: #0e0e12;
  border: 1px solid #1a1a1a;
  padding: 20px 16px;
  text-align: center;
  position: relative;
  overflow: hidden;
  clip-path: polygon(0 0, 100% 0, 97% 100%, 0 100%);
}

.first-place { border-top: 3px solid #FFD700; }
.second-place { border-top: 2px solid #C0C0C0; }
.third-place { border-top: 2px solid #CD7F32; }

.medal {
  width: 36px; height: 36px;
  display: flex; align-items: center; justify-content: center;
  font-size: 16px; font-weight: 700;
  margin: 0 auto 10px;
  clip-path: polygon(0 0, 100% 0, 85% 100%, 0 100%);
}
.medal.gold { background: #FFD700; color: #060608; }
.medal.silver { background: #C0C0C0; color: #060608; }
.medal.bronze { background: #CD7F32; color: #060608; }

.rank-username { font-size: 13px; font-weight: 700; color: #f5f0e8; margin-bottom: 4px; letter-spacing: 0.04em; }
.rank-score { font-size: 11px; color: #555; letter-spacing: 0.05em; }
.rank-score strong { color: #e8001c; font-size: 16px; }

.crown { display: none; }

/* 全ランキングテーブル */
.rankings-table {
  background: #0e0e12;
  border: 1px solid #1a1a1a;
  overflow: hidden;
}

.table-header {
  display: grid;
  grid-template-columns: 60px 1fr 120px 120px;
  padding: 10px 16px;
  background: #0a0a0e;
  border-bottom: 2px solid #e8001c;
}
.table-header span {
  font-size: 10px;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: #444;
}

.rank-row {
  display: grid;
  grid-template-columns: 60px 1fr 120px 120px;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(255,255,255,0.03);
  align-items: center;
  transition: background 0.15s;
  position: relative;
}
.rank-row::before {
  content: '';
  position: absolute;
  left: 0; top: 0; bottom: 0;
  width: 2px;
  background: #e8001c;
  transform: scaleY(0);
  transition: transform 0.15s;
}
.rank-row:hover { background: rgba(255,255,255,0.02); }
.rank-row:hover::before { transform: scaleY(1); }
.rank-row.current-user { background: rgba(232,0,28,0.05); border-left: 2px solid #e8001c; }

.rank-num {
  font-size: 16px;
  font-weight: 700;
  color: #333;
  letter-spacing: 0.05em;
}
.rank-row.current-user .rank-num { color: #e8001c; }

.rank-name { font-size: 13px; color: #888; letter-spacing: 0.03em; }
.rank-row.current-user .rank-name { color: #f5f0e8; }
.you-badge {
  display: inline-block;
  padding: 1px 6px;
  background: rgba(232,0,28,0.15);
  border: 1px solid rgba(232,0,28,0.3);
  color: #e8001c;
  font-size: 9px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin-left: 6px;
}

.rank-attempts { font-size: 12px; color: #444; }
.rank-percentage { font-size: 14px; font-weight: 700; color: #e8001c; letter-spacing: 0.05em; }

/* ページネーション */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  margin-top: 16px;
}
.page-btn {
  padding: 6px 14px;
  background: #0a0a0e;
  border: 1px solid #1e1e22;
  color: #555;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.15s;
  clip-path: polygon(0 0, 100% 0, 94% 100%, 0 100%);
}
.page-btn:hover { border-color: #e8001c; color: #e8001c; }
.page-btn.active { background: #e8001c; border-color: #e8001c; color: #fff; }
.page-btn:disabled { opacity: 0.3; cursor: not-allowed; }

@media (max-width: 600px) {
  .top-ranks { grid-template-columns: 1fr; }
  .table-header, .rank-row { grid-template-columns: 48px 1fr 80px; }
  .table-header span:nth-child(3), .rank-attempts { display: none; }
}
</style>
