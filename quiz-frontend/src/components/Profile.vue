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
  padding: 32px 20px;
  color: #f5f0e8;
}

.profile-container h2 {
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
.profile-container h2::after {
  content: '';
  position: absolute;
  bottom: -1px; left: 0;
  width: 80px; height: 2px;
  background: #e8001c;
}

/* ローディング */
.loading {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; min-height: 300px; gap: 16px; color: #555;
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
  border: 1px solid #1a1a1a;
  border-left: 4px solid #ef4444;
  padding: 20px;
  text-align: center;
  color: #ef4444;
}
.login-btn {
  display: inline-block;
  margin-top: 12px;
  padding: 8px 20px;
  background: #e8001c;
  color: #fff;
  text-decoration: none;
  font-size: 12px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  clip-path: polygon(0 0, 100% 0, 94% 100%, 0 100%);
}

/* ユーザー情報 */
.profile-content { display: flex; flex-direction: column; gap: 20px; }

.user-info {
  background: #0e0e12;
  border: 1px solid #1a1a1a;
  border-left: 4px solid #e8001c;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  position: relative;
  overflow: hidden;
}
.user-info::after {
  content: '';
  position: absolute;
  top: 0; right: 0;
  width: 0; height: 0;
  border-style: solid;
  border-width: 0 36px 36px 0;
  border-color: transparent #060608 transparent transparent;
}

.avatar-container { flex-shrink: 0; }
.avatar {
  width: 64px; height: 64px;
  background: #e8001c;
  clip-path: polygon(0 0, 100% 0, 100% 70%, 85% 100%, 0 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  font-weight: 700;
  color: #fff;
  letter-spacing: 0.05em;
}

.user-info h3 {
  font-size: 20px;
  letter-spacing: 0.06em;
  color: #f5f0e8;
  margin-bottom: 4px;
}
.user-info p { font-size: 12px; color: #555; letter-spacing: 0.05em; }
.username-tag {
  display: inline-block;
  padding: 2px 8px;
  background: rgba(232,0,28,0.1);
  border: 1px solid rgba(232,0,28,0.2);
  color: #e8001c;
  font-size: 11px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin-top: 4px;
}

/* 統計 */
.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 2px;
}

.stat-card {
  background: #0e0e12;
  border: 1px solid #1a1a1a;
  border-top: 2px solid #e8001c;
  padding: 20px 16px;
  position: relative;
  overflow: hidden;
  clip-path: polygon(0 0, 100% 0, 97% 100%, 0 100%);
}
.stat-value {
  font-size: 32px;
  letter-spacing: 0.05em;
  color: #e8001c;
  line-height: 1;
  margin-bottom: 6px;
}
.stat-label {
  font-size: 11px;
  letter-spacing: 0.1em;
  color: #444;
  text-transform: uppercase;
}
.stat-icon { display: none; }

/* ベストカテゴリ */
.best-category-section,
.category-stats,
.recent-activity {
  background: #0e0e12;
  border: 1px solid #1a1a1a;
  border-left: 4px solid #f5e642;
  padding: 20px;
}

.section-title {
  font-size: 13px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #f5e642;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #1a1a1a;
}

.best-category-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 0;
}
.best-category-icon {
  width: 40px; height: 40px;
  background: rgba(245,230,66,0.1);
  border: 1px solid rgba(245,230,66,0.2);
  display: flex; align-items: center; justify-content: center;
  font-size: 18px;
  clip-path: polygon(0 0, 100% 0, 85% 100%, 0 100%);
}
.best-category-name { font-size: 15px; font-weight: 700; color: #f5f0e8; }
.best-category-score { font-size: 12px; color: #555; margin-top: 2px; }

/* カテゴリ統計テーブル */
.category-stats-table { width: 100%; border-collapse: collapse; }
.category-stats-table th {
  font-size: 10px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #444;
  padding: 8px 10px;
  text-align: left;
  border-bottom: 1px solid #1a1a1a;
}
.category-stats-table td {
  padding: 10px 10px;
  font-size: 13px;
  color: #888;
  border-bottom: 1px solid rgba(255,255,255,0.03);
}
.category-stats-table tr:hover td { color: #f5f0e8; background: rgba(255,255,255,0.02); }
.category-stats-table .percentage-cell { color: #e8001c; font-weight: 700; }

/* ミニプログレスバー */
.mini-bar { height: 3px; background: #1a1a1a; margin-top: 4px; }
.mini-bar-fill { height: 100%; background: #e8001c; transition: width 0.6s; }

/* 最近のアクティビティ */
.activity-list { display: flex; flex-direction: column; gap: 6px; }
.activity-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.03);
  font-size: 13px;
  color: #555;
}
.activity-dot {
  width: 6px; height: 6px;
  background: #e8001c;
  flex-shrink: 0;
  clip-path: polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%);
}

/* 設定 */
.profile-settings {
  background: #0e0e12;
  border: 1px solid #1a1a1a;
  border-left: 4px solid #60a5fa;
  padding: 20px;
}

.settings-btn {
  padding: 10px 20px;
  background: transparent;
  border: 1px solid #333;
  color: #555;
  font-size: 12px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  cursor: pointer;
  transition: all 0.15s;
  clip-path: polygon(0 0, 100% 0, 94% 100%, 0 100%);
  margin-top: 8px;
  display: block;
}
.settings-btn:hover { border-color: #e8001c; color: #e8001c; }

@media (max-width: 600px) {
  .stats-overview { grid-template-columns: 1fr 1fr; }
  .user-info { flex-direction: column; text-align: center; }
}
</style>
