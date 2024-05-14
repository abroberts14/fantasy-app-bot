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
  name: 'PitchReplaysView',
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

    const validDates = ref([]);
    const disabledDates = ref([]);
    const latestDisabledDate = ref(null);
    const latestValidDate = ref(null);
    const todayValue = ref(getYesterdayDate(false));
    const paOnly = ref(true);
    const batters = ref([]);
    const userTokenPresent = ref(null);

    const user = computed(() => usersStore.user);
    const currentPitch = ref(0);
    const currentQuery = ref({ player_id: 0, date: '', name: '', current_pitch: 0});
    const isLoggedIn = computed(() => usersStore.isAuthenticated);
    const isPageLoading = computed(() => videoPlayerLoading.value || calendarLoading.value);


    const formattedCalendarValue = computed(() => {
      if (calendarValue.value instanceof Date) {
        return new Date(Date.UTC(
          calendarValue.value.getFullYear(),
          calendarValue.value.getMonth(),
          calendarValue.value.getDate(),
          12, 0, 0
        ))
      }
      return calendarValue.value;
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
      axios.get(`/baseball/get-player-dates/${playerId}?${params}`)
        .then(response => {
          if (response.data) {
            validDates.value = response.data.valid_dates;
            latestDisabledDate.value = response.data.latest_disabled_date;
            latestValidDate.value = response.data.latest_valid_date;
            disabledDates.value = response.data.disabled_dates.map(dateStr => {
                        let date = new Date(dateStr);
                        date.setUTCHours(12, 0, 0, 0); // Set time to noon UTC
                        return date;
                    });

            calendarValue.value = latestValidDate.value;

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
      console.log("current query from fetchpithces", currentQuery.value)
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
      syncMyPlayers,
      validDates,
      disabledDates,
      latestDisabledDate,
      latestValidDate,
      };
  },
  mounted() {
    this.fetchUserTokens();
    this.calendarValue = this.getYesterdayDate(false);
    let autoApplyFilter = false;

    if (this.$route.query.playerId) {
      this.calendarValue = this.$route.query.date;

      this.selectedPlayer = { name: decodeURIComponent(this.$route.query.name), id: this.$route.query.playerId };      
      // set current pitch to 0 if its null 
      this.currentPitch = parseInt(this.$route.query.current_pitch) || 0 
      this.currentQuery = { player_id: this.$route.query.playerId, date: this.$route.query.date, name: decodeURIComponent(this.$route.query.name), current_pitch: parseInt(this.$route.query.current_pitch) || 0 };
      

      console.log("Setting from route query:", this.selectedPlayer);
      console.log("current query from route:", this.currentQuery);
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
