<template>
  <div>
    <h1>My Bots</h1>
    <hr/><br/>
    <BotTable  :bots="bots" />
  </div>
</template>

<script>
import { defineComponent } from 'vue';
import useBotsStore from '@/store/bots'; 
import useUsersStore from '@/store/users'; 
import BotTable from '@/components/BotTable.vue'; 

export default defineComponent({
  name: 'DashboardComponent',
  components: {
    BotTable,
  },
  data() {
    return {
      form: {
        title: '',
        content: '',
      },
    };
  },
  async created() {
    const usersStore = useUsersStore(); 
    await usersStore.viewMe();
    const userId = usersStore.stateUser.id;
    const botsStore = useBotsStore();
    await botsStore.getBots(userId); // send user id to get current users bots
  },
  computed: {
    bots() {
      const botsStore = useBotsStore();
      return botsStore.stateBots;
    },
    user() {
      const usersStore = useUsersStore(); 
      return usersStore.stateUser; 
    },
  },
});
</script>