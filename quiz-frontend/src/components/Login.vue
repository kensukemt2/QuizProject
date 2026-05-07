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
  background: #060608;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

/* 背景スラッシュ */
.login-page::before {
  content: '';
  position: absolute;
  top: -10%; right: -5%;
  width: 45%;
  height: 130%;
  background: #e8001c;
  transform: skewX(-8deg);
  z-index: 0;
}
.login-page::after {
  content: '';
  position: absolute;
  inset: 0;
  background-image: radial-gradient(circle, rgba(255,255,255,0.04) 1px, transparent 1px);
  background-size: 24px 24px;
  z-index: 0;
  pointer-events: none;
}

.login-container {
  position: relative;
  z-index: 10;
  width: 100%;
  max-width: 420px;
  padding: 0 20px;
}

.login-box {
  background: #0e0e12;
  border: 1px solid #1a1a1a;
  border-top: 3px solid #e8001c;
  padding: 40px 36px;
  position: relative;
  overflow: hidden;
}

.login-box::before {
  content: '';
  position: absolute;
  top: 0; right: 0;
  width: 0; height: 0;
  border-style: solid;
  border-width: 0 40px 40px 0;
  border-color: transparent #060608 transparent transparent;
}

.login-box h1 {
  font-size: 28px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #f5f0e8;
  text-shadow: 3px 3px 0 #e8001c;
  margin-bottom: 28px;
  text-align: center;
}

/* 装飾サークル → 非表示 */
.decorative-circles { display: none; }

/* メッセージ */
.success-message {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(34,197,94,0.08);
  border-left: 3px solid #22c55e;
  padding: 12px 14px;
  margin-bottom: 20px;
  font-size: 13px;
  color: #22c55e;
}
.error-message {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(239,68,68,0.08);
  border-left: 3px solid #ef4444;
  padding: 12px 14px;
  margin-bottom: 20px;
  font-size: 13px;
  color: #ef4444;
}
.message-icon {
  width: 22px; height: 22px;
  border-radius: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 12px;
  flex-shrink: 0;
  clip-path: polygon(0 0, 100% 0, 85% 100%, 0 100%);
}
.success-message .message-icon { background: #22c55e; color: #fff; }
.error-message .message-icon { background: #ef4444; color: #fff; }

/* フォーム */
.login-form { display: flex; flex-direction: column; gap: 18px; }

.form-group { display: flex; flex-direction: column; gap: 6px; }

.form-group label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: #555;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.form-control {
  width: 100%;
  padding: 12px 14px 12px 40px;
  background: #0a0a0e;
  border: 1px solid #1e1e22;
  color: #f5f0e8;
  font-size: 14px;
  outline: none;
  transition: border-color 0.15s;
}
.form-control:focus { border-color: #e8001c; }
.form-control.error { border-color: #ef4444; }
.form-control::placeholder { color: #333; }

/* アイコン */
.input-icon {
  position: absolute;
  left: 14px;
  width: 16px; height: 16px;
  opacity: 0.3;
}
.user-icon::before { content: '👤'; font-size: 14px; }
.email-icon::before { content: '✉'; font-size: 14px; }
.password-icon::before { content: '🔒'; font-size: 13px; }

.toggle-password {
  position: absolute;
  right: 12px;
  background: transparent;
  border: none;
  color: #444;
  cursor: pointer;
  font-size: 13px;
  padding: 0;
}
.toggle-password:hover { color: #888; }

.error-text { font-size: 11px; color: #ef4444; letter-spacing: 0.05em; }

/* チェックボックス */
.form-check {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #555;
}
.form-check input[type="checkbox"] {
  accent-color: #e8001c;
  width: 14px; height: 14px;
}

/* リンク */
.forgot-link, .register-link a {
  color: #e8001c;
  text-decoration: none;
  font-size: 12px;
  letter-spacing: 0.05em;
  transition: color 0.15s;
}
.forgot-link:hover, .register-link a:hover { color: #ff1a35; }

.forgot-link { text-align: right; font-size: 11px; }

/* ボタン */
.login-btn {
  padding: 14px;
  background: #e8001c;
  color: #fff;
  border: none;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  cursor: pointer;
  transition: all 0.15s;
  clip-path: polygon(0 0, 100% 0, 97% 100%, 0 100%);
  box-shadow: 4px 4px 0 rgba(232,0,28,0.3);
  margin-top: 8px;
}
.login-btn:hover { background: #ff1a35; transform: translate(-2px,-2px); box-shadow: 6px 6px 0 rgba(232,0,28,0.4); }
.login-btn:disabled { opacity: 0.4; cursor: not-allowed; transform: none; }

.register-link {
  text-align: center;
  font-size: 12px;
  color: #444;
  margin-top: 8px;
  letter-spacing: 0.05em;
}

/* ローディング */
.loading-spinner {
  width: 16px; height: 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top: 2px solid #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  display: inline-block;
  margin-right: 6px;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
