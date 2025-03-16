// src/store/index.js
import { createStore } from 'vuex';
import auth from './modules/auth';
import quiz from './modules/quiz';

// Vue.use(Vuex) は Vue 3では不要

export default createStore({
  modules: {
    auth,
    quiz
  }
});