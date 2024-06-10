

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
              <Chart :type="'bar'" :data="createChartData(slotProps.data)" />
  
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
  
  export default defineComponent({
    name: 'TeamPercentilesView',
    components: {
      MediaPlayer,
      LoadingSpinner
    },
    setup() {
      const usersStore = useUsersStore();
      const selectedPlayer = ref({ name: '', id: 0 });
      const players = ref([]);
      const loadingPlayers = ref(false);
      const batters = ref([]);
      const user = computed(() => usersStore.user);
      const isLoggedIn = computed(() => usersStore.isAuthenticated);
      const expandedRow = ref([])
  
      const dynamicScrollHeight = ref('900px'); // Default value
      const debugConsole = true;
      function updateScrollHeight() {
        const width = window.innerWidth;
        const height = window.innerHeight;
  
      }
      
      function createChartData(player) {
        console.log('chart player stats', player.stats);
        return {
          labels: ['Fastball', 'Slider', 'Curveball', 'Changeup'],
          datasets: [
            {
              label: 'wOBA against Pitch Type',
              backgroundColor: ['#42A5F5', '#66BB6A', '#FFA726', '#EF5350'],
              data: [player.stats.wFB, player.wSL, player.wCB, player.wCH]
            }
          ]
        };
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
  
          fetchStatsAllPlayers()
        }
      }
  
  
      function setExpandedRow($event) {
        console.log('rowData', $event.data);
       
        if (typeof expandedRow.value !== 'object' || expandedRow.value === null) {
          console.log('expandedRow.value is not an object');
          expandedRow.value = {};
        }
        nextTick(() => {
          const progressPanel = document.querySelector('.p-datatable-row-expansion');
          
          if (progressPanel) {
            const topPos = progressPanel.offsetTop;
            console.log('topPos', topPos);
            window.scrollTo({
                top: topPos - 100, // Adjust this value to position the scroll appropriately
                behavior: 'smooth'
            });
          } else {
            console.error('progressPanel player element not found');
          }
        });
        Object.keys(expandedRow.value).forEach(key => {
          if (key !== $event.data.key_mlbam) {
            delete expandedRow.value[key];
          }
        });
        
        const playerKey = $event.data.key_mlbam;
       
        expandedRow.value[playerKey] = true;
  
      }
      function setCollapsedRow($event) {
        console.log('rowData collapse', $event.data);
        expandedRow.value = {};
        console.log('collapsed POST', expandedRow.value);
  
      }
      function getGradientColor(value) {
        const red = Math.round((255 * value) / 100);
        const blue = 255 - red;
        return `rgb(${red}, 0, ${blue})`;
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
        batters,
        isLoggedIn,
        fetchMyPlayers,
        expandedRow,
        setExpandedRow,
        setCollapsedRow,
        dynamicScrollHeight,
        updateScrollHeight,
        getGradientColor,
        loadingPlayers,
        createChartData
        };
    },
    mounted() {
      this.fetchMyPlayers();
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
  