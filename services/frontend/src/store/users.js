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
    isAdmin: state => state.user && state.user.role === 'admin',
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
      await axios.post('logout');

      this.logout(null);
    },
    setUser(username) {
      this.user = username;
    },
    logout(user){
      this.user = user;

      //this.$reset();

    },
  },
  persist: {
    storage: sessionStorage,
  },
});

export default useUsersStore;