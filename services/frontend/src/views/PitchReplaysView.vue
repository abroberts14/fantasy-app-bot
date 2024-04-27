<template>
  <Card class="card-settings">
    <template #title>Settings</template>
    <template #content class="content-flex">

      <div class="settings-item">
        <FloatLabel>
      
          <AutoComplete
            v-model="selectedPlayer"
            :suggestions="players"
            :loading="loading"
            field="name"
            :delay="300"
            forceSelection 
            placeholder="Search player..."
            @complete="searchPlayers($event)" 
            :dropdown="true" 
            id="search-player"
          />
          <label for="search-player">Search Batters</label>
        </FloatLabel>
      <FloatLabel>
          <Calendar :showIcon="true" dateFormat="yy-mm-dd" :showButtonBar="true" v-model="calendarValue" id="calendar"></Calendar>
          <label for="calendar">Date</label>
      </FloatLabel>
      </div>
    </template>
    <template #footer>
      <div class="footer-buttons">
        <Button label="Apply Filter" @click="fetchPitches" />
        <Checkbox v-model="paOnly" inputId="plateAppearanceOnly" name="plateAppearanceOnly" binary class="filter-checkbox" />
       <label for="plateAppearanceOnly">Plate Appearance Results Only</label>
      </div>
    </template>
  </Card>
  <LoadingSpinner v-if="videoPlayerLoading" />

  <section class="video-section">
    <div v-if="currentPitches.length > 0">
      <VideoPlayer :videos="currentPitches" :reset-player="resetPlayer" :loading="videoPlayerLoading" />
    </div>
    <div v-else>
      <p> No pitches found. </p>
    </div>
  </section>
</template>

<script>
import { defineComponent } from 'vue';
import useUsersStore from '@/store/users';
import LoginComponent from '@/components/LoginComponent.vue';
import LoadingSpinner from '@/components/LoadingSpinner.vue';
import VideoPlayer from '@/components/VideoPlayer.vue';
import axios from 'axios';

export default defineComponent({
  name: 'HomeView',

  components: {
    LoginComponent,
    VideoPlayer,
    LoadingSpinner
  },

  data() {
    return {
      currentPitches: [],
      pitches: [],
      paOnly: true,
      resetPlayer: false,
      videoPlayerLoading: false,
      players: [],
      loading: false,
      searchQuery: '',
      selectedPlayer: {'name': '', 'id': 0}, // Store selected player data
      calendarValue: this.getYesterdayDate(),
    };
  },

  computed: {
    isLoggedIn() {
      const usersStore = useUsersStore();
      return usersStore.isAuthenticated;
    },
    formattedCalendarValue() {
      if (this.calendarValue) {
        const date = new Date(this.calendarValue);
        return date.toISOString().slice(0, 10);
      }
      return null;
   },
  },

  methods: {
    getYesterdayDate() {
      const today = new Date();
      const yesterday = new Date(today);
      yesterday.setDate(yesterday.getDate() - 1);
      return yesterday.toISOString().slice(0, 10);
    },
    searchPlayers(event) {
      if (!event.query || !event.query.trim()) {
        this.players = []; // Clear suggestions if query is empty or not a string
        return;
      }
      this.loading = true;
      axios.get(`/baseball/players/?name=${encodeURIComponent(event.query)}`)
        .then(response => {
            this.players = response.data.map(player => ({
                name_first: player.name_first,
                name_last: player.name_last,
                name: `${player.name_first} ${player.name_last}`,
                id: player.key_mlbam  // Ensure this matches your data structure
            }));
            console.log('Fetched players:', this.players);  // Log to debug
        })
        .catch(error => {
            console.error('Error fetching players:', error);
        })
        .finally(() => {
            this.loading = false;
        });
    },


   
    fetchPitches() {
      console.log('Fetching pitches for player:', this.selectedPlayer.id)
      this.videoPlayerLoading = true;
      this.resetPlayer = true;
      this.$nextTick(() => {
        this.resetPlayer = false;
      });
      axios.get('/baseball/pitches', { params: { player_id: this.selectedPlayer.id, date: this.formattedCalendarValue } })
        .then(response => {
          this.$router.push({ query: { date:  this.formattedCalendarValue, name:this.selectedPlayer.name, playerId: this.selectedPlayer.id } });

          this.processPitches(response.data.pitches);
          this.videoPlayerLoading = false;

        })
        .catch(error => {
          console.error('Error fetching pitches:', error);
          this.handleError(error);
          this.videoPlayerLoading = false;

        });
    },

    processPitches(pitches) {
      const pitchData = [];
      for (const key in pitches) {
        if (this.paOnly) {
          const lastPitch = pitches[key][pitches[key].length - 1];
          pitchData.push(lastPitch);
        } else {
          pitches[key].forEach(pitch => {
            pitchData.push(pitch);
          });
        }
      }
      this.currentPitches = pitchData;
      this.resetPlayer = true;
      this.$nextTick(() => {
        this.resetPlayer = false;
      });
    },

    handleError(error) {
      console.error('Operation failed:', error.message);
    },

    toggleResetPlayer() {
      this.resetPlayer = !this.resetPlayer;
    },


  },

  mounted() {
    if (this.$route.query.date) {
      this.calendarValue = this.$route.query.date;
    }
    if (this.$route.query.playerId) {
      this.selectedPlayer.id = this.$route.query.playerId;
      this.selectedPlayer.name = this.$route.query.name;
      // You might also need to fetch the player data here
    }
    this.fetchPitches();
  },

  emits: ['reset-video-player'],
});
</script>

<style scoped>
.card-settings {
  width: 50rem;
  overflow: hidden;
  
}

.settings-checkbox {
  margin: 0;
  display: flex;
  align-items: center;
}

.search-input,
.dropdown-full-width {
  width: 100%;
}

.footer-buttons {
  display: flex;
  align-items: center; /* Center align the button and checkbox vertically */
  gap: 20px; /* Space between the button and the checkbox */
  text-align: center;

}

.footer-buttons .filter-checkbox {
  margin-left: 20px; /* Add more space between the button and the checkbox if needed */
}
.video-section {
  justify-content: center;
  align-items: center;
  height: 100vh;
  padding: auto;
}

.content-flex {
  display: flex;
  flex-direction: column;
  justify-content: space-evenly;
  align-items: center;
  height: 100%;  /* Adjust the height as necessary to fit your layout */
}

.settings-item {
  display: flex;
  align-items: center; /* Center align the button and checkbox vertically */
  gap: 20px; /* Space between the button and the checkbox */
  text-align: center;}

</style>

