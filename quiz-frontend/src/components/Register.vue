<template>
  <div class="register-container">
    <h1>ユーザー登録</h1>
    
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
    
    <div v-if="successMessage" class="success-message">
      {{ successMessage }}
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
        <small class="password-hint">
          パスワードの条件:
          <ul>
            <li>8文字以上であること</li>
            <li>一般的でないパスワードを使用すること</li>
            <li>数字だけでなく文字も含めること</li>
            <li>ユーザー名と大きく異なること</li>
          </ul>
        </small>
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
      successMessage: null,
      isLoading: false
    };
  },
  methods: {
    ...mapActions('auth', ['register']),
    async handleRegister() {
      if (this.userData.password !== this.userData.password2) {
        this.error = 'パスワードが一致しません';
        return;
      }
      
      this.isLoading = true;
      this.error = null;
      
      try {
        console.log('登録処理を開始します', this.userData);
        const success = await this.register(this.userData);
        
        if (success) {
          // 成功メッセージを設定
          this.successMessage = `${this.userData.username}さんのアカウント登録に成功しました！ログインページに移動します...`;
          this.error = null;
          
          // 3秒後にログインページへリダイレクト
          setTimeout(() => {
            this.$router.push({
              path: '/login',
              query: { registered: 'true', username: this.userData.username }
            });
          }, 3000);
        } else {
          // エラーがfalseを返した場合の処理
          this.error = 'ユーザー登録に失敗しました';
          this.successMessage = null;
        }
      } catch (err) {
        this.successMessage = null;
        console.error('登録エラーの詳細:', err);
        
        if (err.response && err.response.data) {
          const errorData = err.response.data;
          
          // ユーザー名エラー
          if (errorData.username) {
            if (errorData.username[0].includes('already exists')) {
              this.error = 'そのユーザー名は既に使用されています。';
            } else {
              this.error = `ユーザー名エラー: ${errorData.username[0]}`;
            }
          }
          // メールエラー
          else if (errorData.email) {
            if (errorData.email[0].includes('already exists')) {
              this.error = 'そのメールアドレスは既に登録されています。';
            } else {
              this.error = `メールエラー: ${errorData.email[0]}`;
            }
          }
          // パスワードエラー
          else if (errorData.password) {
            const pwError = errorData.password[0];
            if (pwError.includes('too common')) {
              this.error = 'パスワードが一般的すぎます。別のパスワードを試してください。';
            } else if (pwError.includes('too short')) {
              this.error = 'パスワードが短すぎます。8文字以上必要です。';
            } else if (pwError.includes('entirely numeric')) {
              this.error = 'パスワードは数字だけでなく文字も含めてください。';
            } else if (pwError.includes('too similar')) {
              this.error = 'パスワードがユーザー名と似すぎています。';
            } else {
              this.error = `パスワードエラー: ${pwError}`;
            }
          }
          // パスワード確認エラー
          else if (errorData.password2) {
            this.error = `パスワード確認エラー: ${errorData.password2[0]}`;
          }
          // その他のエラー
          else {
            this.error = '登録に失敗しました。入力内容を確認してください。';
          }
        } else {
          this.error = '登録処理中にエラーが発生しました。後でもう一度お試しください。';
        }
      } finally {
        this.isLoading = false;
      }
    }
  }
};
</script>

<style scoped>
.password-hint {
  display: block;
  color: #666;
  font-size: 0.85em;
  margin-top: 5px;
}

.success-message {
  padding: 10px 15px;
  background-color: #dff0d8;
  border-left: 4px solid #5cb85c;
  color: #3c763d;
  margin-bottom: 20px;
  border-radius: 4px;
}

.error-message {
  padding: 10px 15px;
  background-color: #f8d7da;
  border-left: 4px solid #dc3545;
  color: #721c24;
  margin-bottom: 20px;
  border-radius: 4px;
}
</style>