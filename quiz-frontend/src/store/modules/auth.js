// src/store/modules/auth.js
import axios from 'axios';

const state = {
  token: localStorage.getItem('token') || '',
  user: JSON.parse(localStorage.getItem('user') || 'null'),
  status: ''
};

const getters = {
  isAuthenticated: state => !!state.token,
  authStatus: state => state.status,
  user: state => state.user
};

const actions = {
  // ログイン
  async login({ commit }, user) {
    commit('auth_request');
    try {
      const response = await axios.post('http://localhost:8000/api/token/', {
        username: user.username,
        password: user.password
      });
      const token = response.data.access;
      const refreshToken = response.data.refresh;
      
      localStorage.setItem('token', token);
      localStorage.setItem('refresh_token', refreshToken);
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      
      // ユーザープロフィール取得
      const userResponse = await axios.get('http://localhost:8000/api/profile/');
      const userData = userResponse.data;
      localStorage.setItem('user', JSON.stringify(userData));
      
      commit('auth_success', { token, user: userData });
      return response;
    } catch (err) {
      commit('auth_error');
      localStorage.removeItem('token');
      localStorage.removeItem('refresh_token');
      throw err;
    }
  },
  
  // 登録
  async register({ commit }, userData) {
    commit('auth_request');
    try {
      await axios.post('http://localhost:8000/api/register/', userData);
      commit('register_success');
      return true;
    } catch (err) {
      commit('auth_error', err);
      throw err;
    }
  },
  
  // ログアウト
  logout({ commit }) {
    return new Promise((resolve) => {
      commit('logout');
      localStorage.removeItem('token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      delete axios.defaults.headers.common['Authorization'];
      resolve();
    });
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
  }
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};