<template>
  <section>
    <div>
      <p><strong>Username:</strong> <span>{{ user.username }}</span></p>
      <p><button @click="deleteAccount()" class="btn btn-primary">Delete Account</button></p>
      <p><button @click="connectToYahoo()" class="btn btn-primary">Connect to Yahoo</button></p>
      <p><input v-model="yahooToken" placeholder="Enter Yahoo OAuth token"> </input></p>
    </div>
  </section>
</template>

<script>
import { defineComponent } from 'vue';
import useUsersStore from '@/store/users'; 

export default defineComponent({
  name: 'ProfileComponent',
  data() {
    return {
      yahooToken: '',
    };
  },
  async created() {
    const usersStore = useUsersStore(); 
    await usersStore.viewMe(); // Call the action from your users store
  },
  computed: {
    user() {
      const usersStore = useUsersStore(); 
      return usersStore.stateUser; 
    },
  },
  methods: {
    async deleteAccount() {
      try {
        const usersStore = useUsersStore(); 
        await usersStore.deleteUser(this.user.id); // Call the action from your users store
        await usersStore.logOut(); // Call the action from your users store
        this.$router.push('/');
      } catch (error) {
        console.error(error);
      }
    },
    connectToYahoo() {
      const YAHOO_API_URL = "https://api.login.yahoo.com/oauth2/";
      const consumer_key =  import.meta.env.YAHOO_CLIENT_ID;

      // Access the environment variable directly
      const backendURL = import.meta.env.VITE_APP_BACKEND_URL || 'http://localhost:5000';

      const YAHOO_AUTH_URI = `request_auth?redirect_uri=${encodeURIComponent(backendURL)}&response_type=code&client_id=`;
      const link = `${YAHOO_API_URL}${YAHOO_AUTH_URI}${consumer_key}`;
      console.log(link);

      //window.location.href = link;
      console.log(link);
    },
    yahooAuth() {
      // Call your yahoo_auth function with this.yahooToken
      console.log('test')
    },
  },
});
</script>