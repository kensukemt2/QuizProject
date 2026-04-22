<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-box">
        <h1>ログイン</h1>
        
        <!-- 装飾的要素 -->
        <div class="decorative-circles">
          <div class="circle circle-1"></div>
          <div class="circle circle-2"></div>
          <div class="circle circle-3"></div>
        </div>
        
        <!-- 成功メッセージ -->
        <div v-if="registrationSuccess" class="success-message" role="status">
          <div class="message-icon" aria-hidden="true">✓</div>
          <p>{{ registrationSuccess }}</p>
        </div>

        <!-- エラーメッセージ -->
        <div v-if="error" class="error-message" role="alert">
          <div class="message-icon" aria-hidden="true">!</div>
          <p>{{ error }}</p>
        </div>
        
        <form @submit.prevent="handleLogin" class="login-form">
          <div class="form-group">
            <label for="username">ユーザー名</label>
            <div class="input-wrapper">
              <input
                type="text"
                id="username"
                v-model="credentials.username"
                required
                class="form-control"
                placeholder="ユーザー名を入力"
                autocomplete="username"
                :aria-invalid="error ? 'true' : undefined"
              />
              <div class="input-icon user-icon"></div>
            </div>
          </div>
          
          <div class="form-group">
            <label for="password">パスワード</label>
            <div class="input-wrapper">
              <input
                type="password"
                id="password"
                v-model="credentials.password"
                required
                class="form-control"
                placeholder="パスワードを入力"
                autocomplete="current-password"
                :aria-invalid="error ? 'true' : undefined"
              />
              <div class="input-icon password-icon"></div>
            </div>
          </div>
          
          <button 
            type="submit" 
            class="login-btn"
            :disabled="isLoading"
          >
            <span v-if="isLoading" class="spinner"></span>
            <span>{{ isLoading ? 'ログイン中...' : 'ログイン' }}</span>
          </button>
          
          <div class="register-link">
            <div class="register-character">
              <div class="character-face"></div>
              <div class="character-eye left"></div>
              <div class="character-eye right"></div>
              <div class="character-mouth"></div>
            </div>
            <p>
              アカウントをお持ちでない方は
              <router-link to="/register">こちらから登録</router-link>
              してください
            </p>
          </div>
        </form>
      </div>
    </div>
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
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #3B82F6 0%, #1E40AF 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  position: relative;
  overflow: hidden;
}

/* グリッド線の装飾 */
.login-page::before {
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

/* 放射状グロー効果 */
.login-page::after {
  content: '';
  position: absolute;
  top: 15%;
  left: 50%;
  transform: translateX(-50%);
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(147, 197, 253, 0.6) 0%, rgba(30, 64, 175, 0) 70%);
  z-index: 0;
  pointer-events: none;
}

.login-container {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 450px;
}

.login-box {
  background-color: rgba(59, 130, 246, 0.7);
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  position: relative;
  overflow: hidden;
}

/* オレンジのトップバー */
.login-box::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 5px;
  background-color: #F97316;
  border-radius: 2.5px 2.5px 0 0;
}

h1 {
  text-align: center;
  margin: 0 0 30px 0;
  color: #FFFFFF;
  font-size: 28px;
  position: relative;
  font-weight: bold;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

h1::after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 80px;
  height: 3px;
  background-color: #F97316;
  border-radius: 1.5px;
}

/* 装飾的な円 */
.decorative-circles {
  position: absolute;
  top: 0;
  right: 0;
  z-index: -1;
}

.circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.3;
}

.circle-1 {
  width: 60px;
  height: 60px;
  background-color: #F97316;
  top: 20px;
  right: 20px;
}

.circle-2 {
  width: 40px;
  height: 40px;
  background-color: #FACC15;
  top: 70px;
  right: 60px;
}

.circle-3 {
  width: 30px;
  height: 30px;
  background-color: #10B981;
  top: 40px;
  right: 90px;
}

/* メッセージスタイル */
.success-message, .error-message {
  display: flex;
  align-items: center;
  border-radius: 10px;
  padding: 15px;
  margin-bottom: 20px;
}

.success-message {
  background-color: rgba(16, 185, 129, 0.2);
  border-left: 4px solid #10B981;
}

.error-message {
  background-color: rgba(239, 68, 68, 0.2);
  border-left: 4px solid #EF4444;
}

.message-icon {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  margin-right: 15px;
  font-weight: bold;
  font-size: 18px;
}

.success-message .message-icon {
  background-color: #10B981;
  color: white;
}

.error-message .message-icon {
  background-color: #EF4444;
  color: white;
}

.success-message p, .error-message p {
  margin: 0;
  color: white;
  font-size: 14px;
  flex: 1;
}

/* フォームスタイル */
.login-form {
  position: relative;
  z-index: 1;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
  color: #FFFFFF;
  font-size: 16px;
}

.input-wrapper {
  position: relative;
}

.form-control {
  width: 100%;
  padding: 12px 15px 12px 45px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 25px;
  background-color: rgba(30, 64, 175, 0.5);
  font-size: 16px;
  color: #FFFFFF;
  transition: all 0.3s;
}

.form-control::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

.form-control:focus {
  outline: none;
  border-color: #F97316;
  box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.3);
  background-color: rgba(30, 64, 175, 0.7);
}

.input-icon {
  position: absolute;
  top: 50%;
  left: 15px;
  transform: translateY(-50%);
  width: 24px;
  height: 24px;
  opacity: 0.7;
}

.user-icon::before {
  content: '👤';
  font-size: 20px;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.password-icon::before {
  content: '🔒';
  font-size: 20px;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

/* ログインボタン */
.login-btn {
  width: 100%;
  padding: 12px;
  background: linear-gradient(to bottom, #F97316, #EA580C);
  color: white;
  border: none;
  border-radius: 25px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  margin-top: 10px;
  position: relative;
  overflow: hidden;
  transition: all 0.3s;
  display: flex;
  justify-content: center;
  align-items: center;
}

.login-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 5px;
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 2.5px 2.5px 0 0;
}

.login-btn:hover:not([disabled]) {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
}

.login-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.spinner {
  display: inline-block;
  width: 18px;
  height: 18px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top: 3px solid white;
  border-radius: 50%;
  margin-right: 10px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 登録リンク */
.register-link {
  text-align: center;
  margin-top: 25px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.register-link p {
  margin: 10px 0 0;
  color: #FFFFFF;
  font-size: 14px;
}

.register-link a {
  color: #FACC15;
  text-decoration: none;
  font-weight: bold;
  position: relative;
  transition: all 0.3s;
}

.register-link a::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 100%;
  height: 2px;
  background-color: #FACC15;
  transform: scaleX(0);
  transform-origin: bottom right;
  transition: transform 0.3s;
}

.register-link a:hover::after {
  transform: scaleX(1);
  transform-origin: bottom left;
}

/* キャラクター装飾 */
.register-character {
  width: 60px;
  height: 60px;
  position: relative;
}

.character-face {
  width: 60px;
  height: 60px;
  background-color: #FACC15;
  border-radius: 50%;
  position: relative;
}

.character-eye {
  width: 12px;
  height: 12px;
  background-color: white;
  border-radius: 50%;
  position: absolute;
  top: 18px;
}

.character-eye::after {
  content: '';
  width: 6px;
  height: 6px;
  background-color: #1E40AF;
  border-radius: 50%;
  position: absolute;
  top: 3px;
  left: 4px;
}

.character-eye.left {
  left: 15px;
}

.character-eye.right {
  right: 15px;
}

.character-mouth {
  position: absolute;
  bottom: 15px;
  left: 50%;
  transform: translateX(-50%);
  width: 20px;
  height: 10px;
  border-bottom: 2px solid #1E40AF;
  border-radius: 0 0 30px 30px;
}

/* レスポンシブ対応 */
@media (max-width: 480px) {
  .login-box {
    padding: 20px;
  }
  
  h1 {
    font-size: 24px;
  }
  
  .form-control {
    padding: 10px 15px 10px 40px;
    font-size: 14px;
  }
  
  .login-btn {
    padding: 10px;
  }
}
</style>