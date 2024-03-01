<template>
  <div class="surface-section">
    <div class="font-medium text-3xl text-900 mb-3">Integrations</div>
    <div v-if="oauthTokens">
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
    </div>
    <div v-else>
      <p><button @click="connectToYahoo()" class="btn btn-primary">Connect to Yahoo</button></p>
    </div>
    <ConfirmDialog></ConfirmDialog>
    <Button label="Delete Integration" severity="danger" @click="confirmDelete(oauthTokens.id)" />
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

    onMounted(async () => {
      try {
        const response = await axios.get('/oauth/yahoo/tokens');
        oauthTokens.value = response.data;
      } catch (error) {
        console.error('Failed to fetch OAuth tokens:', error);
      }
    });

    const user = computed(() => usersStore.stateUser);
    async function connectToYahoo() {
      // Existing connectToYahoo logic
    }
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
