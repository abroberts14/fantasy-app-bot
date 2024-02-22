<template>
  <div>
    <h1>All Bots</h1>
    <hr/><br/>
    <BotTable :bots="bots" :loaded="loaded" />
  </div>
</template>

<script>
import { defineComponent, onMounted, computed, ref} from 'vue';
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
    const loaded = ref(false);
    const fetchData = async () => {
      loaded.value = false;
      await usersStore.viewMe();
      await botsStore.getBots();
      loaded.value = true;
    };

    onMounted(() => {
      fetchData();
    });
    const bots = computed(() => botsStore.stateBots);
    const user = computed(() => usersStore.stateUser);

    return { bots, user, loaded };
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