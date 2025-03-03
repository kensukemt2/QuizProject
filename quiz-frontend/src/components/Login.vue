<template>
    <div class="login-container">
      <div class="form-container">
        <h2>ログイン</h2>
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
        <form @submit.prevent="login">
          <div class="form-group">
            <label for="username">ユーザー名</label>
            <input 
              id="username" 
              v-model="loginForm.username" 
              type="text" 
              required
            />
          </div>
          
          <div class="form-group">
            <label for="password">パスワード</label>
            <input 
              id="password" 
              v-model="loginForm.password" 
              type="password" 
              required
            />
          </div>
          
          <button type="submit" :disabled="loading" class="submit-btn">
            {{ loading ? 'ログイン中...' : 'ログイン' }}
          </button>
        </form>
        
        <div class="form-footer">
          <p>アカウントをお持ちでないですか？ <router-link to="/register">登録する</router-link></p>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { mapActions } from 'vuex';
  
  export default {
    name: 'LoginComponent',
    data() {
      return {
        loginForm: {
          username: '',
          password: ''
        },
        loading: false,
        error: null
      };
    },
    methods: {
      ...mapActions('auth', ['login']),
      async handleLogin() {
        this.loading = true;
        this.error = null;
        
        try {
          await this.login(this.loginForm);
          this.$router.push({ name: 'quiz' });
        } catch (err) {
          this.error = err.response?.data?.detail || 'ログインに失敗しました。認証情報を確認してください。';
        } finally {
          this.loading = false;
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
    background-color: #ffebee;
    color: #f44336;
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