<template>
  <div class="login-container">
    <h1>ログイン</h1>
    
    <!-- 成功メッセージ -->
    <div v-if="registrationSuccess" class="success-message">
      {{ registrationSuccess }}
    </div>
    
    <!-- エラーメッセージ -->
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
    
    <form @submit.prevent="handleLogin" class="login-form">
      <div class="form-group">
        <label for="username">ユーザー名</label>
        <input 
          type="text" 
          id="username" 
          v-model="credentials.username" 
          required 
          class="form-control"
        />
      </div>
      
      <div class="form-group">
        <label for="password">パスワード</label>
        <input 
          type="password" 
          id="password" 
          v-model="credentials.password" 
          required
          class="form-control" 
        />
      </div>
      
      <button 
        type="submit" 
        class="login-btn"
        :disabled="isLoading"
      >
        {{ isLoading ? 'ログイン中...' : 'ログイン' }}
      </button>
      
      <p class="register-link">
        アカウントをお持ちでない方は
        <router-link to="/register">こちらから登録</router-link>
        してください
      </p>
    </form>
  </div>
</template>

<script>
import { mapActions } from 'vuex';
import { useToast } from 'vue-toastification';

export default {
  name: 'LoginPage',
  setup() {
    const toast = useToast();
    return { toast };
  },
  data() {
    return {
      credentials: {
        username: '',
        password: ''
      },
      error: null,
      isLoading: false,
      registrationSuccess: null
    };
  },
  created() {
    // URLクエリパラメータから登録成功情報を取得
    if (this.$route.query.registered === 'true') {
      const username = this.$route.query.username || 'ユーザー';
      this.registrationSuccess = `${username}さん、登録完了しました！以下のフォームからログインしてください。`;
    }
  },
  methods: {
    ...mapActions('auth', ['login']),
    async handleLogin() {
      this.isLoading = true;
      this.error = null;
      
      try {
        const success = await this.login(this.credentials);
        
        if (success) {
          this.toast.success('ログインしました！');
          this.$router.push('/');
        } else {
          this.error = 'ログインに失敗しました。ユーザー名とパスワードを確認してください。';
          this.toast.error('ログインに失敗しました');
        }
      } catch (err) {
        console.error('ログインエラー:', err);
        this.error = 'ログインに失敗しました。ユーザー名とパスワードを確認してください。';
        this.toast.error('ログインに失敗しました');
      } finally {
        this.isLoading = false;
      }
    }
  }
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 70vh;
}

.form-container {
  background-color: #f5f5f5;
  border-radius: 10px;
  padding: 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

h2 {
  text-align: center;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.submit-btn {
  width: 100%;
  padding: 12px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  margin-top: 10px;
}

.submit-btn:hover:not([disabled]) {
  background-color: #45a049;
}

.submit-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.error-message {
  color: #dc3545;
  background-color: #f8d7da;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 15px;
}

.success-message {
  color: #28a745;
  background-color: #d4edda;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 15px;
}

.form-footer {
  text-align: center;
  margin-top: 20px;
}

.form-footer a {
  color: #2196F3;
  text-decoration: none;
}

.form-footer a:hover {
  text-decoration: underline;
}
</style>