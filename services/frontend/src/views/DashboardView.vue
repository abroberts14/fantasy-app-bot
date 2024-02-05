<template>
  <div>
    <section>
      <h1>Bots</h1>
      <hr/><br/>

      <div v-if="bots.length">
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
import { mapGetters, mapActions } from 'vuex';

export default defineComponent({
  name: 'DashboardComponent',
  data() {
    return {
      form: {
        title: '',
        content: '',
      },
    };
  },
  created: function() {
    this.$store.dispatch('getBots');  // Fetch the bots when the component is created
  },
  computed: {
    ...mapGetters({ bots: 'stateBots' }),  // Add a new getter for bots
  },
});
</script>