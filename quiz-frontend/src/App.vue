<!-- App.vue -->
<template>
  <div id="app">
    <SiteNavigation />
    <main>
      <router-view/>
    </main>
    <footer>
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

footer {
  margin-top: 50px;
  text-align: center;
  font-size: 0.8em;
  color: #666;
  padding: 20px 0;
}
</style>