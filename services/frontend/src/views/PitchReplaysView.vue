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
            @complete="searchPlayers"
            @item-select="onPlayerSelect"
            :dropdown="true"
            :disabled="isPageLoading"
            id="search-player"
          />
          <label for="search-player">Search Batters</label>
        </FloatLabel>
        <div class="calendar-container">
          <FloatLabel>
            <Calendar
              @month-change="onMonthChange"
              :disabledDates="disabledDates"
              :disabled="calendarLoading"
              :showIcon="true"
              dateFormat="yy-mm-dd"
              :showButtonBar="true"
              v-model="calendarValue"
              :maxDate="todayValue"
              id="calendar"
            />
            <label for="calendar">Date</label>
            <div v-if="calendarLoading" class="calendar-loading-overlay">
              <ProgressSpinner style="width: 50px; height: 50px" strokeWidth="8" />
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
  <section class="video-section">
    <div v-if="currentPitches.length > 0">

      <MediaPlayer :videos="currentPitches" :reset="videoPlayerLoading" :currentQuery="currentQuery" autoplay="false" />
    </div>
    <div v-else>
      <p>No pitches found.</p>
      <div v-if="userTokenPresent">
        <Button @click="syncMyPlayers">Sync My Players From Yahoo</Button>
        <div v-if="batters.length > 0">
          <p>My Players:</p>
          <ul>
            <li v-for="(batter, index) in batters" :key="index">{{ batter.name }}</li>
          </ul>
        </div>
        <div v-else>
          <p>No players loaded.</p>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import { defineComponent, ref, computed  } from 'vue';
import useUsersStore from '@/store/users';
import MediaPlayer from '@/components/MediaPlayer.vue';
import LoadingSpinner from '@/components/LoadingSpinner.vue';
import axios from 'axios';

export default defineComponent({
  name: 'HomeView',
  components: {
    MediaPlayer,
    LoadingSpinner,
  },
  setup() {
    const usersStore = useUsersStore();
    const selectedPlayer = ref({ name: '', id: 0 });
    const players = ref([]);
    const loading = ref(false);
    const currentPitches = ref([]);
    const videoPlayerLoading = ref(false);
    const calendarValue = ref(getYesterdayDate());
    const calendarLoading = ref(false);

    const disabledDates = ref();
    const todayValue = ref(getYesterdayDate(false));
    const paOnly = ref(true);
    const batters = ref([]);
    const userTokenPresent = ref(null);

    const user = computed(() => usersStore.user);
    const currentPitch = ref(0);
    const currentQuery = ref({ player_id: 0, date: '', name: '', current_pitch: 0});
    const isLoggedIn = computed(() => usersStore.isAuthenticated);
    const isPageLoading = computed(() => videoPlayerLoading.value || calendarLoading.value);

    // const disabledDates = computed(() => {
    //     if (Array.isArray(disabledDates.value)) {

    //       return disabledDates.value.map(dateStr => {
    //         // Ensure the date string includes time part 'T00:00:00Z' to parse as UTC
    //         const dateTimeStr = dateStr.includes('T') ? dateStr : `${dateStr}T00:00:00Z`;
    //         return new Date(dateTimeStr);
    //       });
    //     } else {
    //       return [];
    //     }
    // });
    const formattedCalendarValue = computed(() => {
      
      // Ensure calendarValue is a Date object before calling toISOString
      if (calendarValue.value instanceof Date) {
        return calendarValue.value.toISOString().slice(0, 10);
      } else {
        return calendarValue.value
      }
      c
    });
    function searchPlayers(event) {
      if (!event.query.trim()) {
        players.value = [];
        return;
      }
      loading.value = true;
      axios.get(`/baseball/players/?name=${encodeURIComponent(event.query)}`)
        .then((response) => {
          players.value = response.data.map((player) => ({
            name_first: player.name_first,
            name_last: player.name_last,
            name: `${player.name_first} ${player.name_last}`,
            id: player.key_mlbam
          }));
        })
        .catch((error) => console.error('Error fetching players:', error))
        .finally(() => loading.value = false);
    }
    function   onPlayerSelect(event) {
      console.log('Player selected:', event);
      selectedPlayer.value = event.value;
      console.log('Selected player:', selectedPlayer.value);
      if (selectedPlayer.value && selectedPlayer.value.id) {
        const today = new Date();
        const thirtyDaysAgo = new Date(today.getFullYear(), today.getMonth(), today.getDate() - 30);
        
        // Format dates as 'YYYY-MM-DD'
        const startDate = thirtyDaysAgo.toISOString().slice(0, 10);
        const endDate = today.toISOString().slice(0, 10);
        const yesterday = getYesterdayDate(false);
        console.log(`Fetching valid dates for ${startDate} to ${yesterday}`);
        fetchValidDates(selectedPlayer.value.id, thirtyDaysAgo, getYesterdayDate(false));  
      }
    }
    async function syncMyPlayers() {
      const usersStore = useUsersStore();
      if (!usersStore.isAuthenticated) {
        console.error('User is not logged in or token is not available');
        return;
      }
      try {
        videoPlayerLoading.value = true;
        const response = await axios.get('/baseball/players/sync_players');
        console.log('API Response:', response.data);
        if (response.data.players.batters) {
          batters.value = response.data.players.batters;
          // console.log('response assigned:', response.data.players.batters);

          // console.log('Batters assigned:', this.batters);
        } else {
          console.error('Batters data is not in expected format:', response.data);
        }
      } catch (error) {
        console.error('Failed to fetch players:', error);
        batters.value = []; // Reset batters on error
      } finally {
        videoPlayerLoading.value = false;
      }
    }
    async function fetchUserTokens() {
      try {
        const response = await axios.get(`/oauth/yahoo/tokens`, {
          params: {
            user_id: user.value.id
          }
        });        
        console.log('API Response:', response.data);
        this.oauth_response = response.data;
      } catch (error) {
        console.error('Failed to fetch Yahoo integration:', error);
      }
      finally {
        userTokenPresent.value = this.oauth_response;
      }
    }
    function updateSelectedDate(startDate, endDate) {
      let latestValidDate = null;

      // Create a loop from end of month to start of month
      for (let d = endDate; d >= startDate; d.setDate(d.getDate() - 1)) {
        if (!disabledDates.value.some(disabledDate => 
          disabledDate.getDate() === d.getDate() && 
          disabledDate.getMonth() === d.getMonth() && 
          disabledDate.getFullYear() === d.getFullYear())) {
          latestValidDate = new Date(d);
          break;
        }
      }
      if (latestValidDate) {
        // If a valid date is found, update your calendar's selected date
        calendarValue.value = latestValidDate;
        console.log('Updated selected date to:', calendarValue.value);
      } else {
        console.log('No valid dates available in the selected month.');
        calendarValue.value = null; // or set to a default value

      }
    }

    function onMonthChange(date) {
      console.log('Month changed:', date);
      fetchValidDates(selectedPlayer.value.id, new Date(date.year, date.month - 1, 1), new Date(date.year, date.month, 0));
    }

    function fetchValidDates(playerId, startDate, endDate) {
      if (!startDate || !endDate) {
        console.error('fetchValidDates requires both startDate and endDate.');
        disabledDates.value = [];
        return;
      }

      const params = new URLSearchParams({
        start_date: startDate.toISOString().slice(0, 10), // format as 'YYYY-MM-DD'
        end_date: endDate.toISOString().slice(0, 10)     // format as 'YYYY-MM-DD'
      }).toString();
      calendarLoading.value = true;
      axios.get(`/baseball/player-valid-dates/${playerId}?${params}`)
        .then(response => {
          if (response.data) {
            console.log('Disabled dates str before fetch:', disabledDates.value);
            console.log('Response data:', response.data);
            disabledDates.value = response.data.map(timestamp => {
              // Create a new Date object from the timestamp
              const date = new Date(timestamp * 1000);
              // Construct a UTC date string
              const utcDateString = `${date.getUTCFullYear()}-${String(date.getUTCMonth() + 1).padStart(2, '0')}-${String(date.getUTCDate()).padStart(2, '0')}`;
              // Return the date object created from the UTC date string
              return new Date(date)
            });
            console.log('Disabled dates str in UTC after fetch:', disabledDates.value);
            updateSelectedDate(startDate, endDate);
          } else {
            disabledDates.value = [];
          }
        })
        .catch(error => {
          console.error('Error fetching valid dates:', error);
          disabledDates.value = [];
        })
        .finally(() => {
          console.log('Disabled dates str:', disabledDates.value);
          calendarLoading.value = false;
        });
    }

    function getYesterdayDate(formatted = true) {
      const today = new Date();
      const yesterday = new Date(today.setDate(today.getDate() - 1));
      return formatted ? yesterday.toISOString().slice(0, 10) : yesterday;
    }
    async function fetchPitches() {
      console.log("current query", currentQuery.value)
      videoPlayerLoading.value = true;
        try {
            const response = await axios.get('/baseball/pitches', { 
                params: { player_id: selectedPlayer.value.id, date: formattedCalendarValue.value } 
            });
            if (response.data && response.data.pitches) {
                const allPitches = Object.values(response.data.pitches); // This gives an array of arrays
                currentPitches.value = allPitches.reduce((acc, pitchArray) => {
                    if (paOnly.value) {
                        acc.push(pitchArray[pitchArray.length - 1]); // Assuming each pitch array's last item is the most relevant
                    } else {
                        acc.push(...pitchArray);
                    }
                    return acc;
                }, []);
            }
        } catch (error) {
            console.error('Error fetching pitches:', error);
        } finally {
            videoPlayerLoading.value = false;
            currentQuery.value = { player_id: selectedPlayer.value.id, date: formattedCalendarValue.value , name: selectedPlayer.value.name, current_pitch: currentPitch.value };
            console.log("current query", currentQuery.value)

          }

      }
    
    async function fetchMyPlayers() {
      if (!this.isLoggedIn) {
        console.error('User is not logged in or token is not available');
        return;
      }
      this.loading = true;
      try {
        const response = await axios.get('/baseball/players/my-players');
        this.batters = response.data.players.batters || [];
      } catch (error) {
        console.error('Failed to fetch players:', error);
        this.batters = [];
      } finally {
        this.loading = false;
      }
    }
    return {
      selectedPlayer,
      players,
      loading,
      currentPitches,
      videoPlayerLoading,
      calendarValue,
      calendarLoading,
      disabledDates,
      disabledDates,
      todayValue,
      paOnly,
      batters,
      userTokenPresent,
      isLoggedIn,
      isPageLoading,
      formattedCalendarValue,
      currentQuery,
      currentPitch,
      searchPlayers,
      onMonthChange,
      fetchValidDates,
      fetchPitches,
      fetchMyPlayers,
      onPlayerSelect,
      getYesterdayDate,
      fetchUserTokens,
      syncMyPlayers
      };
  },
  mounted() {
    this.fetchUserTokens();
    this.calendarValue = this.getYesterdayDate(false);

    if (this.$route.query.date) {
      this.calendarValue = this.$route.query.date;
      console.log("Setting from route query:", this.calendarValue);
    }
    if (this.$route.query.playerId) {
      this.selectedPlayer = { name: decodeURIComponent(this.$route.query.name), id: this.$route.query.playerId };      
      if (this.$route.query.current_pitch) {
        console.log("Setting current pitch from route query:", this.$route.query.current_pitch);
        this.currentPitch = parseInt(this.$route.query.current_pitch);        
        this.currentQuery = { player_id: this.$route.query.playerId, date: this.$route.query.date, name: this.$route.query.name, current_pitch: this.currentPitch };
      } else {
        this.currentQuery = { player_id: this.$route.query.playerId, date: this.$route.query.date, name: this.$route.query.name, current_pitch: 0 };
      }

      console.log("Setting from route query:", this.selectedPlayer);
    }
    this.fetchMyPlayers();
    if (this.selectedPlayer && this.selectedPlayer.id) {
      this.fetchPitches();
    }
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
