import axios from 'axios';

const state = {
  bots: null,
  bot: null
};

const getters = {
  stateBots: state => state.bots,
  stateBot: state => state.bot,
};

const actions = {
  async createBot({dispatch}, bot) {
    await axios.post('register-bot', bot);
    await dispatch('getBots');
  },

  async getBots({commit}) {
    let {data} = await axios.get('bots');
    commit('setBots', data);
  },
  async viewBot({commit}, id) {
    let {data} = await axios.get(`bot/${id}`);
    commit('setBot', data);
  },
  // eslint-disable-next-line no-empty-pattern
  async updateBot({}, bot) {
    await axios.patch(`bot/${bot.id}`, bot.form);
  },
  // eslint-disable-next-line no-empty-pattern
  async deleteBot({}, id) {
    await axios.delete(`bot/${id}`);
  }
};

const mutations = {
  setBots(state, bots){
    state.bots = bots;
  },
  setBot(state, bot){
    state.bot = bot;
  },
};

export default {
  state,
  getters,
  actions,
  mutations
};
