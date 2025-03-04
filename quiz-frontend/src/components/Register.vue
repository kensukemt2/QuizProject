<template>
  <div class="register-container">
    <h1>ユーザー登録</h1>
    
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
    
    <form @submit.prevent="handleRegister" class="register-form">
      <div class="form-group">
        <label for="username">ユーザー名</label>
        <input 
          type="text" 
          id="username" 
          v-model="userData.username" 
          required 
          class="form-control"
        />
      </div>
      
      <div class="form-group">
        <label for="email">メールアドレス</label>
        <input 
          type="email" 
          id="email" 
          v-model="userData.email" 
          required
          class="form-control" 
        />
      </div>
      
      <div class="form-group">
        <label for="password">パスワード</label>
        <input 
          type="password" 
          id="password" 
          v-model="userData.password" 
          required
          minlength="8"
          class="form-control" 
        />
      </div>
      
      <div class="form-group">
        <label for="password2">パスワード（確認）</label>
        <input 
          type="password" 
          id="password2" 
          v-model="userData.password2" 
          required
          minlength="8"
          class="form-control" 
        />
      </div>
      
      <button type="submit" class="btn btn-primary" :disabled="isLoading">
        {{ isLoading ? '登録中...' : '登録する' }}
      </button>
      
      <p class="login-link">
        すでにアカウントをお持ちですか？
        <router-link to="/login">ログインはこちら</router-link>
      </p>
    </form>
  </div>
</template>

<script>
import { mapActions } from 'vuex';

export default {
  name: 'RegisterPage',
  data() {
    return {
      userData: {
        username: '',
        email: '',
        password: '',
        password2: ''
      },
      error: null,
      isLoading: false
    };
  },
  methods: {
    ...mapActions('auth', ['register']),
    async handleRegister() {
      // パスワード確認
      if (this.userData.password !== this.userData.password2) {
        this.error = 'パスワードが一致しません';
        return;
      }
      
      this.isLoading = true;
      this.error = null;
      
      try {
        // 登録処理
        const success = await this.register(this.userData);
        
        if (success) {
          // 登録成功時
          this.$router.push('/login');
        } else {
          this.error = '登録に失敗しました';
        }
      } catch (err) {
        console.error('登録エラー:', err);
        this.error = '登録に失敗しました。入力内容を確認してください。';
      } finally {
        this.isLoading = false;
      }
    }
  }
};
</script>