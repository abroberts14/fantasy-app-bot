<template>
  <section>
    <div>
      <p><strong>Username:</strong> <span>{{ user.username }}</span></p>
      <p><button @click="deleteAccount()" class="btn btn-primary">Delete Account</button></p>
      <p><button @click="connectToYahoo()" class="btn btn-primary">Connect to Yahoo</button></p>
      <p><button @click="testAuth()" class="btn btn-primary">Test OAuth Callback</button></p>

    </div>
  </section>
</template>

<script>
import { defineComponent } from 'vue';
import useUsersStore from '@/store/users'; 
import { useToast } from 'vue-toastification';
import axios from 'axios';

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
      document.cookie = 'oauth_started=true; path=/';
      const toast = useToast();
      console.log('This window origin:', window.location.origin); // Log the origin of this window

    // Open a blank new window with specified features
     // let authWindow = window.open('', '_blank', windowFeatures);

     const channel = new BroadcastChannel('oauth_channel');

      const oauthListener = (event) => {
        console.log('event', event);
        if (event.data === 'oauth_success') {
          authWindow.close(); // Close the OAuth window
          toast.success('Yahoo integration successful');
          channel.removeEventListener('message', oauthListener); // Remove event listener
          window.removeEventListener('message', oauthListener); // Remove event listener
        }
        if (event.data === 'oauth_error') {
          authWindow.close(); // Close the OAuth window
          toast.error('Yahoo integration failed, please try again.');
          channel.removeEventListener('message', oauthListener); // Remove event listener
          window.removeEventListener('message', oauthListener); // Remove event listener
        }
      };

      // Add an event listener for the 'message' event
      channel.addEventListener('message', oauthListener, false);
      window.addEventListener('message', oauthListener, false);
      const YAHOO_API_URL = "https://api.login.yahoo.com/oauth2/";
  
      const consumer_key =  import.meta.env.VITE_APP_YAHOO_CLIENT_ID;
      console.log("client id", consumer_key);
      // Access the environment variable directly
      const backendURL = (import.meta.env.VITE_APP_BACKEND_URL || 'http://localhost:5000') + '/oauth/yahoo/callback';
      console.log("redirect uri", backendURL);
      const converted_url = encodeURIComponent(backendURL);
      console.log("converted url", converted_url);
     // const YAHOO_AUTH_URI = `request_auth?redirect_uri=${encodeURIComponent(backendURL)}&response_type=code&client_id=`;
      const YAHOO_AUTH_URI = `request_auth?redirect_uri=${converted_url}&response_type=code&client_id=`;

      const link = `${YAHOO_API_URL}${YAHOO_AUTH_URI}${consumer_key}`;
      console.log("link", link);
     // window.location.href = link;
      // Open the OAuth link in a new window
      //const oauthWindow = window.open(link, 'yahooOauthWindow', 'width=800,height=600');
      // Check if the window is successfully opened
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

