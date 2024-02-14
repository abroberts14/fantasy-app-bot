import axios from 'axios';
import { defineStore } from 'pinia';

const useUsersStore = defineStore('users', {
  id: 'users',
  state: () => ({
    user: null,
  }),
  getters: {
    isAuthenticated: state => !!state.user,
    stateUser: state => state.user,
  },
  actions: {
    async register(form) {
      await axios.post('register', form);
      let UserForm = new FormData();
      UserForm.append('username', form.username);
      UserForm.append('password', form.password);
      await this.logIn(UserForm);
    },
    async logIn(user) {
      await axios.post('login', user);
      await this.viewMe();
    },
    async viewMe() {
      let {data} = await axios.get('users/whoami');
      this.setUser(data);
    },
    async deleteUser(id) {
      await axios.delete(`user/${id}`);
    },
    async logOut() {
      this.logout(null);
    },
    setUser(username) {
      this.user = username;
    },
    logout(user){
      this.user = user;
    },
  },
  persist: {
    storage: sessionStorage,
  },
});

export default useUsersStore;