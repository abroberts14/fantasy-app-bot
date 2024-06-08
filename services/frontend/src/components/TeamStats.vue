<template>
  <LoadingSpinner v-if="loadingPlayers"/>
  <section class="video-section">
    <div>
      <TabView>
        <TabPanel header="Basic Stats">
          <DataTable v-if="filteredDataBasic.length > 0" :value="filteredDataBasic" class="compact-table" stripedRows scrollable  >
            <span v-if="filteredDataBasic.isLoading" class="loading-spinner">
              <ProgressSpinner style="width: 20px; height: 20px" strokeWidth="8" fill="var(--surface-ground)" animationDuration=".5s" aria-label="Loading data" />
            </span>
            <Column field="name" header="Name"  class="compact-column" frozen />
            <Column class="compact-column" frozen >
              <template #body="slotProps">
                <img  :src="`https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_213,q_auto:best/v1/people/${slotProps.data.key_mlbam}/headshot/67/current`" :alt="slotProps.data.image" class="img-headshot" />
              </template>
            </Column>
            <Column v-for="field in fields.basic" :key="field.key" :field="'stats.' + field.key" :header="field.label"  class="compact-column" />
          </DataTable>
        </TabPanel>
        <TabPanel header="Advanced Stats">
          <DataTable v-if="filteredDataCustom.length > 0" :value="filteredDataCustom" class="compact-table" stripedRows  scrollable  >
            <span v-if="filteredDataCustom.isLoading" class="loading-spinner">
              <ProgressSpinner style="width: 20px; height: 20px" strokeWidth="8" fill="var(--surface-ground)" animationDuration=".5s" aria-label="Loading data" />
            </span>

            <Column field="name" header="Name"  class="compact-column" frozen />
            <Column class="compact-column" frozen >
              <template #body="slotProps">
                <img  :src="`https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_213,q_auto:best/v1/people/${slotProps.data.key_mlbam}/headshot/67/current`" :alt="slotProps.data.image" class="img-headshot" />
              </template>
            </Column>
            <!-- <Column frozen >
              <template #body="slotProps">



                  <img :src="`https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_213,q_auto:best/v1/people/${slotProps.data.key_mlbam}/headshot/67/current`" :alt="slotProps.data.image" class="img-headshot" />
              </template>
            </Column> -->
            <Column v-for="field in fields.custom" :key="field.key" :field="'stats.' + field.key" :header="field.label"  class="compact-column" />
          </DataTable>
        </TabPanel>
      </TabView>
    </div>
  </section>
</template>

<script>
import { defineComponent, ref, computed, onMounted, onUnmounted, watch } from 'vue';
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
    const expandedRow = ref([]);
    const activeStatTab = ref('Basic Stats');
    const dynamicScrollHeight = ref('900px'); // Default value
    const selectedStatGroup = ref(null);

    const fields = ref({
      basic: [
        { key: 'G', label: 'G' },
        { key: 'AB', label: 'AB' },
        { key: 'PA', label: 'PA' },
        { key: 'H', label: 'H' },
        { key: 'HR', label: 'HR' },
        { key: 'R', label: 'R' },
        { key: 'RBI', label: 'RBI' },
        { key: 'AVG', label: 'AVG' },
        { key: 'OBP', label: 'OBP' },
        { key: 'SLG', label: 'SLG' },
        { key: 'OPS', label: 'OPS' },
      ],
      custom: [
        { key: 'BABIP', label: 'BABIP' },
        { key: 'BB%', label: 'BB%' },
        { key: 'K%', label: 'K%' },
        { key: 'SwStr%', label: 'SwStr%' },
        { key: 'wOBA', label: 'wOBA' },
        { key: 'ISO', label: 'ISO' },
        { key: 'HR/FB', label: 'HR/FB' },
        { key: 'FB%', label: 'FB%' },
        { key: 'GB%', label: 'GB%' },
        { key: 'LD%', label: 'LD%' },
        { key: 'Soft%', label: 'Soft%' },
        { key: 'Med%', label: 'Med%' },
        { key: 'Hard%', label: 'Hard%' },
        { key: 'Barrels', label: 'Barrels' },
        { key: 'Barrel%', label: 'Barrel%' },
        { key: 'maxEV', label: 'maxEV' },
        { key: 'HardHit%', label: 'HardHit%' },
        { key: 'xBA', label: 'xBA' },
        { key: 'xSLG', label: 'xSLG' },
        { key: 'xwOBA', label: 'xwOBA' },
        { key: 'wRC+', label: 'wRC+' },
        { key: 'O-Swing%', label: 'O-Swing%' },
        { key: 'Z-Swing%', label: 'Z-Swing%' },
        { key: 'O-Contact%', label: 'O-Contact%' },
        { key: 'Z-Contact%', label: 'Z-Contact%' },
        { key: 'CSW%', label: 'CSW%' }
      ]
    });

    const filteredData = ref([]);

    const filteredDataBasic = computed(() => {
      return batters.value.map(player => ({
        ...player,
        stats: Object.fromEntries(
          Object.entries(player.stats || {}).filter(([key]) => fields.value.basic.some(field => field.key === key))
            .map(([key, value]) => {
              if (key.includes('%')) {
                // Assuming the value is a decimal that needs to be converted to a percentage
                value = `${(value * 100).toFixed(1)}%`;
              }
              return [key, value];
            })
        )
      }));
    });

  const filteredDataCustom = computed(() => {
    return batters.value.map(player => ({
      ...player,
      stats: Object.fromEntries(
        Object.entries(player.stats || {}).filter(([key]) => fields.value.custom.some(field => field.key === key))
          .map(([key, value]) => {
            if (key.includes('%')) {
              // Assuming the value is a decimal that needs to be converted to a percentage
              value = `${(value * 100).toFixed(1)}%`;
            }
            return [key, value];
          })
      )
    }));
  });

    watch(activeStatTab, () => {
      if (activeStatTab.value === 'Basic Stats') {
        filteredData.value = filteredDataBasic.value;
      } else if (activeStatTab.value === 'Custom Stats') {
        filteredData.value = filteredDataCustom.value;
      }
    }, { immediate: true });

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
        fetchStatsAllPlayers();
      }
    }

    function updateScrollHeight() {
      const width = window.innerWidth;
      const height = window.innerHeight;
      // Adjust dynamicScrollHeight based on window dimensions if necessary
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
      selectedStatGroup,
      activeStatTab,
      filteredData,
      filteredDataBasic,
      filteredDataCustom
    };
  }
});
</script>
   

  
  <style scoped>
  .name-image-container {
    display: flex;
    align-items: center;
    white-space: nowrap;
  }
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
  


