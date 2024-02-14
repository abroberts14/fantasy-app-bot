<template>
  <div v-if="bot">
    <p><strong>Bot Name:</strong> {{ bot.name }}</p>
    <p><strong>League ID:</strong> {{ bot.league_id }}</p>
    <p><strong>GroupMe Bot ID:</strong> {{ bot.groupme_bot_id }}</p>

    <div v-if="user.id === bot.user.id">
      <p><router-link :to="{name: 'EditBot', params:{id: bot.id}}" class="btn btn-primary">Edit</router-link></p>
      <p><button @click="removeBot()" class="btn btn-secondary">Delete</button></p>
    </div>
  </div>
</template>


<script>
import { defineComponent } from 'vue';
import useBotsStore from '@/store/bots'; 
import useUsersStore from '@/store/users'; 

export default defineComponent({
  name: 'BotComponent',
  props: ['id'],
  async created() {
    try {
      const botsStore = useBotsStore(); 
      await botsStore.viewBot(this.id); 
    } catch (error) {
      console.error(error);
      this.$router.push('/dashboard');
    }
  },
  computed: {
    bot() {
      const botsStore = useBotsStore(); 
      return botsStore.stateBot; 
    },
    user() {
      const usersStore = useUsersStore(); 
      return usersStore.stateUser; 
    },
  },
  methods: {
    async removeBot() {
      try {
        const botsStore = useBotsStore(); 
        await botsStore.deleteBot(this.id); 
        this.$router.push('/dashboard');
      } catch (error) {
        console.error(error);
      }
    },
  },
});
</script>