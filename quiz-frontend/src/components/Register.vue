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
  background: #060608;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  padding: 40px 0;
}

.register-page::before {
  content: '';
  position: absolute;
  top: -10%; left: -5%;
  width: 40%;
  height: 130%;
  background: #e8001c;
  transform: skewX(-8deg);
  z-index: 0;
}
.register-page::after {
  content: '';
  position: absolute;
  inset: 0;
  background-image: radial-gradient(circle, rgba(255,255,255,0.04) 1px, transparent 1px);
  background-size: 24px 24px;
  z-index: 0;
  pointer-events: none;
}

.register-container {
  position: relative;
  z-index: 10;
  width: 100%;
  max-width: 460px;
  padding: 0 20px;
}

.register-box {
  background: #0e0e12;
  border: 1px solid #1a1a1a;
  border-top: 3px solid #e8001c;
  padding: 40px 36px;
  position: relative;
  overflow: hidden;
}

.register-box::before {
  content: '';
  position: absolute;
  top: 0; right: 0;
  width: 0; height: 0;
  border-style: solid;
  border-width: 0 40px 40px 0;
  border-color: transparent #060608 transparent transparent;
}

.register-box h1 {
  font-size: 26px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #f5f0e8;
  text-shadow: 3px 3px 0 #e8001c;
  margin-bottom: 28px;
  text-align: center;
}

.decorative-shapes { display: none; }
.star, .circle { display: none; }

/* メッセージ */
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
.message-icon {
  width: 22px; height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 12px;
  flex-shrink: 0;
  clip-path: polygon(0 0, 100% 0, 85% 100%, 0 100%);
}
.error-message .message-icon { background: #ef4444; color: #fff; }
.success-message .message-icon { background: #22c55e; color: #fff; }

/* フォーム */
.register-form { display: flex; flex-direction: column; gap: 16px; }
.form-group { display: flex; flex-direction: column; gap: 6px; }

.form-group label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: #555;
}
.required::after { content: ' *'; color: #e8001c; }

.input-wrapper { position: relative; display: flex; align-items: center; }

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

.input-icon { position: absolute; left: 14px; width: 16px; height: 16px; opacity: 0.3; }
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
}
.toggle-password:hover { color: #888; }

.error-text { font-size: 11px; color: #ef4444; }

/* パスワード強度 */
.password-strength { display: flex; flex-direction: column; gap: 4px; }
.strength-bar {
  height: 3px;
  background: #1a1a1a;
  position: relative;
  overflow: hidden;
}
.strength-fill {
  height: 100%;
  transition: width 0.3s;
}
.strength-fill.weak { background: #ef4444; width: 33%; }
.strength-fill.medium { background: #f5e642; width: 66%; }
.strength-fill.strong { background: #22c55e; width: 100%; }
.strength-label { font-size: 11px; color: #555; }

/* 利用規約 */
.terms-group {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 12px;
  color: #555;
}
.terms-group input[type="checkbox"] { accent-color: #e8001c; margin-top: 2px; flex-shrink: 0; }
.terms-group a { color: #e8001c; text-decoration: none; }
.terms-group a:hover { color: #ff1a35; }

/* ボタン */
.register-btn {
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
.register-btn:hover { background: #ff1a35; transform: translate(-2px,-2px); }
.register-btn:disabled { opacity: 0.4; cursor: not-allowed; transform: none; }

.login-link {
  text-align: center;
  font-size: 12px;
  color: #444;
  margin-top: 8px;
  letter-spacing: 0.05em;
}
.login-link a { color: #e8001c; text-decoration: none; }
.login-link a:hover { color: #ff1a35; }

.loading-spinner {
  width: 14px; height: 14px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top: 2px solid #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  display: inline-block;
  margin-right: 6px;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
