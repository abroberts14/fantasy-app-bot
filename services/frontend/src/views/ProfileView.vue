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
    connectToYahoo() {
      document.cookie = 'oauth_started=true; path=/';
      const toast = useToast();
      console.log('This window origin:', window.location.origin); // Log the origin of this window

    // Open a blank new window with specified features
     // let authWindow = window.open('', '_blank', windowFeatures);


      const oauthListener = (event) => {
        console.log('event', event);
        if (event.data === 'oauth_success') {
          toast.success('Yahoo integration successful');
          window.removeEventListener('message', oauthListener); // Remove event listener
        }
        if (event.data === 'oauth_error') {
          toast.error('Yahoo integration failed, please try again.');
          window.removeEventListener('message', oauthListener); // Remove event listener
        }
      };

      // Add an event listener for the 'message' event
      window.addEventListener('message', oauthListener, false);
      const YAHOO_API_URL = "https://api.login.yahoo.com/oauth2/";
  
      const consumer_key =  import.meta.env.VITE_APP_YAHOO_CLIENT_ID;
      const backendURL = (import.meta.env.VITE_APP_BACKEND_URL || 'http://localhost:5000') + '/oauth/yahoo/callback';
      console.log("redirect uri", backendURL);
      const converted_url = encodeURIComponent(backendURL);
      const YAHOO_AUTH_URI = `request_auth?redirect_uri=${converted_url}&response_type=code&client_id=`;
      const link = `${YAHOO_API_URL}${YAHOO_AUTH_URI}${consumer_key}`;

      const windowFeatures = "width=800,height=600,resizable,scrollbars=yes,status=1";

      let authWindow = window.open(link, '_blank', windowFeatures);

      if (authWindow) {
        authWindow.location.href = link
        authWindow.onload = () => {
          console.log('New window origin:', authWindow.location.origin);
        };
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

