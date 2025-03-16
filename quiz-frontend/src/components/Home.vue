<template>
  <div class="home">
    <!-- 背景グロー効果 -->
    <div class="background-glow"></div>
    
    <div class="header">
      <div class="logo">
        <div class="logo-box">Q</div>
        <h1>マジカルクイズ</h1>
      </div>
      
      <!-- ユーザーバッジ（ログイン中のみ表示） -->
      <div v-if="isAuthenticated" class="user-badge">
        {{ user.username.charAt(0).toUpperCase() }}{{ user.username.charAt(1).toUpperCase() }}
      </div>
    </div>
    
    <div class="content-container">
      <div class="hero-section">
        <div class="character">
          <div class="face"></div>
          <div class="eye left"></div>
          <div class="eye-pupil left"></div>
          <div class="eye right"></div>
          <div class="eye-pupil right"></div>
          <div class="mouth"></div>
          <div class="hair"></div>
        </div>
        
        <div class="hero-text">
          <h2>マジカルクイズワールド</h2>
          <p>４つの選択肢から正解を見つけよう！魔法の知識バトル！</p>
        </div>
        
        <!-- ログイン済みユーザー向け -->
        <div v-if="isAuthenticated" class="authenticated-options">
          <button class="btn primary-btn" @click="startQuiz">クイズを始める</button>
          <div class="user-stats">
            <p>こんにちは、{{ user.username }}さん</p>
            <p>これまでの挑戦回数: {{ userStats.total_attempts || 0 }}</p>
          </div>
        </div>
        
        <!-- ゲストユーザー向け -->
        <div v-else class="guest-options">
          <button class="btn primary-btn" @click="startGuestQuiz">ゲストとしてクイズを始める</button>
          <button class="btn secondary-btn" @click="goToLogin">ログインする</button>
        </div>
      </div>
      
      <!-- カテゴリーセクション -->
      <div class="category-section">
        <h3>クイズカテゴリ</h3>
        <div class="category-underline"></div>
        
        <!-- ローディング状態 -->
        <div v-if="loading" class="loading-categories">
          <p>カテゴリをロード中...</p>
        </div>
        
        <!-- エラー表示 -->
        <div v-else-if="error" class="error-message">
          <p>{{ error }}</p>
          <button @click="fetchCategories" class="retry-btn">再読み込み</button>
        </div>
        
        <!-- カテゴリ一覧 -->
        <div v-else-if="categories && categories.length > 0" class="categories">
          <div 
            v-for="category in categories" 
            :key="category.id"
            :class="['category-card', category.colorClass]"
          >
            <div class="category-line"></div>
            <h4>{{ category.name }}</h4>
            <div class="category-icon">{{ category.icon }}</div>
            <button class="category-btn" @click="startCategoryQuiz(category.id)">挑戦する</button>
          </div>
        </div>
        
        <!-- カテゴリがない場合 -->
        <div v-else class="no-categories">
          <p>現在利用可能なカテゴリーはありません。</p>
        </div>
      </div>
      
      <!-- ゲスト向け情報 -->
      <div v-if="!isAuthenticated" class="guest-info">
        <h3>ログインするメリット</h3>
        <ul>
          <li>クイズの成績を保存できる</li>
          <li>ランキングに参加できる</li>
          <li>履歴から過去の回答を確認できる</li>
          <li>カスタマイズされたクイズに挑戦できる</li>
        </ul>
      </div>
      
      <!-- リーダーボードプレビュー -->
      <div class="leaderboard-preview">
        <div class="leaderboard-container">
          <template v-if="leaderboardLoading">
            <span class="loading-indicator">ランキング取得中...</span>
          </template>
          <template v-else>
            <template v-for="(user, index) in leaderboard" :key="index">
              <span :class="['rank', getRankClass(index)]">{{ index + 1 }}</span>
              <span>{{ user.username || '名無し' }} - {{ formatPercentage(user.avg_percentage || 0) }}</span>
            </template>
            <span v-if="isAuthenticated" class="all-rankings" @click="$router.push('/leaderboard')">全ランキング ▶</span>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';
import axios from 'axios';

export default {
  name: 'HomePage',
  data() {
    return {
      userStats: {
        total_attempts: 0
      },
      categories: [],
      loading: false,
      error: null,
      // リーダーボード関連の新しいプロパティ
      leaderboard: [],
      leaderboardLoading: false,
      leaderboardError: null
    };
  },
  computed: {
    ...mapGetters('auth', ['isAuthenticated', 'user'])
  },
  methods: {
    startQuiz() {
      this.$router.push('/quiz');
    },
    startGuestQuiz() {
      // Vuexストアにゲストモードフラグを保存（より確実）
      this.$store.commit('quiz/SET_GUEST_MODE', true);
      
      // ローカルストレージにも保存
      localStorage.setItem('quizMode', 'guest');
      
      // 明示的なクエリパラメータでルーティング
      this.$router.push({
        path: '/quiz',
        query: { mode: 'guest' }
      });
    },
    startCategoryQuiz(categoryId) {
      // カテゴリーIDをもとにルーティング
      this.$router.push({
        path: '/quiz',
        query: { 
          category: categoryId,
          mode: this.isAuthenticated ? 'user' : 'guest'
        }
      });
    },
    goToLogin() {
      this.$router.push('/login');
    },
    async fetchUserStats() {
      if (!this.isAuthenticated) {
        this.userStats = {
          total_attempts: 0,
          total_categories_played: 0,
          best_category: null,
          avg_percentage: 0
        };
        return;
      }
      
      try {
        // ログインユーザーの場合、統計情報を取得
        const response = await this.$store.dispatch('user/fetchStats');
        if (response) {
          this.userStats = response;
        }
      } catch (error) {
        console.error('ユーザー統計の取得に失敗:', error);
        // エラー時のフォールバック
        this.userStats = {
          total_attempts: 0,
          total_categories_played: 0,
          best_category: null,
          avg_percentage: 0
        };
      }
    },
    // 新しく追加：カテゴリーをAPIから取得
    async fetchCategories() {
      try {
        this.loading = true;
        this.error = null;
        
        // APIからカテゴリーデータを取得
        const response = await axios.get('http://localhost:8000/api/categories/');
        console.log('カテゴリデータ:', response.data);
        
        // レスポンスフォーマットの確認と処理
        let categoryData = [];
        if (Array.isArray(response.data)) {
          categoryData = response.data;
        } else if (response.data && Array.isArray(response.data.results)) {
          categoryData = response.data.results;
        } else {
          throw new Error('予期しないレスポンス形式');
        }
        
        // カテゴリーデータの加工（アイコン情報の追加）
        this.categories = categoryData.map(category => {
          return {
            ...category,
            // カテゴリー名の最初の文字をアイコン文字として使用
            icon: category.name.charAt(0).toUpperCase(),
            // 背景色クラスをランダムに割り当て
            colorClass: this.getRandomColorClass()
          };
        });
        
      } catch (error) {
        console.error('カテゴリーの取得に失敗しました:', error);
        this.error = 'カテゴリーの読み込みに失敗しました';
      } finally {
        this.loading = false;
      }
    },
    // カテゴリーに色をランダムに割り当て
    getRandomColorClass() {
      const colors = ['anime', 'game', 'manga', 'pop'];
      return colors[Math.floor(Math.random() * colors.length)];
    },
    // リーダーボードデータの取得
    async fetchLeaderboard() {
      try {
        this.leaderboardLoading = true;
        this.leaderboardError = null;
        
        // 公開エンドポイントを使用
        const response = await axios.get('http://localhost:8000/api/public/leaderboard/');
        
        console.log('リーダーボードデータ:', response.data);
        
        // レスポンスフォーマットの確認と処理
        if (Array.isArray(response.data)) {
          this.leaderboard = response.data.slice(0, 3);
        } else if (response.data && Array.isArray(response.data.results)) {
          this.leaderboard = response.data.results.slice(0, 3);
        } else {
          throw new Error('予期しないレスポンス形式');
        }
        
      } catch (error) {
        console.error('リーダーボードの取得に失敗しました:', error);
        this.leaderboardError = 'ランキングデータの読み込みに失敗しました';
        
        // フォールバックデータ
        this.useDefaultLeaderboard();
      } finally {
        this.leaderboardLoading = false;
      }
    },

    // フォールバックデータの設定
    useDefaultLeaderboard() {
      this.leaderboard = [
        { username: 'アニメマスター', percentage: 99.1, rank: 1 },
        { username: 'ゲームキング', percentage: 97.8, rank: 2 },
        { username: 'マンガヒーロー', percentage: 95.5, rank: 3 }
      ];
    },
    // ランキングクラスの取得（金、銀、銅）
    getRankClass(index) {
      const rankClasses = ['gold', 'silver', 'bronze'];
      return index < rankClasses.length ? rankClasses[index] : '';
    },
    
    // パーセンテージのフォーマット
    formatPercentage(value) {
      // 数値であることを確認
      const num = parseFloat(value);
      return isNaN(num) ? '0.0%' : `${num.toFixed(1)}%`;
    }
  },
  created() {
    // コンポーネント作成時にカテゴリーとユーザー統計を取得
    this.fetchCategories();
    this.fetchUserStats();
    this.fetchLeaderboard(); // リーダーボードデータの取得を追加
  }
};
</script>

<style scoped>
/* ベース要素 */
.home {
  min-height: 100vh;
  position: relative;
  background: linear-gradient(to bottom right, #3B82F6, #1E40AF);
  overflow: hidden;
  color: #FFFFFF;
  font-family: Arial, sans-serif;
  padding-bottom: 2rem;
}

/* 背景グロー効果 */
.background-glow {
  position: absolute;
  top: -100px;
  left: 0;
  right: 0;
  width: 600px;
  height: 600px;
  margin: 0 auto;
  background: radial-gradient(circle, rgba(147, 197, 253, 0.6) 0%, rgba(30, 64, 175, 0) 70%);
  z-index: 0;
}

/* グリッド線 */
.home::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    linear-gradient(to right, rgba(147, 197, 253, 0.2) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(147, 197, 253, 0.2) 1px, transparent 1px);
  background-size: 200px 200px;
  z-index: 1;
}

/* コンテンツコンテナ */
.content-container {
  position: relative;
  z-index: 2;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

/* ヘッダー */
.header {
  height: 70px;
  background-color: rgba(37, 99, 235, 0.9);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 2rem;
  border-bottom: 2px solid #F97316;
  position: relative;
  z-index: 10;
}

.logo {
  display: flex;
  align-items: center;
}

.logo-box {
  width: 40px;
  height: 40px;
  background-color: #F97316;
  color: white;
  display: flex;
  justify-content: center;
  align-items: center;
  font-weight: bold;
  font-size: 26px;
  border-radius: 10px;
  margin-right: 10px;
}

.logo h1 {
  color: white;
  font-size: 24px;
  margin: 0;
}

.user-badge {
  width: 40px;
  height: 40px;
  background-color: #F97316;
  border: 2px solid white;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-weight: bold;
  font-size: 16px;
  color: white;
}

/* ヒーローセクション */
.hero-section {
  background-color: rgba(59, 130, 246, 0.7);
  border-radius: 20px;
  padding: 2rem;
  margin-top: 2rem;
  position: relative;
  text-align: center;
  overflow: hidden;
  border-top: 5px solid rgba(249, 115, 22, 0.7);
}

.hero-text {
  margin-bottom: 2rem;
}

.hero-text h2 {
  font-size: 2.5rem;
  margin-bottom: 1rem;
  color: white;
}

.hero-text p {
  font-size: 1.2rem;
  color: #DBEAFE;
  max-width: 600px;
  margin: 0 auto;
}

/* キャラクター */
.character {
  position: absolute;
  left: 10%;
  top: 50%;
  transform: translateY(-50%);
  width: 100px;
  height: 100px;
}

.face {
  width: 100px;
  height: 100px;
  background-color: #FACC15;
  border-radius: 50%;
  position: relative;
}

.eye {
  width: 20px;
  height: 20px;
  background-color: white;
  border-radius: 50%;
  position: absolute;
}

.eye.left {
  top: 30px;
  left: 20px;
}

.eye.right {
  top: 30px;
  right: 20px;
}

.eye-pupil {
  width: 10px;
  height: 10px;
  background-color: #1E40AF;
  border-radius: 50%;
  position: absolute;
}

.eye-pupil.left {
  top: 35px;
  left: 25px;
}

.eye-pupil.right {
  top: 35px;
  right: 25px;
}

.mouth {
  position: absolute;
  width: 30px;
  height: 15px;
  border-bottom: 4px solid #1E40AF;
  border-radius: 50%;
  bottom: 25px;
  left: 35px;
}

.hair {
  position: absolute;
  top: -20px;
  left: 0;
  width: 100px;
  height: 30px;
  background-color: transparent;
  border-top: 10px solid #FB923C;
  border-radius: 50% 50% 0 0;
}

/* ボタン */
.btn {
  padding: 0.8rem 2rem;
  font-size: 1.2rem;
  border-radius: 22.5px;
  cursor: pointer;
  border: none;
  transition: all 0.3s ease;
  outline: none;
}

.primary-btn {
  background: linear-gradient(to bottom, #F97316, #EA580C);
  color: white;
  position: relative;
  overflow: hidden;
}

.primary-btn::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 5px;
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 22.5px 22.5px 0 0;
}

.primary-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.secondary-btn {
  background-color: #1E40AF;
  color: #93C5FD;
  border: 2px solid #93C5FD;
  margin-left: 1rem;
}

.secondary-btn:hover {
  background-color: #2563EB;
  color: white;
}

/* カテゴリーセクション */
.category-section {
  margin-top: 3rem;
}

.category-section h3 {
  font-size: 1.5rem;
  color: #F97316;
  text-align: left;
  margin-bottom: 0.5rem;
}

.category-underline {
  width: 160px;
  height: 3px;
  background-color: #F97316;
  margin-bottom: 1.5rem;
}

.categories {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.category-card {
  background-color: rgba(59, 130, 246, 0.7);
  border-radius: 15px;
  padding: 1.5rem;
  text-align: center;
  position: relative;
  height: 180px;
  transition: transform 0.3s ease;
}

.category-card:hover {
  transform: translateY(-5px);
}

.category-line {
  position: absolute;
  top: 0;
  left: 0;
  width: 5px;
  height: 100%;
  border-radius: 15px 0 0 15px;
}

.category-card.anime .category-line { background-color: #F97316; }
.category-card.game .category-line { background-color: #10B981; }
.category-card.manga .category-line { background-color: #FACC15; }
.category-card.pop .category-line { background-color: #93C5FD; }

.category-card h4 {
  font-size: 1.2rem;
  margin-top: 0.5rem;
  margin-bottom: 1.5rem;
}

.category-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 0 auto 1.5rem;
  font-size: 1.5rem;
  font-weight: bold;
  color: white;
}

.category-card.anime .category-icon { background-color: #F97316; }
.category-card.game .category-icon { background-color: #10B981; }
.category-card.manga .category-icon { background-color: #FACC15; }
.category-card.pop .category-icon { 
  background-color: #93C5FD;
  color: #1E40AF;
}

.category-btn {
  background-color: #1E40AF;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 15px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.category-btn:hover {
  background-color: #2563EB;
}

/* 追加スタイル */
.loading-categories, .error-message, .no-categories {
  text-align: center;
  padding: 2rem;
  background-color: rgba(59, 130, 246, 0.7);
  border-radius: 15px;
  margin-top: 1rem;
}

.loading-categories::after {
  content: '';
  display: inline-block;
  width: 1rem;
  height: 1rem;
  border: 2px solid #FFF;
  border-radius: 50%;
  border-top-color: transparent;
  animation: spin 1s linear infinite;
  margin-left: 0.5rem;
}

.error-message {
  background-color: rgba(239, 68, 68, 0.7);
}

.retry-btn {
  background-color: #1E40AF;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 15px;
  cursor: pointer;
  margin-top: 0.5rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ゲスト情報 */
.guest-info {
  margin-top: 3rem;
  background-color: rgba(30, 64, 175, 0.7);
  padding: 1.5rem;
  border-radius: 8px;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.guest-info h3 {
  color: #FCD34D;
  margin-bottom: 1rem;
}

.guest-info ul {
  text-align: left;
  padding-left: 1.5rem;
}

.guest-info li {
  margin: 0.5rem 0;
  color: #DBEAFE;
}

/* リーダーボードプレビュー */
.leaderboard-preview {
  margin-top: 3rem;
  display: flex;
  justify-content: center;
}

.leaderboard-container {
  background-color: #1E40AF;
  border-radius: 10px;
  padding: 0.5rem 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 0.9rem;
}

.rank {
  display: inline-block;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  text-align: center;
  line-height: 16px;
  font-size: 0.8rem;
  font-weight: bold;
}

.rank.gold { background-color: #FFD700; }
.rank.silver { background-color: #C0C0C0; }
.rank.bronze { background-color: #CD7F32; }

.all-rankings {
  color: #F97316;
  margin-left: auto;
  cursor: pointer;
}

/* リーダーボード関連のスタイル追加 */
.loading-indicator {
  display: inline-flex;
  align-items: center;
}

.loading-indicator::after {
  content: '';
  display: inline-block;
  width: 0.8rem;
  height: 0.8rem;
  border: 2px solid #F97316;
  border-radius: 50%;
  border-top-color: transparent;
  animation: spin 1s linear infinite;
  margin-left: 0.5rem;
}

/* ユーザー統計 */
.user-stats {
  margin-top: 1.5rem;
  color: #DBEAFE;
}

/* モバイル対応 */
@media (max-width: 768px) {
  .header {
    padding: 0 1rem;
  }
  
  .logo h1 {
    font-size: 20px;
  }
  
  .character {
    display: none;
  }
  
  .hero-text h2 {
    font-size: 1.8rem;
  }
  
  .hero-text p {
    font-size: 1rem;
  }
  
  .guest-options {
    display: flex;
    flex-direction: column;
  }
  
  .secondary-btn {
    margin-left: 0;
    margin-top: 1rem;
  }
  
  .categories {
    grid-template-columns: 1fr;
  }
  
  .leaderboard-container {
    flex-wrap: wrap;
    justify-content: center;
    padding: 1rem;
  }
}

/* アニメーション */
@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

.primary-btn {
  animation: pulse 2s infinite;
}
</style>