// src/store/modules/auth.js
import axios from 'axios';

const state = () => ({
  token: localStorage.getItem('token') || null,
  user: null
});

const actions = {
  // ログイン
  async login({ commit, dispatch }, credentials) {
    try {
      // APIへのリクエスト例
      const response = await fetch('http://localhost:8000/api/token/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials)
      });
      
      if (!response.ok) {
        throw new Error('ログインに失敗しました');
      }
      
      const data = await response.json();
      const token = data.access;
      
      // トークンをローカルストレージとステートに保存
      localStorage.setItem('token', token);
      commit('SET_TOKEN', token);
      
      // ユーザー情報を取得（オプション）
      await dispatch('fetchUserProfile');
      
      return true;
    } catch (error) {
      console.error('ログインエラー:', error);
      return false;
    }
  },
  
  // 登録
  async register(_, userData) {
    try {
      // APIへのリクエスト
      const response = await fetch('http://localhost:8000/api/register/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData)
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw { response: { data: errorData } };
      }
      
      return true;
    } catch (error) {
      console.error('登録エラー:', error);
      throw error;
    }
  },
  
  // ログアウト
  async logout({ commit }) {
    commit('CLEAR_AUTH');
    localStorage.removeItem('token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    delete axios.defaults.headers.common['Authorization'];
  },
  
  // トークンリフレッシュ
  async refreshToken({ commit, state }) {
    if (!state.token) return;
    
    const refreshToken = localStorage.getItem('refresh_token');
    try {
      const response = await axios.post('http://localhost:8000/api/token/refresh/', {
        refresh: refreshToken
      });
      const newToken = response.data.access;
      localStorage.setItem('token', newToken);
      axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
      commit('refresh_token', newToken);
    } catch (err) {
      console.error('トークンリフレッシュエラー:', err);
      commit('logout');
      localStorage.removeItem('token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      delete axios.defaults.headers.common['Authorization'];
    }
  }
};

const mutations = {
  auth_request(state) {
    state.status = 'loading';
  },
  auth_success(state, { token, user }) {
    state.status = 'success';
    state.token = token;
    state.user = user;
  },
  register_success(state) {
    state.status = 'registered';
  },
  auth_error(state) {
    state.status = 'error';
  },
  logout(state) {
    state.status = '';
    state.token = '';
    state.user = null;
  },
  refresh_token(state, token) {
    state.token = token;
  },
  SET_TOKEN(state, token) {
    state.token = token;
  },
  SET_USER(state, user) {
    state.user = user;
  },
  CLEAR_AUTH(state) {
    state.token = null;
    state.user = null;
  }
};

export default {
  namespaced: true,
  state,
  getters: {
    isAuthenticated: state => !!state.token,
    currentUser: state => state.user
  },
  actions,
  mutations
};