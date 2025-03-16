<template>
  <div class="home">
    <h1>4択クイズアプリへようこそ</h1>
    <p>クイズに挑戦して知識を試してみましょう！</p>
    
    <div class="quiz-options">
      <!-- ログイン済みユーザー向け -->
      <div v-if="isAuthenticated" class="authenticated-options">
        <button class="btn primary" @click="startQuiz">クイズを始める</button>
        <div class="user-stats" v-if="user">
          <p>こんにちは、{{ user.username }}さん</p>
          <p>これまでの挑戦回数: {{ userStats.total_attempts || 0 }}</p>
        </div>
      </div>
      
      <!-- ゲストユーザー向け -->
      <div v-else class="guest-options">
        <button class="btn primary" @click="startGuestQuiz">ゲストとしてクイズを始める</button>
        <button class="btn secondary" @click="goToLogin">ログインする</button>
        
        <div class="guest-info">
          <h3>ログインするメリット</h3>
          <ul>
            <li>クイズの成績を保存できる</li>
            <li>ランキングに参加できる</li>
            <li>履歴から過去の回答を確認できる</li>
            <li>カスタマイズされたクイズに挑戦できる</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
  name: 'HomePage',
  data() {
    return {
      userStats: {
        total_attempts: 0
      }
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
    goToLogin() {
      this.$router.push('/login');
    },
    async fetchUserStats() {
      if (!this.isAuthenticated) return;
      
      try {
        // ログインユーザーの場合、統計情報を取得
        const response = await this.$store.dispatch('user/fetchStats');
        if (response) {
          this.userStats = response;
        }
      } catch (error) {
        console.error('ユーザー統計の取得に失敗:', error);
      }
    }
  },
  mounted() {
    this.fetchUserStats();
  }
}
</script>

<style scoped>
.home {
  text-align: center;
  padding: 2rem;
}

h1 {
  font-size: 2.5rem;
  color: #2c3e50;
  margin-bottom: 1rem;
}

.quiz-options {
  margin-top: 3rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.btn {
  padding: 0.8rem 2rem;
  font-size: 1.2rem;
  border-radius: 4px;
  cursor: pointer;
  margin: 0.5rem;
  border: none;
  transition: all 0.3s ease;
}

.primary {
  background-color: #42b983;
  color: white;
}

.primary:hover {
  background-color: #3aa876;
}

.secondary {
  background-color: #2c3e50;
  color: white;
}

.secondary:hover {
  background-color: #1e2a37;
}

.guest-info {
  margin-top: 2rem;
  background-color: #f5f5f5;
  padding: 1.5rem;
  border-radius: 8px;
  max-width: 500px;
  text-align: left;
}

.guest-info ul {
  padding-left: 1.2rem;
}

.guest-info li {
  margin: 0.5rem 0;
}

.user-stats {
  margin-top: 1.5rem;
  color: #666;
}
</style>