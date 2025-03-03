<template>
    <div class="profile-container">
      <h2>プロフィール</h2>
      
      <div v-if="loading" class="loading">
        <p>読み込み中...</p>
      </div>
      
      <div v-else class="profile-content">
        <div class="user-info">
          <h3>{{ user.username }}</h3>
          <p>{{ user.email }}</p>
        </div>
        
        <div class="stats-overview">
          <div class="stat-card">
            <div class="stat-value">{{ stats.total_attempts }}</div>
            <div class="stat-label">クイズ挑戦回数</div>
          </div>
          
          <div class="stat-card">
            <div class="stat-value">{{ stats.total_categories_played }}</div>
            <div class="stat-label">プレイしたカテゴリー</div>
          </div>
          
          <div class="stat-card">
            <div class="stat-value">{{ Math.round(stats.avg_percentage) }}%</div>
            <div class="stat-label">平均正答率</div>
          </div>
          
          <div class="stat-card">
            <div class="stat-value">{{ stats.best_category || '-' }}</div>
            <div class="stat-label">最も得意なカテゴリー</div>
          </div>
        </div>
        
        <div v-if="stats.category_stats.length > 0" class="category-performance">
          <h3>カテゴリー別成績</h3>
          
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
                <td>{{ category.name }}</td>
                <td>{{ category.attempts_count }}回</td>
                <td>{{ category.best_score }}</td>
                <td>{{ Math.round(category.avg_percentage) }}%</td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <div v-else class="no-stats">
          <p>まだクイズの記録がありません。クイズに挑戦して記録を作りましょう！</p>
          <router-link to="/quiz" class="start-quiz-btn">クイズを始める</router-link>
        </div>
        
        <div class="recent-activity">
          <h3>最近のアクティビティ</h3>
          
          <div v-if="recentAttempts.length === 0" class="no-activity">
            <p>最近のアクティビティはありません。</p>
          </div>
          
          <div v-else class="activity-list">
            <div v-for="attempt in recentAttempts" :key="attempt.id" class="activity-item">
              <div class="activity-header">
                <span class="category">{{ attempt.category_name }}</span>
                <span class="date">{{ formatDate(attempt.created_at) }}</span>
              </div>
              <div class="activity-score">
                スコア: {{ attempt.score }}/{{ attempt.total_questions }} ({{ Math.round(attempt.percentage) }}%)
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
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
        loading: true
      };
    },
    computed: {
      ...mapGetters('auth', ['user']),
    },
    created() {
      this.fetchUserStats();
      this.fetchRecentActivity();
    },
    methods: {
      async fetchUserStats() {
        try {
          const response = await axios.get('http://localhost:8000/api/user/stats/');
          this.stats = response.data;
        } catch (error) {
          console.error('ユーザー統計の取得に失敗しました:', error);
        } finally {
          this.loading = false;
        }
      },
      async fetchRecentActivity() {
        try {
          const response = await axios.get('http://localhost:8000/api/quiz/history/?limit=5');
          this.recentAttempts = response.data.slice(0, 5); // 最新5件のみ表示
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
  }
  
  h2 {
    text-align: center;
    margin-bottom: 20px;
  }
  
  .loading {
    text-align: center;
    margin-top: 50px;
  }
  
  .profile-content {
    background-color: #f5f5f5;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  }
  
  .user-info {
    text-align: center;
    margin-bottom: 20px;
    padding-bottom: 20px;
    border-bottom: 1px solid #ddd;
  }
  
  .user-info h3 {
    margin: 0 0 10px 0;
    font-size: 1.5em;
  }
  
  .stats-overview {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    margin-bottom: 30px;
  }
  
  .stat-card {
    width: calc(25% - 15px);
    background-color: white;
    border-radius: 8px;
    padding: 15px;
    text-align: center;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  }
  
  .stat-value {
    font-size: 1.8em;
    font-weight: bold;
    color: #2196F3;
    margin-bottom: 5px;
  }
  
  .stat-label {
    font-size: 0.9em;
    color: #666;
  }
  
  .category-performance {
    margin-bottom: 30px;
  }
  
  .category-performance h3 {
    margin-bottom: 15px;
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
  
  .no-stats, .no-activity {
    text-align: center;
    padding: 20px 0;
  }
  
  .start-quiz-btn {
    display: inline-block;
    margin-top: 15px;
    padding: 10px 15px;
    background-color: #4CAF50;
    color: white;
    text-decoration: none;
    border-radius: 4px;
  }
  
  .recent-activity h3 {
    margin-bottom: 15px;
  }
  
  .activity-item {
    background-color: white;
    border-radius: 6px;
    padding: 15px;
    margin-bottom: 10px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  }
  
  .activity-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 5px;
  }
  
  .category {
    font-weight: bold;
  }
  
  .date {
    color: #777;
    font-size: 0.9em;
  }
  
  @media (max-width: 768px) {
    .stat-card {
      width: calc(50% - 10px);
      margin-bottom: 15px;
    }
  }
  
  @media (max-width: 480px) {
    .stat-card {
      width: 100%;
      margin-bottom: 15px;
    }
  }
  </style>