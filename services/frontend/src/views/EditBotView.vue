<template>
  <section>
    <h1>Edit Bot</h1>
    <hr/><br/>

    <form @submit.prevent="submit">
      <div class="mb-3">
        <label for="name" class="form-label">Name:</label>
        <input type="text" name="name" v-model="form.name" class="form-control" />
      </div>
      <div class="mb-3">
        <label for="groupme_bot_id" class="form-label">GroupMe Bot ID:</label>
        <input type="text" name="groupme_bot_id" v-model="form.groupme_bot_id" class="form-control" />
      </div>
      <button type="submit" class="btn btn-primary">Submit</button>
    </form>
  </section>
</template>

<script>
import { defineComponent } from 'vue';
import { mapGetters, mapActions } from 'vuex';

export default defineComponent({
  name: 'EditBot',
  props: ['id'],
  data() {
    return {
      form: {
        name: '',
        groupme_bot_id: '',
      },
    };
  },
  created: function() {
    this.GetBot();
  },
  computed: {
    ...mapGetters({ bot: 'stateBot' }),
  },
  methods: {
    ...mapActions(['updateBot', 'viewBot']),
    async submit() {
    try {
      let bot = {
        id: this.id,
        form: this.form,
      };
      await this.updateBot(bot);
      this.$router.push({name: 'Bot', params:{id: this.bot.id}});
    } catch (error) {
      console.log(error);
    }
    },
    async GetBot() {
      try {
        await this.viewBot(this.id);
        this.form.name = this.bot.name;
        this.form.groupme_bot_id = this.bot.groupme_bot_id;
      } catch (error) {
        console.error(error);
        this.$router.push('/dashboard');
      }
    }
  },
});
</script>
