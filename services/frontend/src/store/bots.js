import axios from 'axios';
import { defineStore } from 'pinia';

const useBotsStore = defineStore({
  id: 'bots',
  state: () => ({
    bots: [],
    //bots: null,
    bot: null,
  }),
  getters: {
    stateBots: state => state.bots,
    stateBot: state => state.bot,
  },
  actions: {
    async createBot(bot) {
      await axios.post('register-bot', bot);
      await this.getBots();
    },
    async getBots(userId = null) {
      let url = 'bots';
      if (userId) {
        url += `?user_id=${userId}`;
      }
      let {data} = await axios.get(url);
      this.setBots(data);
    },
    async viewBot(id) {
      let {data} = await axios.get(`bot/${id}`);
      this.setBot(data);
    },
    async updateBot(bot) {
      await axios.patch(`bot/${bot.id}`, bot.form);
    },
    async deleteBot(id) {
      await axios.delete(`bot/${id}`);
    },
    setBots(bots){
      this.bots = bots;
    },
    setBot(bot){
      this.bot = bot;
    },
  },
});

export default useBotsStore;