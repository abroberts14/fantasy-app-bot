<template>
  <div>
    <section>
      <h1>All Bots</h1>
      <hr/><br/>

      <div v-if="bots?.length">
        <div v-for="bot in bots" :key="bot.id" class="bots">
          <div class="card" style="width: 18rem;">
            <div class="card-body">
              <ul>
                <li><strong>Bot Name:</strong> {{ bot.name }}</li>
                <li><strong>League ID:</strong> {{ bot.league_id }}</li>
                <li><strong>GroupMe Bot ID:</strong> {{ bot.groupme_bot_id }}</li>

                <li><router-link :to="{name: 'Bot', params:{id: bot.id}}">View</router-link></li>
              </ul>
            </div>
          </div>
          <br/>
        </div>
      </div>

      <!-- Show a message and a link to register-bot if no bots exist -->
      <div v-else>
        <p>No fantasy chat bots exist. <router-link to="/register-bot">Register a new bot</router-link></p>
      </div>
    </section>
  </div>
</template>

<script>
import { defineComponent } from 'vue';
import useBotsStore from '@/store/bots'; 
import useUsersStore from '@/store/users'; 

export default defineComponent({
  name: 'AdminComponent',
  data() {
    return {
      form: {
        title: '',
        content: '',
      },
    };
  },
  async created() {
    const botsStore = useBotsStore(); 
    await botsStore.getBots()
    const usersStore = useUsersStore(); 
    await usersStore.viewMe(); // Call the action from your users store
  },
  computed: {
    bots() {
      const botsStore = useBotsStore(); 
      const userId = this.user.id; // Replace this with your actual user ID retrieval logic

      return botsStore.stateBots;
    },
    user() {
      const usersStore = useUsersStore(); 
      return usersStore.stateUser; 
    },
  },
});
</script>