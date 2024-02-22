<template>
  <LoadingSpinner v-if="isLoading" />

  <div v-else-if="bot && (isAdmin || userOwnsBot)">
    <div class="surface-section">
      <div class="font-medium text-3xl text-900 mb-3">{{ bot.name }}</div>
      <div class="text-500 mb-5">Created: {{ bot.created_at }}</div>
      <ul class="list-none p-0 m-0">
        <li class="flex align-items-center py-3 px-2 border-top-1 surface-border flex-wrap">
          <div class="text-500 w-6 md:w-2 font-medium">Name</div>
          <div class="text-900 w-full md:w-8 md:flex-order-0 flex-order-1">{{ bot.name }}</div>
        </li>

        <li v-if="bot.app" class="flex align-items-center py-3 px-2 border-top-1 surface-border flex-wrap">
          <div class="text-500 w-6 md:w-2 font-medium">Status</div>
          <div class="text-900 w-full md:w-8 md:flex-order-0 flex-order-1">
            <Button v-if="bot.app.running" label="Running" severity="success" />
            <Button v-else :label="bot.app.status" severity="info" />
          </div>
        </li>

        <li v-if="bot.app" class="flex align-items-center py-3 px-2 border-top-1 surface-border flex-wrap">
          <div class="text-500 w-6 md:w-2 font-medium">Commands</div>
          <div class="text-900 w-full md:w-8 md:flex-order-0 flex-order-1">
            <Button v-if="bot.app.running" label="Stop Bot" severity="info" />
            <Button v-else label="Start Bot" severity="info" />
          </div>
        </li>

        <li v-else class="flex align-items-center py-3 px-2 border-top-1 surface-border flex-wrap">
          <div class="text-500 w-6 md:w-2 font-medium">Commands</div>
          <div class="text-900 w-full md:w-8 md:flex-order-0 flex-order-1">
            <ConfirmDialog></ConfirmDialog>

            <Button label="Initiate Bot" @click="initiateBot" severity="info" />
          </div>
        </li>

        <li class="flex align-items-center py-3 px-2 border-top-1 surface-border flex-wrap">
          <div class="text-500 w-6 md:w-2 font-medium">League ID</div>
          <div class="text-900 w-full md:w-8 md:flex-order-0 flex-order-1">{{bot.league_id}}</div>
        </li>

        <li class="flex align-items-center py-3 px-2 border-top-1 border-bottom-1 surface-border flex-wrap">
          <div class="text-500 w-6 md:w-2 font-medium">GroupMe Bot ID</div>
          <div class="text-900 w-full md:w-8 md:flex-order-0 flex-order-1">{{bot.groupme_bot_id}}</div>
        </li>

        <li v-if="isAdmin" class="flex align-items-center py-3 px-2 border-top-1 surface-border flex-wrap">
          <div class="text-500 w-6 md:w-2 font-medium">Admin Actions</div>
          <div class="text-900 w-full md:w-8 md:flex-order-0 flex-order-1">
            <SplitButton label="Visit" icon="pi pi-cog" :model="adminItems" raised rounded @click="visit" severity="secondary"></SplitButton>
          </div>
        </li>
      </ul>
    </div>

    <p>
      <ConfirmDialog></ConfirmDialog>
      <Button label="Delete" severity="danger" @click="confirmDelete" />
    </p>
  </div>
</template>
<script>
import { defineComponent, onMounted, computed, ref } from 'vue';
import useBotsStore from '@/store/bots'; 
import useUsersStore from '@/store/users'; 
import axios from 'axios';
import LoadingSpinner from '@/components/LoadingSpinner.vue';
import { useRouter } from 'vue-router';
import { useToast } from 'vue-toastification';
import { useConfirm } from "primevue/useconfirm";

export default defineComponent({
    name: 'BotComponent',
    props: ['id'],
    components: { LoadingSpinner },
    confirmDelete() {
          this.$confirm.require({
            message: "Are you sure you want to delete this bot?",
            header: "Delete Confirmation",
            icon: "pi pi-exclamation-triangle",
            accept: () => this.removeBot(),
            reject: () => {
              console.log("Bot deletion cancelled.");
              this.toast.warn('Whew. That was a close one');
            
            }
          });
        },
    setup(props) {
        const botsStore = useBotsStore();
        const usersStore = useUsersStore();
        const isLoading = ref(true);
        const router = useRouter();
        const toast = useToast();
        const confirm = useConfirm();

        const confirmDelete = () => {
          confirm.require({
            message: "Are you sure you want to delete this bot?",
            header: "Delete Confirmation",
            icon: "pi pi-exclamation-triangle",
            accept: () => {removeBot()},
            reject: () => {
              console.log("Bot deletion cancelled.");
              this.toast.warn('Whew. That was a close one');
            
            }
          });
        };
        const adminItems = ref([
            {
                label: 'Refresh',
                icon: 'pi pi-refresh'
            },
            {
                label: 'Visit',
                icon: 'pi pi-bookmark'
            },
            {
                separator: true
            },
            {
                label: 'Kill',
                icon: 'pi pi-times'
            }
        ]);
        async function fetchData() {
            try {
                await botsStore.viewBot(props.id);
                await usersStore.viewMe();
            } catch (error) {
                console.error('Error fetching data:', error);
                if (error.response && error.response.status === 404) {
                    router.push('/dashboard');
                }
            } finally {
                isLoading.value = false;
            }
        }

        onMounted(fetchData);

        const bot = computed(() => botsStore.stateBot);
        const user = computed(() => usersStore.stateUser);
        const isAdmin = computed(() => usersStore.isAdmin);
        const userOwnsBot = computed(() => user.value.id === bot.user.id);

        async function initiateBot() {
            try {
                isLoading.value = true;
                await axios.post(`/apps/start-app/${props.id}`);
                await fetchData();
            } catch (error) {
                console.error('Error initiating bot:', error);
                toast.error('Error initiating bot: ' + error.message);            
            } finally {
                isLoading.value = false;
                toast.success('Bot initiated successfully');

            }
        }

        async function removeBot() {
            try {
                if (bot.value) {
                    isLoading.value = true;
                    await botsStore.deleteBot(props.id);
                    router.push('/dashboard');
                    toast.success('Bot killed and deleted successfully');
                }
            } catch (error) {
                console.error('Error removing bot:', error);
                if (error.response && error.response.status === 404) {
                    toast.error('The requested bot was not found.');
                    router.push('/dashboard');
                } else {
                  if (error.response) {
                    toast.error('Error removing bot: ' + error.message);
                  }
                }
            } finally {
                isLoading.value = false;
            }
        }

        const visit = () => {
            window.open(`http://167.99.4.120:8000/#/apps/${bot.value.app.name}`, '_blank');
        };

        return { bot, user, isAdmin, isLoading, userOwnsBot, removeBot, adminItems, visit, initiateBot, confirmDelete, confirm };
    }
});
</script>
