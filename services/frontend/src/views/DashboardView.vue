<template>
  <div>
    <h1>My Bots</h1>
    <hr/><br/>
    <BotTable :bots="bots" :loaded="loaded" />
  </div>
</template>

<script>
import { defineComponent, ref, computed, onMounted } from 'vue';
import useBotsStore from '@/store/bots'; 
import useUsersStore from '@/store/users'; 
import BotTable from '@/components/BotTable.vue'; 
import { useRouter } from 'vue-router';

export default defineComponent({
  name: 'DashboardComponent',
  components: {
    BotTable,
  },
  setup() {
    const loaded = ref(false);
    const botsStore = useBotsStore();
    const usersStore = useUsersStore(); 
    const router = useRouter();

    const bots = computed(() => botsStore.stateBots);
    const user = computed(() => usersStore.stateUser);


    onMounted(async () => {

      if (usersStore.hasOAuthToken) {
        router.push('/my-team');
      } else {
        await fetchUserData();
      }
    });
    const fetchUserData = async () => {
      loaded.value = false;
      await usersStore.viewMe();
      await botsStore.getBots(user.value.id);
      loaded.value = true;
    };
    return { bots, user, loaded };
  },
});
</script>