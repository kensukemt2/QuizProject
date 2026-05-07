<!-- App.vue -->
<template>
  <div id="app">
    <a href="#main-content" class="skip-link">メインコンテンツへスキップ</a>
    <SiteNavigation />
    <main id="main-content" role="main">
      <router-view/>
    </main>
    <footer role="contentinfo">
      <p>&copy; 2025 クイズアプリ</p>
    </footer>
  </div>
</template>

<script>
import SiteNavigation from './components/Navbar.vue'

export default {
  name: 'App',
  components: {
    SiteNavigation
  }
}
</script>

<style>
/* ── グローバルリセット ── */
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

/* ── Reggae One フォント読み込み ── */
@import url('https://fonts.googleapis.com/css2?family=Reggae+One&display=swap');

/* ── 全体ベース ── */
html, body {
  background: #060608;
  color: #f5f0e8;
  min-height: 100vh;
  font-family: 'Reggae One', 'Hiragino Kaku Gothic ProN', 'Noto Sans JP', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* すべての要素にReggae Oneを強制 */
* {
  font-family: 'Reggae One', 'Hiragino Kaku Gothic ProN', 'Noto Sans JP', sans-serif !important;
}

/* 問題文・選択肢・textarea・inputは読みやすいフォントに */
.question-text h2,
.choice-text,
textarea,
input[type="text"],
input[type="email"],
input[type="password"] {
  font-family: 'Hiragino Kaku Gothic ProN', 'Noto Sans JP', 'Meiryo', sans-serif !important;
}

#app {
  background: #060608;
  color: #f5f0e8;
  min-height: 100vh;
  margin-top: 0;
}

/* ── フッター ── */
footer {
  margin-top: 40px;
  text-align: center;
  font-size: 11px;
  color: #333;
  letter-spacing: 0.1em;
  padding: 20px 0;
  border-top: 1px solid #1a1a1a;
}

/* ── スキップリンク ── */
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: #e8001c;
  color: #fff;
  padding: 8px 16px;
  z-index: 10000;
  text-decoration: none;
  font-weight: bold;
  transition: top 0.2s;
  clip-path: polygon(0 0, 100% 0, 94% 100%, 0 100%);
}
.skip-link:focus { top: 0; }

/* ── スクロールバー（Webkit）── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0e0e12; }
::-webkit-scrollbar-thumb { background: #e8001c; }
::-webkit-scrollbar-thumb:hover { background: #ff1a35; }
</style>
