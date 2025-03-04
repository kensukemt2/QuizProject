// src/store/index.js
import { createStore } from 'vuex'
import auth from './modules/auth'

// storeをエクスポートする前に明示的に作成する
const store = createStore({
  modules: {
    auth
  }
})

export default store