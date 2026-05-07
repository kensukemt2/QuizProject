<template>
  <div class="contact">
    <!-- 背景グロー効果 -->
    <div class="background-glow"></div>
    
    <div class="content-container">
      <div class="contact-section">
        <h1>お問い合わせ</h1>
        <p class="contact-description">マジカルクイズに関するご質問、ご意見、ご要望がございましたら、下記フォームよりお気軽にお問い合わせください。</p>
        
        <!-- 成功メッセージ -->
        <div v-if="submitted" class="success-message">
          <div class="success-icon">✓</div>
          <h3>お問い合わせを受け付けました</h3>
          <p>ご連絡いただき、ありがとうございます。内容を確認の上、可能な限り迅速にご返信いたします。</p>
          <button @click="resetForm" class="new-inquiry-btn">新しいお問い合わせ</button>
        </div>
        
        <!-- お問い合わせフォーム -->
        <form v-else @submit.prevent="submitForm" class="contact-form">
          <div class="form-group">
            <label for="name" class="required">お名前</label>
            <input 
              type="text" 
              id="name" 
              v-model="form.name" 
              :class="{ 'error': errors.name }"
              placeholder="山田太郎"
              required
            />
            <span v-if="errors.name" class="error-message">{{ errors.name }}</span>
          </div>
          
          <div class="form-group">
            <label for="email" class="required">メールアドレス</label>
            <input 
              type="email" 
              id="email" 
              v-model="form.email" 
              :class="{ 'error': errors.email }"
              placeholder="example@email.com"
              required
            />
            <span v-if="errors.email" class="error-message">{{ errors.email }}</span>
          </div>
          
          <div class="form-group">
            <label for="category">お問い合わせ種別</label>
            <select id="category" v-model="form.category">
              <option value="general">一般的なお問い合わせ</option>
              <option value="bug">バグ報告</option>
              <option value="feature">機能要望</option>
              <option value="content">コンテンツに関して</option>
              <option value="account">アカウントに関して</option>
              <option value="other">その他</option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="subject" class="required">件名</label>
            <input 
              type="text" 
              id="subject" 
              v-model="form.subject" 
              :class="{ 'error': errors.subject }"
              placeholder="お問い合わせの件名をご入力ください"
              required
            />
            <span v-if="errors.subject" class="error-message">{{ errors.subject }}</span>
          </div>
          
          <div class="form-group">
            <label for="message" class="required">お問い合わせ内容</label>
            <textarea 
              id="message" 
              v-model="form.message" 
              :class="{ 'error': errors.message }"
              placeholder="お問い合わせ内容を詳しくご記入ください"
              rows="6"
              required
            ></textarea>
            <span v-if="errors.message" class="error-message">{{ errors.message }}</span>
            <div class="character-count">{{ form.message.length }}/1000文字</div>
          </div>
          
          <div class="form-group checkbox-group">
            <label class="checkbox-label">
              <input 
                type="checkbox" 
                v-model="form.consent"
                :class="{ 'error': errors.consent }"
                required
              />
              <span class="checkmark"></span>
              <router-link to="/privacy" target="_blank" class="privacy-link">プライバシーポリシー</router-link>に同意します
            </label>
            <span v-if="errors.consent" class="error-message">{{ errors.consent }}</span>
          </div>
          
          <div class="form-actions">
            <button type="submit" class="submit-btn" :disabled="submitting">
              <span v-if="submitting" class="spinner"></span>
              {{ submitting ? '送信中...' : '送信する' }}
            </button>
          </div>
        </form>
        
        <div class="contact-info">
          <h3>その他のご連絡方法</h3>
          <div class="info-cards">
            <div class="info-card">
              <div class="info-icon">📧</div>
              <h4>メール</h4>
              <p>contact@magical-quiz.com</p>
            </div>
            <div class="info-card">
              <div class="info-icon">⏰</div>
              <h4>対応時間</h4>
              <p>平日 9:00-18:00<br>（土日祝日を除く）</p>
            </div>
            <div class="info-card">
              <div class="info-icon">📱</div>
              <h4>SNS</h4>
              <p>@MagicalQuiz<br>（Twitter/X）</p>
            </div>
          </div>
        </div>
        
        <div class="back-to-home">
          <router-link to="/" class="home-btn">
            <span class="btn-icon">🏠</span>
            ホームに戻る
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ContactPage',
  data() {
    return {
      form: {
        name: '',
        email: '',
        category: 'general',
        subject: '',
        message: '',
        consent: false
      },
      errors: {},
      submitting: false,
      submitted: false
    }
  },
  mounted() {
    // ページタイトルを設定
    document.title = 'お問い合わせ | マジカルクイズ';
  },
  methods: {
    validateForm() {
      this.errors = {};
      
      if (!this.form.name.trim()) {
        this.errors.name = 'お名前を入力してください';
      }
      
      if (!this.form.email.trim()) {
        this.errors.email = 'メールアドレスを入力してください';
      } else if (!this.isValidEmail(this.form.email)) {
        this.errors.email = '有効なメールアドレスを入力してください';
      }
      
      if (!this.form.subject.trim()) {
        this.errors.subject = '件名を入力してください';
      }
      
      if (!this.form.message.trim()) {
        this.errors.message = 'お問い合わせ内容を入力してください';
      } else if (this.form.message.length > 1000) {
        this.errors.message = 'お問い合わせ内容は1000文字以内で入力してください';
      }
      
      if (!this.form.consent) {
        this.errors.consent = 'プライバシーポリシーに同意してください';
      }
      
      return Object.keys(this.errors).length === 0;
    },
    
    isValidEmail(email) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return emailRegex.test(email);
    },
    
    async submitForm() {
      if (!this.validateForm()) {
        return;
      }
      
      this.submitting = true;
      
      try {
        // 実際のAPIエンドポイントがある場合はここで送信
        // await this.sendContactForm(this.form);
        
        // デモ用の遅延
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // ローカルストレージに保存（デモ用）
        const contacts = JSON.parse(localStorage.getItem('contactForms') || '[]');
        contacts.push({
          ...this.form,
          timestamp: new Date().toISOString(),
          id: Date.now()
        });
        localStorage.setItem('contactForms', JSON.stringify(contacts));
        
        this.submitted = true;
        
      } catch (error) {
        console.error('お問い合わせの送信に失敗しました:', error);
        alert('送信に失敗しました。時間をおいて再度お試しください。');
      } finally {
        this.submitting = false;
      }
    },
    
    resetForm() {
      this.form = {
        name: '',
        email: '',
        category: 'general',
        subject: '',
        message: '',
        consent: false
      };
      this.errors = {};
      this.submitted = false;
      this.submitting = false;
    }
  },
  watch: {
    'form.message'(newValue) {
      if (newValue.length > 1000) {
        this.form.message = newValue.substring(0, 1000);
      }
    }
  }
}
</script>

<style scoped>
.contact {
  min-height: 100vh;
  background: #060608;
  color: #f5f0e8;
  position: relative;
  overflow: hidden;
  padding-bottom: 3rem;
}

.contact::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image: radial-gradient(circle, rgba(255,255,255,0.04) 1px, transparent 1px);
  background-size: 24px 24px;
  z-index: 0;
  pointer-events: none;
}

.background-glow {
  position: absolute;
  top: -10%; left: -5%;
  width: 40%;
  height: 130%;
  background: #e8001c;
  transform: skewX(-8deg);
  z-index: 0;
  opacity: 0.5;
}

.content-container {
  position: relative;
  z-index: 2;
  max-width: 700px;
  margin: 0 auto;
  padding: 40px 24px;
}

.contact-section h1 {
  font-size: 28px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #f5f0e8;
  text-shadow: 4px 4px 0 #e8001c;
  margin-bottom: 8px;
}
.contact-description {
  font-size: 13px;
  color: #555;
  line-height: 1.7;
  margin-bottom: 28px;
  border-left: 2px solid #e8001c;
  padding-left: 12px;
}

/* 送信完了 */
.success-message {
  background: #0e0e12;
  border: 1px solid #1a1a1a;
  border-left: 4px solid #22c55e;
  padding: 28px 24px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
}
.success-icon {
  width: 48px; height: 48px;
  background: #22c55e;
  display: flex; align-items: center; justify-content: center;
  font-size: 22px; font-weight: 700; color: #fff;
  clip-path: polygon(0 0, 100% 0, 85% 100%, 0 100%);
}
.success-message h3 { font-size: 18px; letter-spacing: 0.06em; color: #f5f0e8; }
.success-message p { font-size: 13px; color: #555; }
.new-inquiry-btn {
  padding: 10px 24px;
  background: transparent;
  border: 1px solid #333;
  color: #555;
  font-size: 12px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  cursor: pointer;
  transition: all 0.15s;
  clip-path: polygon(0 0, 100% 0, 94% 100%, 0 100%);
}
.new-inquiry-btn:hover { border-color: #e8001c; color: #e8001c; }

/* フォーム */
.contact-form {
  background: #0e0e12;
  border: 1px solid #1a1a1a;
  border-left: 4px solid #e8001c;
  padding: 28px 24px;
  display: flex;
  flex-direction: column;
  gap: 18px;
  position: relative;
  overflow: hidden;
}
.contact-form::after {
  content: '';
  position: absolute;
  top: 0; right: 0;
  width: 0; height: 0;
  border-style: solid;
  border-width: 0 40px 40px 0;
  border-color: transparent #060608 transparent transparent;
}

.form-group { display: flex; flex-direction: column; gap: 6px; }

.form-group label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: #555;
}
.required::after { content: ' *'; color: #e8001c; }

.form-control {
  padding: 12px 14px;
  background: #0a0a0e;
  border: 1px solid #1e1e22;
  color: #f5f0e8;
  font-size: 14px;
  outline: none;
  transition: border-color 0.15s;
  width: 100%;
}
.form-control:focus { border-color: #e8001c; }
.form-control.error { border-color: #ef4444; }
.form-control::placeholder { color: #333; }

textarea.form-control {
  resize: vertical;
  min-height: 120px;
  line-height: 1.6;
  font-family: 'Hiragino Kaku Gothic ProN', 'Noto Sans JP', sans-serif;
}

.error-message { font-size: 11px; color: #ef4444; letter-spacing: 0.05em; }
.char-count { font-size: 11px; color: #444; text-align: right; letter-spacing: 0.05em; }
.char-count.warning { color: #f5e642; }
.char-count.error { color: #ef4444; }

/* カテゴリ選択 */
.form-select {
  padding: 12px 36px 12px 14px;
  background: #0a0a0e;
  border: 1px solid #1e1e22;
  color: #f5f0e8;
  font-size: 14px;
  outline: none;
  appearance: none;
  cursor: pointer;
  transition: border-color 0.15s;
  width: 100%;
}
.form-select:focus { border-color: #e8001c; }
.select-wrapper { position: relative; }
.select-arrow {
  position: absolute;
  right: 12px; top: 50%;
  transform: translateY(-50%);
  font-size: 10px;
  color: #444;
  pointer-events: none;
}

/* 送信ボタン */
.submit-btn {
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
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
.submit-btn:hover { background: #ff1a35; transform: translate(-2px,-2px); box-shadow: 6px 6px 0 rgba(232,0,28,0.4); }
.submit-btn:disabled { opacity: 0.4; cursor: not-allowed; transform: none; }

.loading-spinner {
  width: 14px; height: 14px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top: 2px solid #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* 注意書き */
.form-note {
  font-size: 11px;
  color: #333;
  letter-spacing: 0.05em;
  line-height: 1.6;
}
.form-note a { color: #e8001c; text-decoration: none; }
</style>
