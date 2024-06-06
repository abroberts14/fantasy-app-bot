

<template>

    <LoadingSpinner v-if="loadingPlayers"/>
    <section class="video-section">
      <Dropdown :options="statGroups" v-model="selectedStatGroup" optionLabel="label" placeholder="Select Stat Group" @change="filterDataByGroup" />
      <DataTable v-if="filteredData.length > 0" :value="filteredData">
        <span v-if="filteredData.isLoading" class="loading-spinner">
              <ProgressSpinner style="width: 20px; height: 20px" strokeWidth="8" fill="var(--surface-ground)" animationDuration=".5s" aria-label="Loading data" />
        </span>
  
        <Column field="name" header="Name" sortable />
        <Column v-if="!filteredData.isLoading" v-for="key in statKeys" :field="'stats.' + key" :header="key" :key="key" sortable />
      </DataTable>
  
    </section>
  </template>
  
  <script>
  import { defineComponent, ref, computed, onMounted, onUnmounted , nextTick , watch} from 'vue';
  
  import useUsersStore from '@/store/users';
  import MediaPlayer from '@/components/MediaPlayer.vue';
  import LoadingSpinner from '@/components/LoadingSpinner.vue';
  import axios from 'axios';
  import ModalOverlay from '@/components/ModalOverlay.vue';
  import { useRouter } from 'vue-router';
  import PercentileBars from '@/components/PercentileBars.vue';
  
  export default defineComponent({
    name: 'TeamStatsView',
    components: {
      MediaPlayer,
      LoadingSpinner,
      ModalOverlay,
      PercentileBars
    },
    setup() {
      const usersStore = useUsersStore();
      const selectedPlayer = ref({ name: '', id: 0 });
      const players = ref([]);
      const router = useRouter();
      const loadingPlayers = ref(false);
      const batters = ref([]);
      const user = computed(() => usersStore.user);
      const isLoggedIn = computed(() => usersStore.isAuthenticated);
      const expandedRow = ref([])
     
      const dynamicScrollHeight = ref('900px'); // Default value
      const debugConsole = true;
      const selectedStatGroup = ref(null);
      const filteredData = computed(() => {
        if (!selectedStatGroup.value || !batters.value.length) {
          console.log('no selectedStatGroup.value or batters.value.length');
          return [];  
        }
        console.log('selectedStatGroup.value', selectedStatGroup.value.value);
        console.log('fields.length', fields.value.length);
        const statFields = fields.value[selectedStatGroup.value.value];
        console.log('statFields', statFields);
        if (!Array.isArray(statFields)) {
          console.log('statFields is not an array');
          return [];
        }
  
      return batters.value.map(player => {
        console.log('Processing player:', player.name); // Debugging player being processed
        try {
          const filteredStatsEntries = Object.entries(player.stats).filter(([key]) =>
            statFields.some(field => field.key === key)
          );
          console.log(`Filtered stats for ${player.name}:`, filteredStatsEntries); // Debugging filtered stats
  
  
          return {
            ...player,
            stats: Object.fromEntries(filteredStatsEntries)
          };
        } catch (error) {
          
          return player;
        }
      });
    });
      const statKeys = computed(() => {
        const allKeys = new Set();
        try {
          filteredData.value.forEach(player => {
            Object.keys(player.stats).forEach(key => {
              allKeys.add(key);
            });
          });
          console.log("All Stat Keys:", Array.from(allKeys));
          return Array.from(allKeys);
        } catch (error) {
          console.error('Error while computing statKeys:', error);
          return fields.value.basic.map(field => field.key);
        }
      });
      const selectedFields = computed(() => {
        console.log("Recomputing fields for:", selectedStatGroup.value);
  
        return fields.value[selectedStatGroup.value] || [];
      });
      watch(selectedStatGroup, () => {
        console.log('Stat group changed:', selectedStatGroup.value);
      });
      const statGroups = ref([
        { label: 'Basic Stats', value: 'basic' },
        { label: 'Advanced Batting', value: 'advanced' },
        { label: 'Pitching Stats', value: 'pitching' },
        { label: 'Fielding Stats', value: 'fielding' },
        { label: 'Speed', value: 'speed' },
        { label: 'Statcast Metrics', value: 'statcast' },
        { label: 'Value Metrics', value: 'value' }
      ]);
  
      const fields = ref({
        basic: [
          { key: 'name', label: 'Name' },
          { key: 'team', label: 'Team' },
          { key: 'age', label: 'Age' },
          { key: 'G', label: 'Games' },
          { key: 'AB', label: 'AB' },
          { key: 'PA', label: 'PA' },
          { key: 'H', label: 'H' },
          { key: '1B', label: '1B' },
          { key: '2B', label: '2B' },
          { key: '3B', label: '3B' },
          { key: 'HR', label: 'HR' },
          { key: 'R', label: 'R' },
          { key: 'RBI', label: 'RBI' },
          { key: 'BB', label: 'BB' },
          { key: 'IBB', label: 'IBB' },
          { key: 'SO', label: 'SO' },
          { key: 'HBP', label: 'HBP' },
          { key: 'SF', label: 'SF' },
          { key: 'SH', label: 'SH' },
          { key: 'GDP', label: 'GDP' },
          { key: 'SB', label: 'SB' },
          { key: 'CS', label: 'CS' },
          { key: 'AVG', label: 'AVG' },
          { key: 'OBP', label: 'OBP' },
          { key: 'SLG', label: 'SLG' },
          { key: 'OPS', label: 'OPS' },
          { key: 'ISO', label: 'ISO' },
        ],
        advanced: [
          { key: 'BABIP', label: 'BABIP' },
          { key: 'wOBA', label: 'wOBA' },
          { key: 'wRC', label: 'wRC' },
          { key: 'wRAA', label: 'wRAA' },
          { key: 'wRC+', label: 'wRC+' },
          { key: 'RE24', label: 'RE24' },
          { key: 'WPA', label: 'WPA' },
          { key: 'Clutch', label: 'Clutch' },
        ],
        pitching: [
          { key: 'Pitches', label: 'Pitches' },
          { key: 'Balls', label: 'Balls' },
          { key: 'Strikes', label: 'Strikes' },
          { key: 'BU', label: 'Bunts' },
          { key: 'BUH', label: 'BUH' },
          { key: 'IFFB', label: 'IFFB' },
          { key: 'GB', label: 'GB' },
          { key: 'FB', label: 'FB' },
          { key: 'LD', label: 'LD' },
          { key: 'GB/FB', label: 'GB/FB' },
          { key: 'HR/FB', label: 'HR/FB' },
          { key: 'BB%', label: 'BB%' },
          { key: 'K%', label: 'K%' },
          { key: 'BB/K', label: 'BB/K' }
        ],
        fielding: [
          { key: 'Fld', label: 'Fielding Runs Above Average' },
          { key: 'Def', label: 'Defensive Runs Saved' },
          { key: 'Pos', label: 'Positional Adjustment' },
          { key: 'RAR', label: 'Runs Above Replacement' },
          { key: 'WAR', label: 'Wins Above Replacement' }
        ],
        speed: [
          { key: 'SB%', label: 'Stolen Base Percentage' },
          { key: 'Spd', label: 'Speed Score' },
          { key: 'UBR', label: 'Ultimate Base Running' }
        ],
        statcast: [
          { key: 'xSLG', label: 'xSLG' },
          { key: 'xwOBA', label: 'xwOBA' },
          { key: 'EV', label: 'EV' },
          { key: 'LA', label: 'Launch Angle' },
          { key: 'Barrels', label: 'Barrels' },
          { key: 'Barrel%', label: 'Barrel Percentage' },
          { key: 'HardHit', label: 'Hard Hits' },
          { key: 'HardHit%', label: 'Hard Hit Percentage' }
        ],
        value: [
          { key: 'WAR', label: 'Wins Above Replacement' },
          { key: 'Dol', label: 'Dollar Value' },
          { key: 'L-WAR', label: 'League WAR' }
        ]
      });
  
      onMounted(() => {
        fetchMyPlayers();
        
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
      function filterDataByGroup() {
        // This function might adjust filtered data based on additional criteria or trigger re-computation
        console.log('filterDataByGroup', selectedStatGroup.value);
        console.log('fields', fields.value);
        console.log('statGroups', statGroups.value);
        console.log('selectedFields', selectedFields.value);
        console.log('filteredData', filteredData.value);
        console.log('batters', batters.value);
      }
  
      function updateScrollHeight() {
        const width = window.innerWidth;
        const height = window.innerHeight;
  
      }
  
  
  
  
      async function fetchStatsAllPlayers() {
        const playerIds = batters.value.map(player => player.key_mlbam);
        try {
          
          const response = await axios.post('/baseball/get-multiple-player-stats', playerIds);
          const stats = response.data;
          batters.value.forEach(player => {
            if (stats[player.key_mlbam]) {
              player.stats = stats[player.key_mlbam];
              player.isLoading = false; // Loading done
            } else {
              console.error(`No stats found for player ${player.key_mlbam}`);
              player.stats = {};
            }
          });
        } catch (error) {
          console.error('Error fetching stats for players:', error);
          batters.value.forEach(player => {
            player.stats = {}; // Reset stats on error
          });
        } finally {
        }
      }
          
      async function fetchMyPlayers() {
        if (!isLoggedIn) {
          console.error('User is not logged in or token is not available');
          return;
        }
        loadingPlayers.value = true;
        try {
          const response = await axios.get('/baseball/players/my-players');
          batters.value = response.data.players.batters || [];
        } catch (error) {
          console.error('Failed to fetch players:', error);
          batters.value = [];
        } finally {
          loadingPlayers.value = false;
  
          fetchStatsAllPlayers()
          
        }
      }
  
      return {
        selectedPlayer,
        players,
        batters,
        isLoggedIn,
        fetchMyPlayers,
        dynamicScrollHeight,
        updateScrollHeight,
        loadingPlayers,
        fetchStatsAllPlayers,
        fields,
        statGroups,
        selectedStatGroup,
        filterDataByGroup,
        selectedFields,
        filteredData,
        statKeys
        };
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
  .loading-spinner {
    display: inline-block;
    vertical-align: middle;
    margin-left: 5px;
  }
  </style>
  