<template>
  <div class="surface-section">
    <div class="font-medium text-3xl text-900 mb-3">Integrations</div>
    <div v-if="oauthTokens ">
      <div class="text-500 mb-5">Provider: {{ oauthTokens.provider }}</div>
      <ul class="list-none p-0 m-0">
        <li class="flex align-items-center py-3 px-2 border-top-1 surface-border flex-wrap">
          <div class="text-500 w-6 md:w-2 font-medium">Created</div>
          <div class="text-900 w-full md:w-8 md:flex-order-0 flex-order-1">{{ formatDate(oauthTokens.created_at) }}</div>

        </li>

        <li v-if="oauthTokens.modified_at" class="flex align-items-center py-3 px-2 border-top-1 surface-border flex-wrap">
          <div class="text-500 w-6 md:w-2 font-medium">Modified</div>
          <div class="text-900  md:w-8 md:flex-order-0 flex-order-1">{{ formatDate(oauthTokens.modified_at) }}</div>
        </li>
      </ul>
      <ConfirmDialog></ConfirmDialog>
      <Button label="Delete Integration" severity="danger" @click="confirmDelete(oauthTokens.id)" />
    </div>
    <div v-else>
      <p><button @click="connectToYahoo()" class="btn btn-primary">Connect to Yahoo</button></p>
      <p> After integrating your yahoo account, you might need to refresh the page.</p>

    </div>


  </div>
</template>

<script>
import { defineComponent, ref, computed, onMounted } from 'vue';
import useUsersStore from '@/store/users'; 
import axios from 'axios';
import { useToast } from 'vue-toastification';

export default defineComponent({
  name: 'OAuth',
  

  setup() {
    const usersStore = useUsersStore();
    const oauthTokens = ref(null);
    const toast = useToast();

    onMounted( () => {
      fetchData();
    });

    const user = computed(() => usersStore.stateUser);


    const fetchData = async () => {
      try {
        const response = await axios.get(`/oauth/yahoo/tokens`, {
          params: {
            user_id: user.value.id
          }
        });
        oauthTokens.value = response.data;
      } catch (error) {
        console.error('Failed to fetch Yahoo integration:', error);
      }
    };

    async function removeIntegration(tokenId) {
      try {
        await axios.delete(`/oauth/yahoo/tokens/${tokenId}`);
        toast.success('Integration removed successfully');
        // Reset oauthTokens to null or empty object if necessary
        this.oauthTokens = null;
      } catch (error) {
        console.error('Failed to remove integration:', error);
        toast.error('Failed to remove integration');
      }
    }
    function confirmDelete(tokenId) {
      this.$confirm.require({
        message: "Are you sure you want to remove this integration?",
        header: "Delete Confirmation",
        icon: "pi pi-exclamation-triangle",
        accept: () => this.removeIntegration(tokenId),
        reject: () => {
          console.log("Integration deletion cancelled.");
          this.toast.warn('Whew. That was a close one');
        }
      });
    }
    function connectToYahoo() {
        document.cookie = 'oauth_started=true; path=/';
        const toast = useToast();
        console.log('This window origin:', window.location.origin); // Log the origin of this window

        const oauthListener = (event) => {
          console.log('event', event);
          if (event.data === 'oauth_success') {
            fetchData();
            toast.success('Yahoo integration successful');
            window.removeEventListener('message', oauthListener); // Remove event listener
          }
          if (event.data === 'oauth_error') {
            fetchData();
            toast.error('Yahoo integration failed, please try again.');
            window.removeEventListener('message', oauthListener); // Remove event listener
          }
        };

      window.addEventListener('message', oauthListener);
      
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

    }
    function formatDate(dateString) {
      const options = { year: 'numeric', month: 'long', day: 'numeric' };
      return new Date(dateString).toLocaleDateString(undefined, options);
    }
    return {
      user, oauthTokens, connectToYahoo, removeIntegration, confirmDelete, formatDate
    }
  }
});
</script>
