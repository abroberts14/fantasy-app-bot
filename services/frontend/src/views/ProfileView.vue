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
      const windowFeatures = "width=800,height=600,resizable,scrollbars=yes,status=1";

    // Open a blank new window with specified features
      let authWindow = window.open('', '_blank', windowFeatures);
      const pollTimer = window.setInterval(() => {
      try {
        if (authWindow.location.href.includes("oauth-success")) {
          window.clearInterval(pollTimer);
          authWindow.close(); // Close the OAuth window

          // Additional logic after successful OAuth completion
          // e.g., update the user's state, fetch new data, etc.
        }
      } catch (e) {
        // Error handling, e.g., cross-origin issues
      }
    }, 100); // Poll every 100 milliseconds
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
      if (authWindow) {
        // Set the URL of the new window
        authWindow.location.href = link;
      } else {
        alert("Pop-up blocked! Please allow pop-ups and try again.");
      }
    },
    yahooAuth() {
      // Call your yahoo_auth function with this.yahooToken
      console.log('test')
    },
  },
});
</script>

