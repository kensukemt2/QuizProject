<template>
  <div class="register-page">
    <div class="register-container">
      <div class="register-box">
        <h1>ユーザー登録</h1>
        
        <!-- 装飾的要素 -->
        <div class="decorative-shapes">
          <div class="star star-1"></div>
          <div class="star star-2"></div>
          <div class="circle circle-1"></div>
          <div class="circle circle-2"></div>
        </div>
        
        <div v-if="error" class="error-message" role="alert">
          <div class="message-icon" aria-hidden="true">!</div>
          <p>{{ error }}</p>
        </div>

        <div v-if="successMessage" class="success-message" role="status">
          <div class="message-icon" aria-hidden="true">✓</div>
          <p>{{ successMessage }}</p>
        </div>
        
        <form @submit.prevent="handleRegister" class="register-form">
          <div class="form-group">
            <label for="username">ユーザー名</label>
            <div class="input-wrapper">
              <input
                type="text"
                id="username"
                v-model="userData.username"
                required
                class="form-control"
                placeholder="ユーザー名を入力"
                autocomplete="username"
              />
              <div class="input-icon user-icon"></div>
            </div>
          </div>
          
          <div class="form-group">
            <label for="email">メールアドレス</label>
            <div class="input-wrapper">
              <input
                type="email"
                id="email"
                v-model="userData.email"
                required
                class="form-control"
                placeholder="メールアドレスを入力"
                autocomplete="email"
              />
              <div class="input-icon email-icon"></div>
            </div>
          </div>
          
          <div class="form-group">
            <label for="password">パスワード</label>
            <div class="input-wrapper">
              <input
                type="password"
                id="password"
                v-model="userData.password"
                required
                minlength="8"
                class="form-control"
                placeholder="パスワードを入力"
                autocomplete="new-password"
                aria-describedby="password-requirements"
              />
              <div class="input-icon password-icon"></div>
            </div>
            <div class="password-hint" id="password-requirements">
              <h4>パスワードの条件:</h4>
              <ul>
                <li>8文字以上であること</li>
                <li>一般的でないパスワードを使用すること</li>
                <li>数字だけでなく文字も含めること</li>
                <li>ユーザー名と大きく異なること</li>
              </ul>
            </div>
          </div>
          
          <div class="form-group">
            <label for="password2">パスワード（確認）</label>
            <div class="input-wrapper">
              <input
                type="password"
                id="password2"
                v-model="userData.password2"
                required
                minlength="8"
                class="form-control"
                placeholder="パスワードを再入力"
                autocomplete="new-password"
              />
              <div class="input-icon password-confirm-icon"></div>
            </div>
          </div>
          
          <button type="submit" class="register-btn" :disabled="isLoading">
            <span v-if="isLoading" class="spinner"></span>
            <span>{{ isLoading ? '登録中...' : '登録する' }}</span>
          </button>
          
          <div class="login-link">
            <p>
              すでにアカウントをお持ちですか？
              <router-link to="/login">ログインはこちら</router-link>
            </p>
          </div>
        </form>
      </div>
    </div>
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
        
        if (err.response && err.response.data) {
          const errorData = err.response.data;
          this.error = this.parseErrorMessage(errorData);
        } else {
          this.error = '登録処理中にエラーが発生しました。後でもう一度お試しください。';
        }
      } finally {
        this.isLoading = false;
      }
    },
    // エラーメッセージの処理を関数化する
    parseErrorMessage(errorData) {
      if (!errorData) return '不明なエラーが発生しました';
      
      // キーとエラーメッセージのマッピング
      const errorTypes = {
        username: {
          'already exists': 'そのユーザー名は既に使用されています。'
        },
        email: {
          'already exists': 'そのメールアドレスは既に登録されています。'
        },
        password: {
          'too common': 'パスワードが一般的すぎます。別のパスワードを試してください。',
          'too short': 'パスワードが短すぎます。8文字以上必要です。',
          'entirely numeric': 'パスワードは数字だけでなく文字も含めてください。',
          'too similar': 'パスワードがユーザー名と似すぎています。'
        }
      };
      
      // 最初に見つかったエラーを返す
      for (const field in errorTypes) {
        if (errorData[field]) {
          const message = errorData[field][0];
          for (const key in errorTypes[field]) {
            if (message.includes(key)) {
              return errorTypes[field][key];
            }
          }
          return `${field}エラー: ${message}`;
        }
      }
      
      return '登録に失敗しました。入力内容を確認してください。';
    }
  }
};
</script>

<style scoped>
.register-page {
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
.register-page::before {
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
.register-page::after {
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

.register-container {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 500px;
}

.register-box {
  background-color: rgba(59, 130, 246, 0.7);
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  position: relative;
  overflow: hidden;
}

/* オレンジのトップバー */
.register-box::before {
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

/* 装飾的な形 */
.decorative-shapes {
  position: absolute;
  top: 0;
  right: 0;
  z-index: -1;
}

.star {
  position: absolute;
  opacity: 0.3;
}

.star-1 {
  top: 30px;
  right: 40px;
  width: 0;
  height: 0;
  transform: rotate(20deg);
  color: #FFD700;
  font-size: 30px;
}

.star-1::after {
  content: '★';
  position: absolute;
}

.star-2 {
  top: 60px;
  right: 70px;
  width: 0;
  height: 0;
  transform: rotate(-15deg);
  color: #FFD700;
  font-size: 20px;
}

.star-2::after {
  content: '★';
  position: absolute;
}

.circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.3;
}

.circle-1 {
  width: 40px;
  height: 40px;
  background-color: #F97316;
  top: 20px;
  right: 100px;
}

.circle-2 {
  width: 25px;
  height: 25px;
  background-color: #10B981;
  top: 70px;
  right: 30px;
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
.register-form {
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

.email-icon::before {
  content: '✉️';
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

.password-confirm-icon::before {
  content: '🔐';
  font-size: 20px;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

/* パスワードヒント */
.password-hint {
  background-color: rgba(255, 255, 255, 0.1);
  border-left: 3px solid #FACC15;
  border-radius: 0 10px 10px 0;
  padding: 10px 15px;
  margin-top: 10px;
}

.password-hint h4 {
  color: #FACC15;
  margin: 0 0 8px 0;
  font-size: 14px;
}

.password-hint ul {
  margin: 0;
  padding-left: 20px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 13px;
}

.password-hint li {
  margin-bottom: 4px;
}

/* 登録ボタン */
.register-btn {
  width: 100%;
  padding: 12px;
  background: linear-gradient(to bottom, #F97316, #EA580C);
  color: white;
  border: none;
  border-radius: 25px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  margin-top: 20px;
  position: relative;
  overflow: hidden;
  transition: all 0.3s;
  display: flex;
  justify-content: center;
  align-items: center;
}

.register-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 5px;
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 2.5px 2.5px 0 0;
}

.register-btn:hover:not([disabled]) {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
}

.register-btn:disabled {
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

/* ログインリンク */
.login-link {
  text-align: center;
  margin-top: 20px;
}

.login-link p {
  margin: 0;
  color: #FFFFFF;
  font-size: 14px;
}

.login-link a {
  color: #FACC15;
  text-decoration: none;
  font-weight: bold;
  position: relative;
  transition: all 0.3s;
}

.login-link a::after {
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

.login-link a:hover::after {
  transform: scaleX(1);
  transform-origin: bottom left;
}

/* レスポンシブ対応 */
@media (max-width: 480px) {
  .register-box {
    padding: 20px;
  }
  
  h1 {
    font-size: 24px;
  }
  
  .form-control {
    padding: 10px 15px 10px 40px;
    font-size: 14px;
  }
  
  .register-btn {
    padding: 10px;
  }
  
  .password-hint ul {
    padding-left: 15px;
  }
  
  .password-hint li {
    font-size: 12px;
  }
}
</style>