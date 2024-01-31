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
import { mapGetters, mapActions } from 'vuex';

export default defineComponent({
  name: 'BotComponent',
  props: ['id'],
  async created() {
    try {
      await this.viewBot(this.id);
    } catch (error) {
      console.error(error);
      this.$router.push('/dashboard');
    }
  },
  computed: {
    ...mapGetters({ bot: 'stateBot', user: 'stateUser'}),
  },
  methods: {
    ...mapActions(['viewBot', 'deleteBot']),
    async removeBot() {
      try {
        await this.deleteBot(this.id);
        this.$router.push('/dashboard');
      } catch (error) {
        console.error(error);
      }
    }
  },
});
</script>
