import { createStore } from "vuex";

import notes from './modules/notes';
import users from './modules/users';
import bots from './modules/bots';

export default createStore({
  modules: {
    notes,
    users,
    bots,
  }
});
