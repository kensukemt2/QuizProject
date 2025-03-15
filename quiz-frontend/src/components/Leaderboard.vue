<template>
    <div class="leaderboard-container">
      <h2>リーダーボード</h2>
      
      <div class="filter-section">
        <label for="category-filter">カテゴリーフィルター:</label>
        <select id="category-filter" v-model="selectedCategory" @change="onCategoryChange">
          <option :value="null">すべてのカテゴリー</option>
          <option v-for="category in categories" :key="category.id" :value="category.id">
            {{ category.name }}
          </option>
        </select>
      </div>
      
      <div v-if="loading" class="loading">
        <p>読み込み中...</p>
      </div>
      <div v-else-if="error" class="error-message">
        <p>{{ error }}</p>
        <button @click="fetchLeaderboard" class="retry-btn">再試行</button>
      </div>
      <div v-else-if="leaderboardData.length === 0" class="no-data">
        <p>リーダーボードデータがありません。</p>
      </div>
      <div v-else class="leaderboard-table">
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
            <tr v-for="(user, index) in leaderboardData" :key="user?.id || `user-${index}`" :class="{ 'current-user': user?.id === currentUserId }">
              <td class="rank">{{ index + 1 }}</td>
              <td class="username">
                {{ user?.username || 'ユーザー不明' }}
                <span v-if="user?.id === currentUserId" class="current-user-tag">あなた</span>
              </td>
              <td class="attempts">
                {{ selectedCategory ? (user?.category_attempts || 0) : (user?.total_attempts || 0) }}回
              </td>
              <td class="percentage">
                {{ selectedCategory ? (user?.category_percentage || 0) : (user?.avg_percentage || 0) }}%
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
        <p>あなたの順位: <strong>{{ currentUserRank }}位</strong> / {{ leaderboardData.length || 0 }}人中</p>
      </div>
      
      <!-- ページネーションコントロール（必要に応じて） -->
      <div class="pagination-controls" v-if="pagination && pagination.count > 10">
        <button 
          @click="loadPreviousPage" 
          :disabled="!pagination.previous"
          class="pagination-btn"
        >
          前へ
        </button>
        <span class="pagination-info">{{ paginationText }}</span>
        <button 
          @click="loadNextPage" 
          :disabled="!pagination.next"
          class="pagination-btn"
        >
          次へ
        </button>
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
      
      // ページネーション用の新しいメソッド
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
  }
  
  h2 {
    text-align: center;
    margin-bottom: 20px;
  }
  
  .filter-section {
    margin-bottom: 20px;
    display: flex;
    align-items: center;
  }
  
  .filter-section label {
    margin-right: 10px;
    font-weight: bold;
  }
  
  .filter-section select {
    padding: 8px;
    border-radius: 4px;
    border: 1px solid #ddd;
    min-width: 200px;
  }
  
  .loading, .no-data {
    text-align: center;
    margin-top: 50px;
  }
  
  .leaderboard-table {
    background-color: #f5f5f5;
    border-radius: 8px;
    padding: 15px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    overflow-x: auto;
  }
  
  table {
    width: 100%;
    border-collapse: collapse;
  }
  
  th, td {
    padding: 12px 15px;
    text-align: left;
    border-bottom: 1px solid #ddd;
  }
  
  th {
    background-color: #f0f0f0;
    font-weight: bold;
  }
  
  tr:hover {
    background-color: #f9f9f9;
  }
  
  tr.current-user {
    background-color: #e3f2fd;
  }
  
  tr.current-user:hover {
    background-color: #bbdefb;
  }
  
  .rank {
    text-align: center;
    font-weight: bold;
  }
  
  .username {
    font-weight: bold;
  }
  
  .current-user-tag {
    background-color: #2196F3;
    color: white;
    font-size: 0.8em;
    padding: 3px 6px;
    border-radius: 4px;
    margin-left: 8px;
  }
  
  .your-rank {
    margin-top: 20px;
    text-align: center;
    font-size: 1.1em;
  }
  
  /* Top 3 ランキング用のスタイル */
  tbody tr:nth-child(1) .rank {
    color: #FFD700; /* ゴールド */
  }
  
  tbody tr:nth-child(2) .rank {
    color: #C0C0C0; /* シルバー */
  }
  
  tbody tr:nth-child(3) .rank {
    color: #CD7F32; /* ブロンズ */
  }
  
  @media (max-width: 600px) {
    th, td {
      padding: 8px;
    }
    
    .leaderboard-table {
      padding: 10px;
    }
  }
  
  .pagination-controls {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-top: 20px;
    gap: 10px;
  }
  
  .pagination-btn {
    padding: 8px 15px;
    background-color: #f0f0f0;
    border: 1px solid #ddd;
    border-radius: 4px;
    cursor: pointer;
  }
  
  .pagination-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  .pagination-btn:hover:not(:disabled) {
    background-color: #e0e0e0;
  }
  
  .pagination-info {
    padding: 0 10px;
  }

  .error-message {
    color: #f44336;
    text-align: center;
    margin: 20px 0;
    padding: 15px;
    background-color: #ffebee;
    border-radius: 4px;
  }

  .retry-btn {
    background-color: #2196F3;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    margin-top: 10px;
    cursor: pointer;
  }

  .retry-btn:hover {
    background-color: #0d8bf2;
  }
  </style>