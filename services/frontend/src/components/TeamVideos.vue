

<template>
  

    <section class="video-section">
      <LoadingSpinner v-if="loadingPlayers" />
      <DataTable 
          @row-expand="setExpandedRow" 
          @row-collapse="setCollapsedRow" 
          scrollable 
          scrollHeight="dynamicScrollHeight" 
          v-model:expandedRows="expandedRow" 
          :value="batters" 
          dataKey="key_mlbam" 
          class="p-datatable-sm"
        >      
        <Column expander style="width: 3rem"/>
        <Column field="name" header="Batter">
          <template #body="slotProps">
            {{ slotProps.data.name }}
            <span v-if="slotProps.data.isLoading" class="loading-spinner">
              <ProgressSpinner style="width: 20px; height: 20px" strokeWidth="8" fill="var(--surface-ground)" animationDuration=".5s" aria-label="Loading data" />
            </span>
          </template>
        </Column>
        <template #expansion="slotProps">
  
            <div v-if="slotProps.data.isLoading">
              <InlineMessage severity="info">Loading...</InlineMessage>
            </div>
            <div v-else>
              
            <span v-if="videoPlayerLoading " class="loading-spinner">
              <ProgressSpinner style="width: 20px; height: 20px" strokeWidth="8" fill="var(--surface-ground)" animationDuration=".5s" aria-label="Loading data" />
            </span> 
            <div v-if="!slotProps.data.latestValidDate">
              <InlineMessage severity="warn">No plays loaded</InlineMessage>
            </div>
            <div v-if="currentPitches.length > 0 && !videoPlayerLoading" >
  
              <MediaPlayer :videos="currentPitches" :reset="videoPlayerLoading" :currentQuery="currentQuery" autoplay="false" />
              </div>
             <!-- Output the latestValidDate -->
             <!-- <p>Latest valid date: {{ slotProps.data.latestValidDate }}</p> -->
             <!-- Loop through and output the disableddates in a list -->
             <!-- <ul>
               <li v-for="date in slotProps.data.disabledDates" :key="date">{{ date }}</li>
             </ul> -->
            </div>
        </template>
      </DataTable>
  
    </section>
  </template>
  
  <script>
  import { defineComponent, ref, computed, onMounted, onUnmounted , nextTick } from 'vue';
  import useUsersStore from '@/store/users';
  import MediaPlayer from '@/components/MediaPlayer.vue';
  import LoadingSpinner from '@/components/LoadingSpinner.vue';
  import axios from 'axios';
  import ModalOverlay from '@/components/ModalOverlay.vue';
  import { useRouter } from 'vue-router';
  
  export default defineComponent({
    name: 'TeamVideosView',
    components: {
      MediaPlayer,
      LoadingSpinner,
      ModalOverlay
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
      const router = useRouter();
      const loadingPlayers = ref(false);
      const disabledDates = ref();
      const todayValue = ref(getYesterdayDate(false));
      const paOnly = ref(true);
      const batters = ref([]);
      const user = computed(() => usersStore.user);
      const currentPitch = ref(0);
      const currentQuery = ref({ player_id: 0, date: '', name: '', current_pitch: 0});
      const isLoggedIn = computed(() => usersStore.isAuthenticated);
      const isPageLoading = computed(() => videoPlayerLoading.value || calendarLoading.value);
      const expandedRow = ref([])
  
      const dynamicScrollHeight = ref('900px'); // Default value
      const debugConsole = true;
      function updateScrollHeight() {
        const width = window.innerWidth;
        const height = window.innerHeight;
  
        // if (height < 768) {
        //   dynamicScrollHeight.value = '300px'; // Smaller height for mobile devices
        // } else {
        //   dynamicScrollHeight.value = '900px'; // Larger height for desktop
        // }
      }
  
     
      const formattedCalendarValue = computed(() => {
        
        // Ensure calendarValue is a Date object before calling toISOString
        if (calendarValue.value instanceof Date) {
          return calendarValue.value.toISOString().slice(0, 10);
        } else {
          return calendarValue.value
        }
        c
      });
      function debugLog(message) {
        if (debugConsole) {
          console.log(message);
        }
      }
    
      
      function onMonthChange(date) {
        debugLog('Month changed:', date);
        fetchValidDates(selectedPlayer.value.id, new Date(date.year, date.month - 1, 1), new Date(date.year, date.month, 0));
      }

  
      function getYesterdayDate(formatted = true) {
        const today = new Date();
        const yesterday = new Date(today.setDate(today.getDate() - 1));
        return formatted ? yesterday.toISOString().slice(0, 10) : yesterday;
      }

      async function fetchPitches(playerId, date) {
        debugLog("Fetching pitches for player ID:", playerId, "on date:", date);
        const player = batters.value.find(p => p.key_mlbam === playerId);
        console.log('player', player)
        
        // Check if the player already has pitches loaded for this date
        if (player && player.pitches && player.pitches[date]) {
            debugLog("Using cached pitches for player ID:", playerId, "on date:", date);
            currentPitches.value = player.pitches[date];
            return; // Skip the API call
        }

        player.isLoading = true; // Ensure loading is true when starting to fetch

        videoPlayerLoading.value = true;

        try {
            const response = await axios.get('/baseball/pitches', { 
            params: { player_id: playerId, date: date }
            });

            if (response.data && response.data.pitches) {
            const allPitches = Object.values(response.data.pitches); // This gives an array of arrays
            const pitches = allPitches.reduce((acc, pitchArray) => {
                if (paOnly.value) {
                acc.push(pitchArray[pitchArray.length - 1]); // Assuming each pitch array's last item is the most relevant
                } else {
                acc.push(...pitchArray);
                }
                return acc;
            }, []);

            // Save the fetched pitches to the player object
            if (!player.pitches) {
                player.pitches = {};
            }
            player.pitches[date] = pitches;
           //currentPitches.value = pitches;
            }
        } catch (error) {
            console.error('Error fetching pitches:', error);
        } finally {
            player.isLoading = false; // Loading done
            videoPlayerLoading.value = false;
           // currentQuery.value = { player_id: playerId, date: date, name: selectedPlayer.value.name, current_pitch: currentPitch.value };
            debugLog("Current query", currentQuery.value);
        }
    }
      
      async function fetchMyPlayers() {
        if (!this.isLoggedIn) {
          console.error('User is not logged in or token is not available');
          return;
        }
        loadingPlayers.value = true;
        try {
          const response = await axios.get('/baseball/players/my-players');
          this.batters = response.data.players.batters || [];
        } catch (error) {
          console.error('Failed to fetch players:', error);
          this.batters = [];
        } finally {
          loadingPlayers.value = false;
  
          //this.fetchAndSetPlayerData()
        }
      }
      async function fetchPlayerData(player) {
        if (!player) {
          console.error('fetchPlayerData requires a player object.');
          return;
        }

        player.isLoading = true;  // Set loading to true initially
        const startDate = getYesterdayDate(false); // Assuming getYesterdayDate function exists and returns Date object
        const endDate = new Date(); // Today's date

        const params = new URLSearchParams({
          start_date: startDate.toISOString().slice(0, 10), // format as 'YYYY-MM-DD'
          end_date: endDate.toISOString().slice(0, 10)     // format as 'YYYY-MM-DD'
        }).toString();

        debugLog('params', params);

        try {
          const response = await axios.get(`/baseball/get-player-dates/${player.key_mlbam}?${params}`);
          if (response.data) {
            player.validDates = response.data.valid_dates;
            player.disabledDates = response.data.disabled_dates.map(dateStr => {
              let date = new Date(dateStr);
              date.setUTCHours(12, 0, 0, 0); // Set time to noon UTC
              return date;
            });
            player.latestValidDate = response.data.latest_valid_date;
            player.latestDisabledDate = response.data.latest_disabled_date;
          } else {
            player.disabledDates = [];
            player.latestValidDate = null;
            player.validDates = [];
          }
          if (player.latestValidDate) {
            await fetchPitches(player.key_mlbam, player.latestValidDate);
          } else {
            debugLog("No latest valid date for player ID:", player.key_mlbam);
          }
        } catch (error) {
          console.error(`Error fetching valid dates for player ${player.key_mlbam}:`, error);
          player.disabledDates = [];
        } finally {
          player.isLoading = false;
        }
      }
        
      async function setExpandedRow($event) {
        console.log('rowData', $event.data);
        
        currentPitches.value = [];

        // Reset expanded rows to ensure only one can be open at a time
        if (expandedRow.value !== $event.data.key_mlbam) {
          expandedRow.value = {};
        }

        await fetchPlayerData($event.data);

        nextTick(() => {
          const rowData = $event.data;
          const videoPlayerElement = document.querySelector('.p-datatable-row-expansion');
          if (videoPlayerElement) {
              const topPos = videoPlayerElement.offsetTop;
              window.scrollTo({
                  top: topPos - 100,
                  behavior: 'smooth'
              });
          } else {
              console.log('Video player element not found:', '#row-' + rowData.key_mlbam + ' .video-player-class');
          }
        });

        // Set the current row as the expanded row
        expandedRow.value = { [ $event.data.key_mlbam ]: true };

        debugLog('expandedRow POST', expandedRow.value);
        if ($event.data.latestValidDate) {
          await trackPlayer($event.data.key_mlbam, $event.data.latestValidDate);
        }
      }
      function setCollapsedRow($event) {
        debugLog('rowData collapse', $event.data);
        expandedRow.value = {};
        debugLog('collapsed POST', expandedRow.value);
  
      }
      async function trackPlayer(playerId, date) {
        // Logic to track the selected player ID and date
        debugLog(`Tracking player ${playerId} with date ${date}`);
        currentQuery.value = { player_id: playerId, date: date, name: selectedPlayer.value.name, current_pitch: 0 };
        debugLog("Current query", currentQuery.value);
        await fetchPitches(playerId, date);
  
        // Store this information or perform additional actions
      }
      onMounted(() => {
        updateScrollHeight();
        window.addEventListener('resize', updateScrollHeight); // Update on window resize
        window.scrollTo({
                  top: 0, // Adjust this value to position the scroll appropriately
                  behavior: 'smooth'
              });
      });
  
      onUnmounted(() => {
        window.removeEventListener('resize', updateScrollHeight); // Clean up the event listener
      });
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
        isLoggedIn,
        isPageLoading,
        formattedCalendarValue,
        currentQuery,
        currentPitch,
        onMonthChange,
        fetchPitches,
        fetchMyPlayers,
        getYesterdayDate,
        expandedRow,
        setExpandedRow,
        setCollapsedRow,
        dynamicScrollHeight,
        updateScrollHeight,
        trackPlayer,
        loadingPlayers,
        };
    },
    mounted() {
      this.fetchMyPlayers();
      
  
    },
    
    applyFilter() {
      const playerId = selectedPlayer.value.id; // Assuming selectedPlayer is reactive and holds the current player
      const date = formattedCalendarValue.value; // Assuming this holds the formatted date
      fetchPitches(playerId, date);
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
    padding: 5px;
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
  .loading-spinner {
    display: inline-block;
    vertical-align: middle;
    margin-left: 5px;
  }
  </style>
  