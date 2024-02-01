import { createStore } from "vuex";
import users from './modules/users';
import bots from './modules/bots';

export default createStore({
  modules: {
    users,
    bots,
  }
});
