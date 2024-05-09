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
            :delay="750"
            forceSelection 
            placeholder="Search player..."
            @complete="searchPlayers($event)" 
            @item-select="onPlayerSelect"
            :dropdown="true" 
            :disabled="isPageLoading"
            id="search-player"
          />
          <label for="search-player">Search Batters</label>
        </FloatLabel>
          <div class="calendar-container">
            <FloatLabel>

              <Calendar   @month-change="onMonthChange" :disabledDates="disabledDates" :disabled="calendarLoading" :showIcon="true" dateFormat="yy-mm-dd"  :showButtonBar="true" v-model="calendarValue"  :maxDate="todayValue"  id="calendar"></Calendar>
              <label for="calendar">Date</label>
              <div v-if="calendarLoading" class="calendar-loading-overlay">
                <ProgressSpinner style="width: 50px; height: 50px" strokeWidth="8"></ProgressSpinner>          
              </div>
            </FloatLabel>

        </div>
      </div>
    </template>
    <template #footer>
      <div class="footer-buttons">
        <Button :disabled="isPageLoading" label="Apply Filter" @click="fetchPitches" />
        <Checkbox :disabled="isPageLoading" v-model="paOnly" inputId="plateAppearanceOnly" name="plateAppearanceOnly" binary class="filter-checkbox" />
       <label for="plateAppearanceOnly">Plate Appearance Results Only</label>
      </div>
    </template>
  </Card>
  <LoadingSpinner v-if="videoPlayerLoading" />

  <!-- :disabledDates="disabledDates" -->

  <section class="video-section">
    <div v-if="currentPitches.length > 0">
      <!-- <div v-for="(video, index) in currentPitches" :key="index"> 
        <MobileVideoPlayer :videoUrl="video.mp4"  :videos="currentPitches"  autoplay="false"  />
        </div> -->
        <MediaPlayer :videos="currentPitches" :reset="videoPlayerLoading"  autoplay="false"  />

    </div>
      <div v-else>
        <p> No pitches found. </p>

        

        <div v-if="userTokenPresent">
            <Button @click="syncMyPlayers">Sync My Players From Yahoo</Button>
            <div v-if="batters.length > 0">
              <p>My Players:</p>
              <ul>
                <li v-for="(batter, index) in batters" :key="index">{{ batter.name }}</li>
              </ul>
            </div>
          <!-- Add a fallback UI for empty batters -->
          <div v-else>
            <p>No players loaded.</p>
          </div>
        </div>
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
import MobileVideoPlayer from '@/components/MobileVideoPlayer.vue';
import MediaPlayer from '@/components/MediaPlayer.vue';
export default defineComponent({
  name: 'HomeView',

  components: {
    LoginComponent,
    VideoPlayer,
    MobileVideoPlayer,
    LoadingSpinner,
    MediaPlayer
  },

  data() {
    return {
      currentPitches: [],
      pitches: [],
      paOnly: true,
      videoPlayerLoading: false,
      players: [],
      loading: false,
      searchQuery: '',
      selectedPlayer: {'name': '', 'id': 0}, // Store selected player data
      calendarValue: this.getYesterdayDate(),
      calendarLoading: false,
      disabledDates: [],
      screenWidth: window.innerWidth,
      screenHeight: window.innerHeight,
      batters: [],
      userTokenPresent: false,
      oauth_response: null,
      todayValue: this.getYesterdayDate(false),
    };
  },

  computed: {
    isLoggedIn() {
      const usersStore = useUsersStore();
      return usersStore.isAuthenticated;
    },
    user() {
      const usersStore = useUsersStore(); 
      return usersStore.stateUser; 
    },
    isPageLoading() {
      return this.videoPlayerLoading || this.calendarLoading;
    },
    formattedCalendarValue() {
      if (this.calendarValue) {
        const date = new Date(this.calendarValue);
        return date.toISOString().slice(0, 10);
      }
      return null;
   }
  },

  methods: {
    async  fetchUserTokens() {
      try {

        const response = await axios.get(`/oauth/yahoo/tokens`, {
          params: {
            user_id: this.user.id
          }
        });        
        console.log('API Response:', response.data);
        this.oauth_response = response.data;
      } catch (error) {
        console.error('Failed to fetch Yahoo integration:', error);
      }
      finally {
        console.log("oauth_respons length: ", this.oauth_response);
        this.userTokenPresent = this.oauth_response;
        console.log("userTokenPresent: ", this.userTokenPresent);
      }
    },
    async fetchMyPlayers() {
      const usersStore = useUsersStore();
      if (!usersStore.isAuthenticated) {
        console.error('User is not logged in or token is not available');
        return;
      }
      try {
        const response = await axios.get('/baseball/players/my-players');
        console.log('API Response:', response.data);
        if (response.data.players.batters) {
          this.batters = response.data.players.batters;
          console.log('response assigned:', response.data.players.batters);

          console.log('Batters assigned:', this.batters);
        } else {
          console.error('Batters data is not in expected format:', response.data);
        }
      } catch (error) {
        console.error('Failed to fetch players:', error);
        this.batters = []; // Reset batters on error
      }
    },
    async syncMyPlayers() {
      const usersStore = useUsersStore();
      if (!usersStore.isAuthenticated) {
        console.error('User is not logged in or token is not available');
        return;
      }
      try {
        const response = await axios.get('/baseball/players/sync_players');
        console.log('API Response:', response.data);
        if (response.data.players.batters) {
          this.batters = response.data.players.batters;
          console.log('response assigned:', response.data.players.batters);

          console.log('Batters assigned:', this.batters);
        } else {
          console.error('Batters data is not in expected format:', response.data);
        }
      } catch (error) {
        console.error('Failed to fetch players:', error);
        this.batters = []; // Reset batters on error
      }
    },
    onPlayerSelect(event) {
      console.log('Player selected:', event);
      this.selectedPlayer = event.value;
      console.log('Selected player:', this.selectedPlayer);
      if (this.selectedPlayer && this.selectedPlayer.id) {
        const today = new Date();
        const thirtyDaysAgo = new Date(today.getFullYear(), today.getMonth(), today.getDate() - 30);
        
        // Format dates as 'YYYY-MM-DD'
        const startDate = thirtyDaysAgo.toISOString().slice(0, 10);
        const endDate = today.toISOString().slice(0, 10);

        console.log(`Fetching valid dates for ${startDate} to ${endDate}`);
        this.fetchValidDates(this.selectedPlayer.id, thirtyDaysAgo, today);
      }
    },
    onMonthChange(date) {
      // date parameter is the date of the month shown in the calendar after the change
      console.log('Month changed:', date);  
      const startOfMonth = new Date(date.year, date.month -1, 1);
      const endOfMonth = new Date(date.year, date.month, 0); // Last day of the month

      console.log(`Month change fetch valid dates from ${startOfMonth} to ${endOfMonth}`);
      this.fetchValidDates(this.selectedPlayer.id, startOfMonth, endOfMonth);
    },


    fetchValidDates(playerId, startDate, endDate) {
      if (!startDate || !endDate) {
        console.error('fetchValidDates requires both startDate and endDate.');
        this.disabledDates = [];
        return;
      }

      const params = new URLSearchParams({
        start_date: startDate.toISOString().slice(0, 10), // format as 'YYYY-MM-DD'
        end_date: endDate.toISOString().slice(0, 10)     // format as 'YYYY-MM-DD'
      }).toString();
      this.calendarLoading = true;
      axios.get(`/baseball/player-valid-dates/${playerId}?${params}`)
        .then(response => {
          if (response.data) {
            // Assume response.data contains the disabled dates
            this.disabledDates = response.data.map(date => new Date(date));
            this.disabledDates.push(new Date());
            // Find the latest date that is not disabled
            this.updateSelectedDate(startDate, endDate);
          } else {
            this.disabledDates = [];
          }
        })
        .catch(error => {
          console.error('Error fetching valid dates:', error);
          this.disabledDates = [];
        })
        .finally(() => {
          console.log('Disabled dates:', this.disabledDates);
          this.calendarLoading = false;
        });
    },

    updateSelectedDate(startDate, endDate) {
      let latestValidDate = null;

      // Create a loop from end of month to start of month
      for (let d = endDate; d >= startDate; d.setDate(d.getDate() - 1)) {
        if (!this.disabledDates.some(disabledDate => 
          disabledDate.getDate() === d.getDate() && 
          disabledDate.getMonth() === d.getMonth() && 
          disabledDate.getFullYear() === d.getFullYear())) {
          latestValidDate = new Date(d);
          break;
        }
      }

      if (latestValidDate) {
        // If a valid date is found, update your calendar's selected date
        this.calendarValue = latestValidDate;
        console.log('Updated selected date to:', this.calendarValue);
      } else {
        console.log('No valid dates available in the selected month.');
      }
    },
   
    getTodayDate() {
      const today = new Date();
      const formattedDate = today.toISOString().slice(0, 10);
      console.log("Today's date calculated as:", formattedDate); // Debug output
      return today;
    },
    getYesterdayDate(formatted = true) {
      const today = new Date();
      const yesterday = new Date(today);
      yesterday.setDate(yesterday.getDate() - 1);
      const formattedDate = yesterday.toISOString().slice(0, 10);
      console.log("Yesterday's date calculated as:", formattedDate); // Debug output
      if (formatted) {
        return formattedDate;
      } else {
        return yesterday;
      }
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

      console.log('currentPitches:', this.currentPitches);
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

      console.log('currentPitches:', this.currentPitches);
      console.log('mp4 ', this.currentPitches[0].mp4);
    },

    handleError(error) {
      console.error('Operation failed:', error.message);
    },




  },

  mounted() {
    console.log("Before setting initial value:", this.calendarValue);
    this.calendarValue = this.getYesterdayDate();
    console.log("After setting initial value:", this.calendarValue);

    if (this.$route.query.date) {
      this.calendarValue = this.$route.query.date;
      console.log("Setting from route query:", this.calendarValue);
    }
    this.fetchUserTokens();
    this.fetchMyPlayers();
    this.fetchPitches();
  },

});

</script>

<style scoped>
.card-settings {
  width: auto;;
  overflow:auto;
  
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


.video-container {
  margin-bottom: 20px; /* Adjust the gap size as needed */
}

</style>

