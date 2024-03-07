<template>
  <section>
    <div>
      <p><strong>Username:</strong> <span>{{ user.username }}</span></p>
      <OAuth></OAuth>
      <!-- <p><button @click="deleteAccount()" class="btn btn-primary">Delete Account</button></p> -->

    </div>
  </section>
</template>

<script>
import { defineComponent } from 'vue';
import useUsersStore from '@/store/users'; 
import { useToast } from 'vue-toastification';
import axios from 'axios';
import OAuth from '@/components/OAuth.vue';
export default defineComponent({
  name: 'ProfileComponent',
  components: {
    OAuth
  },
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
    async testAuth() {
      // Call your yahoo_auth function with this.yahooToken
      document.cookie = 'oauth_started=true; path=/';
   
      const backendURL = (import.meta.env.VITE_APP_BACKEND_URL || 'http://localhost:5000') + '/oauth/yahoo/callback/test';
      console.log("redirect uri", backendURL);
      const response = await axios.get(backendURL);
      console.log("response", response);
     
    }   

  },
});
</script>

