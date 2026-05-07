<!-- src/components/Navbar.vue -->
<template>
  <nav class="navbar" aria-label="メインナビゲーション">
    <div class="grid-lines"></div>
    <div class="glow-effect"></div>
    
    <div class="logo">
      <div class="logo-box">
        <span class="logo-text">Q</span>
      </div>
      <router-link to="/" class="site-name">マジカルクイズ</router-link>
    </div>
    
    <div class="nav-links">
      <template v-if="isAuthenticated">
        <router-link to="/quiz" class="nav-link" active-class="nav-active">
          <div class="nav-btn">クイズ</div>
        </router-link>
        <router-link to="/history" class="nav-link" active-class="nav-active">
          <div class="nav-btn">履歴</div>
        </router-link>
        <router-link to="/leaderboard" class="nav-link" active-class="nav-active">
          <div class="nav-btn">ランキング</div>
        </router-link>
        <router-link to="/profile" class="nav-link" active-class="nav-active">
          <div class="nav-btn">プロフィール</div>
        </router-link>
        
        <div class="dropdown" @mouseover="showDropdown = true" @mouseleave="showDropdown = false" @keydown.escape="showDropdown = false">
          <button type="button" class="nav-btn dropdown-trigger" aria-haspopup="true" :aria-expanded="showDropdown.toString()" @click="showDropdown = !showDropdown" @keydown.enter.prevent="showDropdown = !showDropdown" @keydown.space.prevent="showDropdown = !showDropdown">
            情報
            <span class="dropdown-arrow" aria-hidden="true">▼</span>
          </button>
          <div class="dropdown-menu" :class="{ 'show': showDropdown }" role="menu">
            <router-link to="/about" class="dropdown-item" role="menuitem">運営者情報</router-link>
            <router-link to="/contact" class="dropdown-item" role="menuitem">お問い合わせ</router-link>
            <router-link to="/privacy" class="dropdown-item" role="menuitem">プライバシーポリシー</router-link>
          </div>
        </div>
        
        <div class="user-profile" v-if="currentUser">
          <div class="user-avatar">
            {{ currentUser.username ? currentUser.username.charAt(0).toUpperCase() : 'U' }}
          </div>
          <span class="user-name">{{ currentUser.username }}さん</span>
        </div>
        
        <button class="logout-btn" @click="handleLogout">
          ログアウト
          <span class="logout-icon">⟲</span>
        </button>
      </template>
      <template v-else>
        <div class="dropdown" @mouseover="showGuestDropdown = true" @mouseleave="showGuestDropdown = false" @keydown.escape="showGuestDropdown = false">
          <button type="button" class="nav-btn dropdown-trigger" aria-haspopup="true" :aria-expanded="showGuestDropdown.toString()" @click="showGuestDropdown = !showGuestDropdown" @keydown.enter.prevent="showGuestDropdown = !showGuestDropdown" @keydown.space.prevent="showGuestDropdown = !showGuestDropdown">
            情報
            <span class="dropdown-arrow" aria-hidden="true">▼</span>
          </button>
          <div class="dropdown-menu" :class="{ 'show': showGuestDropdown }" role="menu">
            <router-link to="/about" class="dropdown-item" role="menuitem">運営者情報</router-link>
            <router-link to="/contact" class="dropdown-item" role="menuitem">お問い合わせ</router-link>
            <router-link to="/privacy" class="dropdown-item" role="menuitem">プライバシーポリシー</router-link>
          </div>
        </div>
        <router-link to="/login" class="auth-btn login">ログイン</router-link>
        <router-link to="/register" class="auth-btn register">登録</router-link>
      </template>
    </div>
  </nav>
</template>

<script>
import { mapGetters, mapActions } from 'vuex';

export default {
  name: 'SiteNavigation',
  data() {
    return {
      showDropdown: false,
      showGuestDropdown: false
    }
  },
  computed: {
    ...mapGetters('auth', ['isAuthenticated', 'currentUser'])
  },
  methods: {
    ...mapActions('auth', ['logout']),
    async handleLogout() {
      await this.logout();
      this.$router.push('/login');
    }
  }
};
</script>

<style scoped>
:root {
  --red: #e8001c;
  --black: #060608;
  --dark: #0e0e12;
  --white: #f5f0e8;
  --yellow: #f5e642;
}

.navbar {
  display: flex;
  align-items: stretch;
  height: 56px;
  background: rgba(6,6,8,0.97);
  border-bottom: 2px solid #1a1a1a;
  position: sticky;
  top: 0;
  z-index: 1000;
  overflow: visible;
  padding: 0;
}

/* グリッド線・グロー非表示 */
.grid-lines, .glow-effect { display: none; }

/* 赤いボトムライン */
.navbar::after {
  content: '';
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 2px;
  background: var(--red);
}

/* ロゴ */
.logo {
  display: flex;
  align-items: center;
  margin-right: auto;
  padding: 0 24px;
  z-index: 10;
}

.logo-box {
  width: 40px;
  height: 100%;
  background: var(--red);
  display: flex;
  align-items: center;
  justify-content: center;
  clip-path: polygon(0 0, 85% 0, 100% 100%, 0 100%);
  padding-right: 6px;
  border-radius: 0;
}

.logo-text {
  font-size: 24px;
  font-weight: 700;
  color: #fff;
}

.site-name {
  font-size: 16px;
  font-weight: 700;
  color: var(--white);
  text-decoration: none;
  letter-spacing: 0.15em;
  padding-left: 14px;
  text-transform: uppercase;
}

/* ナビリンク群 */
.nav-links {
  display: flex;
  align-items: stretch;
  gap: 0;
  z-index: 10;
}

.nav-link { text-decoration: none; }

.nav-btn {
  display: flex;
  align-items: center;
  height: 100%;
  padding: 0 16px;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.08em;
  color: #555;
  background: transparent;
  border: none;
  border-left: 1px solid #1a1a1a;
  cursor: pointer;
  transition: color 0.15s;
  position: relative;
}

.nav-btn::after {
  content: '';
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 2px;
  background: var(--red);
  transform: scaleX(0);
  transition: transform 0.2s;
}

.nav-btn:hover,
.nav-active .nav-btn { color: var(--white); }
.nav-btn:hover::after,
.nav-active .nav-btn::after { transform: scaleX(1); }

/* ユーザープロフィール */
.user-profile {
  display: flex;
  align-items: center;
  padding: 0 16px;
  border-left: 1px solid #1a1a1a;
  gap: 8px;
}

.user-avatar {
  width: 28px;
  height: 28px;
  background: var(--red);
  clip-path: polygon(0 0, 100% 0, 100% 70%, 85% 100%, 0 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  color: #fff;
  border: none;
  border-radius: 0;
}

.user-name {
  font-size: 12px;
  color: #888;
  letter-spacing: 0.06em;
}

/* ログアウトボタン */
.logout-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 0 16px;
  background: transparent;
  border: none;
  border-left: 1px solid #1a1a1a;
  color: #555;
  font-size: 12px;
  letter-spacing: 0.1em;
  cursor: pointer;
  transition: all 0.15s;
  clip-path: polygon(0 0, 100% 0, 94% 100%, 0 100%);
  height: 100%;
}

.logout-btn:hover { color: var(--red); border-left-color: var(--red); }
.logout-icon { font-size: 14px; }

/* 認証ボタン（未ログイン） */
.auth-btn {
  display: flex;
  align-items: center;
  padding: 0 18px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-decoration: none;
  border-left: 1px solid #1a1a1a;
  transition: all 0.15s;
  height: 100%;
}

.auth-btn.login { color: #555; }
.auth-btn.login:hover { color: var(--white); }
.auth-btn.register {
  background: var(--red);
  color: #fff;
  clip-path: polygon(0 0, 100% 0, 94% 100%, 0 100%);
  padding-right: 24px;
}
.auth-btn.register:hover { background: #ff1a35; }

/* ドロップダウン */
.dropdown {
  position: relative;
  display: flex;
  align-items: stretch;
}

.dropdown-trigger {
  display: flex;
  align-items: center;
  height: 100%;
  padding: 0 16px;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.08em;
  color: #555;
  background: transparent;
  border: none;
  border-left: 1px solid #1a1a1a;
  cursor: pointer;
  transition: color 0.15s;
  position: relative;
}

.dropdown-trigger::after {
  content: '';
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 2px;
  background: var(--red);
  transform: scaleX(0);
  transition: transform 0.2s;
}

.dropdown:hover .dropdown-trigger,
.dropdown-trigger:focus { color: var(--white); }
.dropdown:hover .dropdown-trigger::after { transform: scaleX(1); }

.dropdown-arrow {
  margin-left: 4px;
  font-size: 10px;
  transition: transform 0.2s;
}
.dropdown:hover .dropdown-arrow { transform: rotate(180deg); }

.dropdown-menu {
  position: absolute;
  top: calc(100% + 2px);
  left: 0;
  min-width: 180px;
  background: #0e0e12;
  border: 1px solid #1a1a1a;
  border-top: 2px solid var(--red);
  opacity: 0;
  visibility: hidden;
  transform: translateY(-8px);
  transition: all 0.2s;
  z-index: 9999;
}

.dropdown-menu.show {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

.dropdown-item {
  display: block;
  padding: 12px 16px;
  color: #555;
  text-decoration: none;
  font-size: 12px;
  letter-spacing: 0.08em;
  border-bottom: 1px solid #1a1a1a;
  transition: all 0.15s;
  position: relative;
}

.dropdown-item::before {
  content: '';
  position: absolute;
  left: 0; top: 0; bottom: 0;
  width: 2px;
  background: var(--red);
  transform: scaleY(0);
  transition: transform 0.15s;
}

.dropdown-item:last-child { border-bottom: none; }
.dropdown-item:hover { color: var(--white); padding-left: 20px; }
.dropdown-item:hover::before { transform: scaleY(1); }

/* レスポンシブ */
@media (max-width: 768px) {
  .navbar {
    flex-direction: column;
    height: auto;
    padding: 12px 0;
  }
  .logo { padding: 0 16px 10px; }
  .nav-links { flex-wrap: wrap; padding: 0 8px; }
  .nav-btn, .auth-btn, .logout-btn, .dropdown-trigger {
    height: 40px;
    font-size: 12px;
    padding: 0 12px;
  }
  .dropdown-menu {
    position: static;
    opacity: 1;
    visibility: visible;
    transform: none;
    border: none;
    background: transparent;
  }
}
</style>
