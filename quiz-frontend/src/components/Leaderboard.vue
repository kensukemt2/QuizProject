<template>
    <div class="leaderboard-container">
      <h2>リーダーボード</h2>
      
      <div class="filter-section">
        <label for="category-filter">カテゴリーフィルター:</label>
        <select id="category-filter" v-model="selectedCategory" @change="fetchLeaderboard">
          <option :value="null">すべてのカテゴリー</option>
          <option v-for="category in categories" :key="category.id" :value="category.id">
            {{ category.name }}
          </option>
        </select>
      </div>
      
      <div v-if="loading" class="loading">
        <p>読み込み中...</p>
      </div>
      
      <div v-else>
        <div v-if="leaderboardData.length === 0" class="no-data">
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
              <tr v-for="(user, index) in leaderboardData" :key="user.id" :class="{ 'current-user': user.id === currentUserId }">
                <td class="rank">{{ index + 1 }}</td>
                <td class="username">
                  {{ user.username }}
                  <span v-if="user.id === currentUserId" class="current-user-tag">あなた</span>
                </td>
                <td class="attempts">
                  {{ selectedCategory ? user.category_attempts : user.total_attempts }}回
                </td>
                <td class="percentage">
                  {{ selectedCategory ? user.category_percentage : user.avg_percentage }}%
                </td>
                <td class="score">
                  {{ selectedCategory ? user.category_score : user.total_score }} / 
                  {{ selectedCategory ? user.category_questions : user.total_questions }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <div class="your-rank" v-if="currentUserRank">
          <p>あなたの順位: <strong>{{ currentUserRank }}位</strong> / {{ leaderboardData.length }}人中</p>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  import { mapGetters } from 'vuex';
  
  export default {
    name: 'LeaderboardComponent',
    data() {
      return {
        leaderboardData: [],
        categories: [],
        selectedCategory: null,
        loading: true
      };
    },
    computed: {
      ...mapGetters('auth', ['user']),
      currentUserId() {
        return this.user ? this.user.id : null;
      },
      currentUserRank() {
        if (!this.currentUserId) return null;
        
        const userIndex = this.leaderboardData.findIndex(user => user.id === this.currentUserId);
        return userIndex !== -1 ? userIndex + 1 : null;
      }
    },
    created() {
      this.fetchCategories();
      this.fetchLeaderboard();
    },
    methods: {
      async fetchCategories() {
        try {
          const response = await axios.get('http://localhost:8000/api/categories/');
          this.categories = response.data;
        } catch (error) {
          console.error('カテゴリの取得に失敗しました:', error);
        }
      },
      async fetchLeaderboard() {
        this.loading = true;
        try {
          let url = 'http://localhost:8000/api/leaderboard/';
          if (this.selectedCategory) {
            url += `?category=${this.selectedCategory}`;
          }
          
          const response = await axios.get(url);
          this.leaderboardData = response.data;
          this.loading = false;
        } catch (error) {
          console.error('リーダーボードデータの取得に失敗しました:', error);
          this.loading = false;
        }
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
  </style>