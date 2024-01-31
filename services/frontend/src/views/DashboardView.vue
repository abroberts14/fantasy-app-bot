<template>
  <div>
    <section>
      <h1>Add new note</h1>
      <hr/><br/>

      <form @submit.prevent="submit">
        <div class="mb-3">
          <label for="title" class="form-label">Title:</label>
          <input type="text" name="title" v-model="form.title" class="form-control" />
        </div>
        <div class="mb-3">
          <label for="content" class="form-label">Content:</label>
          <textarea
            name="content"
            v-model="form.content"
            class="form-control"
          ></textarea>
        </div>
        <button type="submit" class="btn btn-primary">Submit</button>
      </form>
    </section>

    <br/><br/>

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
      </section>
    <section>
      <h1>Notes</h1>
      <hr/><br/>

      <div v-if="notes.length">
        <div v-for="note in notes" :key="note.id" class="notes">
          <div class="card" style="width: 18rem;">
            <div class="card-body">
              <ul>
                <li><strong>Note Title:</strong> {{ note.title }}</li>
                <li><strong>Author:</strong> {{ note.user.username }}</li>
                <li><router-link :to="{name: 'Note', params:{id: note.id}}">View</router-link></li>
              </ul>
            </div>
          </div>
          <br/>
        </div>
      </div>

      <div v-else>
        <p>Nothing to see. Check back later.</p>
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
    this.$store.dispatch('getNotes');
    this.$store.dispatch('getBots');  // Fetch the bots when the component is created
  },
  computed: {
    ...mapGetters({ notes: 'stateNotes', bots: 'stateBots' }),  // Add a new getter for bots
  },
  methods: {
    ...mapActions(['createNote', 'getBots']),  // Add a new action for getting bots
    async submit() {
      await this.createNote(this.form);
    },
  },
});
</script>