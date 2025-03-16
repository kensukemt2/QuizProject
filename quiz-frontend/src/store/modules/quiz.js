// store/modules/quiz.js
const state = {
  isGuestMode: false
};

const mutations = {
  SET_GUEST_MODE(state, isGuest) {
    state.isGuestMode = isGuest;
  }
};

const getters = {
  isGuestMode: state => state.isGuestMode
};

export default {
  namespaced: true,
  state,
  mutations,
  getters
};