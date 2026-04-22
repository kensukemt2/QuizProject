<template>
  <div class="profile-container">
    <h2>プロフィール</h2>
    
    <div v-if="loading" class="loading">
      <p>読み込み中...</p>
      <div class="loading-spinner"></div>
    </div>
    
    <!-- isAuthenticated も確認 -->
    <div v-else-if="!isAuthenticated || !user" class="error-message">
      <p>ユーザー情報を取得できませんでした。ログインしてください。</p>
      <router-link to="/login" class="login-btn">ログイン</router-link>
    </div>
    
    <div v-else class="profile-content">
      <!-- ユーザー情報セクション -->
      <div class="user-info">
        <div class="avatar-container">
          <div class="avatar">{{ safeUsername.charAt(0) }}{{ safeUsername.charAt(1) || '' }}</div>
        </div>
        <h3>{{ safeUsername }}</h3>
        <p>{{ user.email || 'メールアドレスなし' }}</p>
      </div>
      
      <!-- 統計情報カード -->
      <div class="stats-overview">
        <div class="stat-card">
          <div class="stat-value">{{ stats.total_attempts }}</div>
          <div class="stat-label">クイズ挑戦回数</div>
          <div class="stat-icon quiz-icon"></div>
        </div>
        
        <div class="stat-card">
          <div class="stat-value">{{ stats.total_categories_played }}</div>
          <div class="stat-label">プレイしたカテゴリー</div>
          <div class="stat-icon category-icon"></div>
        </div>
        
        <div class="stat-card">
          <div class="stat-value">{{ Math.round(stats.avg_percentage) }}%</div>
          <div class="stat-label">平均正答率</div>
          <div class="stat-icon percentage-icon"></div>
        </div>
        
        <div class="stat-card">
          <div class="stat-value best-category">{{ stats.best_category || '-' }}</div>
          <div class="stat-label">最も得意なカテゴリー</div>
          <div class="stat-icon trophy-icon"></div>
        </div>
      </div>
      
      <!-- カテゴリー別成績 -->
      <div v-if="stats.category_stats && stats.category_stats.length > 0" class="category-performance">
        <h3>カテゴリー別成績</h3>
        
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>カテゴリー</th>
                <th>挑戦回数</th>
                <th>最高スコア</th>
                <th>平均正答率</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="category in stats.category_stats" :key="category.id">
                <td>
                  <span class="category-tag">{{ category.name }}</span>
                </td>
                <td>{{ category.attempts_count }}回</td>
                <td>{{ category.best_score }}</td>
                <td>
                  <div class="percentage-bar-container">
                    <div class="percentage-bar" :style="{ width: `${Math.round(category.avg_percentage)}%` }"></div>
                    <span class="percentage-text">{{ Math.round(category.avg_percentage) }}%</span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      
      <div v-else class="no-stats">
        <div class="character">
          <div class="character-face"></div>
          <div class="character-eye left"></div>
          <div class="character-eye right"></div>
          <div class="character-mouth"></div>
        </div>
        <p>まだクイズの記録がありません。クイズに挑戦して記録を作りましょう！</p>
        <router-link to="/quiz" class="start-quiz-btn">クイズを始める</router-link>
      </div>
      
      <!-- 最近のアクティビティ -->
      <div class="recent-activity">
        <h3>最近のアクティビティ</h3>
        
        <div v-if="recentAttempts.length === 0" class="no-activity">
          <p>最近のアクティビティはありません。</p>
          <div class="magic-icon">✧</div>
        </div>
        
        <div v-else class="activity-list">
          <div v-for="attempt in recentAttempts" :key="attempt.id" class="activity-item">
            <div class="activity-content">
              <div class="activity-header">
                <span class="category-tag">{{ attempt.category_name }}</span>
                <span class="date">{{ formatDate(attempt.created_at) }}</span>
              </div>
              <div class="activity-score">
                <span class="score-label">スコア:</span>
                <span class="score-value">{{ attempt.score }}/{{ attempt.total_questions }}</span>
                <div class="mini-progress-bar">
                  <div class="mini-progress-fill" :style="{ width: `${attempt.percentage}%` }"></div>
                </div>
                <span class="percentage-value">{{ Math.round(attempt.percentage) }}%</span>
              </div>
            </div>
            <div class="activity-action">
              <router-link :to="'/history'" class="view-btn">詳細</router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../utils/api';
import { mapGetters } from 'vuex';

export default {
  name: 'ProfileComponent',
  data() {
    return {
      stats: {
        total_attempts: 0,
        total_categories_played: 0,
        best_category: null,
        avg_percentage: 0,
        category_stats: []
      },
      recentAttempts: [],
      loading: true,
      apiError: null
    };
  },
  computed: {
    ...mapGetters('auth', ['user', 'isAuthenticated']),
    // 安全にユーザー名を取得するためのゲッター
    safeUsername() {
      return this.user?.username || 'ゲスト';
    }
  },
  created() {
    // 認証状態を確認
    if (!this.isAuthenticated) {
      console.log('未認証のためログインページへリダイレクト');
      this.$router.push('/login');
      return;
    }
    
    // ユーザー情報がない場合は、ユーザー情報を取得
    if (!this.user) {
      console.log('ユーザー情報がないため取得を試みます');
      this.$store.dispatch('auth/fetchUserProfile').then(() => {
        if (!this.user) {
          // それでもユーザー情報が取得できない場合はログイン画面へ
          console.log('ユーザー情報を取得できませんでした');
          this.$router.push('/login');
          return;
        }
        // ユーザー情報が取得できたらデータ取得
        this.fetchUserStats();
        this.fetchRecentActivity();
      });
    } else {
      // ユーザー情報がある場合は、そのままデータ取得
      this.fetchUserStats();
      this.fetchRecentActivity();
    }
  },
  methods: {
    async fetchUserStats() {
      try {
        // デバッグログを追加
        console.log('ユーザー統計の取得を開始します');
        
        const response = await api.get('/api/user/stats/');
        
        // レスポンスの詳細をログ出力
        console.log('ユーザー統計APIのレスポンス:', response);
        console.log('stats.category_stats:', response.data.category_stats);
        console.log('category_stats配列の長さ:', response.data.category_stats?.length || 0);
        
        this.stats = response.data;
      } catch (error) {
        console.error('ユーザー統計の取得に失敗しました:', error);
        
        // エラーの詳細をログ出力
        if (error.response) {
          console.error('エラーレスポンス:', error.response.data);
          console.error('ステータスコード:', error.response.status);
        }
      } finally {
        this.loading = false;
      }
    },
    async fetchRecentActivity() {
      try {
        // $http ではなく api を使用
        const response = await api.get('/api/quiz/history/?limit=5');
        if (response.data && Array.isArray(response.data)) {
          this.recentAttempts = response.data.slice(0, 5);
        } else if (response.data && Array.isArray(response.data.results)) {
          // ページネーション形式の場合
          this.recentAttempts = response.data.results.slice(0, 5);
        }
      } catch (error) {
        console.error('最近のアクティビティの取得に失敗しました:', error);
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
    }
  }
};
</script>

<style scoped>
.profile-container {
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
.profile-container::before {
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
.profile-container::after {
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

h3 {
  position: relative;
  color: #FFFFFF;
  font-size: 20px;
  margin: 0 0 20px 0;
  padding-bottom: 10px;
  z-index: 1;
}

h3::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 40px;
  height: 3px;
  background-color: #F97316;
  border-radius: 1.5px;
}

.loading, .error-message {
  text-align: center;
  margin: 50px 0;
  z-index: 1;
  position: relative;
}

.loading p, .error-message p {
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

.login-btn, .start-quiz-btn {
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

.login-btn::before, .start-quiz-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 5px;
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 2.5px 2.5px 0 0;
}

.login-btn:hover, .start-quiz-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
}

.start-quiz-btn::after {
  content: '▶';
  display: inline-block;
  margin-left: 8px;
  font-size: 12px;
}

.profile-content {
  position: relative;
  z-index: 1;
}

/* ユーザー情報セクション */
.user-info {
  text-align: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  position: relative;
}

.user-info::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 20%;
  width: 60%;
  height: 1px;
  background: linear-gradient(to right, transparent, rgba(255, 255, 255, 0.5), transparent);
}

.avatar-container {
  display: flex;
  justify-content: center;
  margin-bottom: 15px;
}

.avatar {
  width: 80px;
  height: 80px;
  background-color: #F97316;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  font-weight: bold;
  color: #FFFFFF;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  border: 2px solid #FFFFFF;
  text-transform: uppercase;
}

.user-info h3 {
  margin: 0 0 10px 0;
  padding: 0;
  font-size: 24px;
}

.user-info h3::after {
  display: none;
}

.user-info p {
  color: rgba(255, 255, 255, 0.8);
  font-size: 16px;
}

/* 統計情報カード */
.stats-overview {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  margin-bottom: 30px;
}

.stat-card {
  width: calc(25% - 15px);
  background-color: rgba(59, 130, 246, 0.7);
  border-radius: 15px;
  padding: 20px 15px;
  text-align: center;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  position: relative;
  overflow: hidden;
  transition: transform 0.3s;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 5px;
  background-color: #F97316;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #FFFFFF;
  margin-bottom: 5px;
}

.stat-value.best-category {
  font-size: 18px;
}

.stat-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
}

.stat-icon {
  width: 32px;
  height: 32px;
  margin: 10px auto 0;
  opacity: 0.8;
  position: relative;
}

.stat-icon::before {
  content: '';
  position: absolute;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  transform: scale(1.2);
}

/* アイコンプレースホルダー */
.quiz-icon::after {
  content: 'Q';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #FFFFFF;
  font-weight: bold;
  font-size: 18px;
}

.category-icon::after {
  content: 'C';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #FFFFFF;
  font-weight: bold;
  font-size: 18px;
}

.percentage-icon::after {
  content: '%';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #FFFFFF;
  font-weight: bold;
  font-size: 18px;
}

.trophy-icon::after {
  content: '🏆';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

/* カテゴリー別成績 */
.category-performance {
  margin-bottom: 30px;
  background-color: rgba(30, 64, 175, 0.5);
  border-radius: 15px;
  padding: 20px;
  position: relative;
}

.category-performance::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 5px;
  background-color: #FACC15;
  border-radius: 2.5px 2.5px 0 0;
}

.table-container {
  overflow-x: auto;
  margin-top: 15px;
  border-radius: 8px;
}

table {
  width: 100%;
  border-collapse: collapse;
  background-color: rgba(59, 130, 246, 0.3);
  border-radius: 8px;
  overflow: hidden;
}

th, td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

th {
  background-color: rgba(30, 64, 175, 0.7);
  font-weight: bold;
  color: #FFFFFF;
}

td {
  color: #FFFFFF;
}

.category-tag {
  display: inline-block;
  padding: 5px 10px;
  background-color: #1E40AF;
  border-radius: 15px;
  font-size: 14px;
  color: #FFFFFF;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.percentage-bar-container {
  position: relative;
  width: 100%;
  height: 20px;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  overflow: hidden;
}

.percentage-bar {
  height: 100%;
  background-color: #F97316;
  border-radius: 10px;
  transition: width 0.5s;
}

.percentage-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #FFFFFF;
  font-weight: bold;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
  font-size: 12px;
}

/* 統計データがない場合 */
.no-stats, .no-activity {
  text-align: center;
  padding: 40px 20px;
  background-color: rgba(30, 64, 175, 0.5);
  border-radius: 15px;
  margin-bottom: 30px;
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

/* 最近のアクティビティ */
.recent-activity {
  margin-top: 20px;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.activity-item {
  background-color: rgba(59, 130, 246, 0.7);
  border-radius: 15px;
  padding: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
  transition: transform 0.3s;
}

.activity-item:hover {
  transform: translateY(-3px);
}

.activity-content {
  flex: 1;
}

.activity-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.activity-header .category-tag {
  background-color: #2563EB;
}

.date {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
}

.activity-score {
  display: flex;
  align-items: center;
  gap: 8px;
}

.score-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
}

.score-value {
  font-weight: bold;
}

.mini-progress-bar {
  flex: 1;
  height: 10px;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 5px;
  overflow: hidden;
}

.mini-progress-fill {
  height: 100%;
  background-color: #F97316;
  border-radius: 5px;
  transition: width 0.5s;
}

.percentage-value {
  font-weight: bold;
  color: #FACC15;
  min-width: 45px;
  text-align: right;
}

.activity-action .view-btn {
  display: inline-block;
  padding: 6px 12px;
  background-color: #1E40AF;
  color: white;
  border-radius: 15px;
  text-decoration: none;
  font-size: 14px;
  font-weight: bold;
  transition: all 0.3s;
}

.activity-action .view-btn:hover {
  background-color: #F97316;
}

@media (max-width: 768px) {
  .stat-card {
    width: calc(50% - 10px);
    margin-bottom: 15px;
  }
  
  .activity-item {
    flex-direction: column;
  }
  
  .activity-action {
    width: 100%;
    margin-top: 10px;
    text-align: right;
  }
}

@media (max-width: 480px) {
  .profile-container {
    padding: 15px;
    border-radius: 15px;
  }
  
  h2 {
    font-size: 24px;
    margin-bottom: 20px;
  }
  
  .stat-card {
    width: 100%;
    margin-bottom: 15px;
  }
  
  .stat-value {
    font-size: 24px;
  }
  
  th, td {
    padding: 8px;
  }
  
  .activity-header {
    flex-direction: column;
    gap: 5px;
  }
  
  .activity-score {
    flex-wrap: wrap;
  }
}
</style>