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

export default defineComponent({
  name: 'DashboardComponent',
  components: {
    BotTable,
  },
  setup() {
    const loaded = ref(false);
    const botsStore = useBotsStore();
    const usersStore = useUsersStore(); 

    const bots = computed(() => botsStore.stateBots);
    const user = computed(() => usersStore.stateUser);

    const fetchData = async () => {
      loaded.value = false;
      await usersStore.viewMe();
      await botsStore.getBots(user.value.id);
      loaded.value = true;
    };

    onMounted(() => {
      fetchData();
    });

    return { bots, user, loaded };
  },
});
</script>