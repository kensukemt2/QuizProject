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
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  margin-top: 20px;
}

.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: #F97316;
  color: white;
  padding: 8px 16px;
  z-index: 10000;
  text-decoration: none;
  font-weight: bold;
  transition: top 0.2s;
}

.skip-link:focus {
  top: 0;
}

footer {
  margin-top: 50px;
  text-align: center;
  font-size: 0.8em;
  color: #666;
  padding: 20px 0;
}
</style>