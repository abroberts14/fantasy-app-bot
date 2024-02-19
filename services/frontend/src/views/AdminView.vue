<template>
  <div>
    <h1>All Bots</h1>
    <hr/><br/>
    <BotTable :bots="bots" />
  </div>
</template>

<script>
import { defineComponent, onMounted, computed } from 'vue';
import useBotsStore from '@/store/bots'; 
import useUsersStore from '@/store/users'; 
import BotTable from '@/components/BotTable.vue'; 


export default defineComponent({
  name: 'AdminComponent',
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
  setup() {
    const botsStore = useBotsStore();
    const usersStore = useUsersStore();

    onMounted(async () => {
      await botsStore.getBots();
      await usersStore.viewMe();
    });

    const bots = computed(() => botsStore.stateBots);
    const user = computed(() => usersStore.stateUser);

    return { bots, user };
  }
  // async created() {
  //   const botsStore = useBotsStore();
  //   const usersStore = useUsersStore();
  //   await botsStore.getBots();
  //   await usersStore.viewMe();
  // },
  // computed: {
  //   bots() {
  //     const botsStore = useBotsStore();
  //     return botsStore.stateBots;
  //   },
  //   user() {
  //     const usersStore = useUsersStore();
  //     return usersStore.stateUser; 
  //   },
  // },
});
</script>