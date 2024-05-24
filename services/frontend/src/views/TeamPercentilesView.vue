

<template>
  
  <ModalOverlay :isVisible="isDialogVisible" @update:isVisible="handleModalVisibilityChange">
      <h3>No Yahoo Account Detected</h3>
      <p>
        To search for your players most recent plate appearances, you must connect and authorize a Yahoo account.
      </p>
      <p>
        Visit your <router-link to="/profile">profile</router-link> for Yahoo integration setup.
      </p>
  </ModalOverlay> 
  <LoadingSpinner v-if="loadingPlayers"/>
  <section class="video-section">
    <Message severity="info" :sticky="false" :life="5000">Resync your players on your <router-link to="/profile">profile</router-link> page</Message>

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
            <PercentileBars :percentiles="slotProps.data.percentiles" />

          </div>
      </template>
    </DataTable>
    <div v-if="batters.length === 0">
      <p>No players loaded.</p>
      <Button @click="syncMyPlayers">Sync My Players From Yahoo</Button>
    </div>
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
import PercentileBars from '@/components/PercentileBars.vue';

export default defineComponent({
  name: 'TeamPercentilesView',
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
    const userTokenPresent = ref(null);
    const user = computed(() => usersStore.user);
    const isLoggedIn = computed(() => usersStore.isAuthenticated);
    const expandedRow = ref([])
    const isDialogVisible = ref(false);
    const handleModalVisibilityChange = (newValue) => {
      isDialogVisible.value = newValue;
      if (!newValue) { // if newValue is false, indicating the modal is closed
        router.push('/profile'); // navigate to /profile
      }
    };
    const dynamicScrollHeight = ref('900px'); // Default value
    const debugConsole = true;
    function updateScrollHeight() {
      const width = window.innerWidth;
    }


    async function syncMyPlayers() {
      const usersStore = useUsersStore();
      if (!usersStore.isAuthenticated) {
        console.error('User is not logged in or token is not available');
        return;
      }
      try {
        const response = await axios.get('/baseball/players/sync_players');
        console.log('API Response:', response.data);
        if (response.data.players.batters) {
          batters.value = response.data.players.batters;
        
        } else {
          console.error('Batters data is not in expected format:', response.data);
        }
      } catch (error) {
        console.error('Failed to fetch players:', error);
        batters.value = []; // Reset batters on error
      } finally {
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
        isDialogVisible.value = !userTokenPresent.value 
        console.log("isDialogVisible: ", isDialogVisible.value);
      }
    }
    
    async function fetchPercentilesAllPlayers() {

      const fetchPromises = batters.value.map(player => {
        player.isLoading = true;  // Set loading to true initially
          return axios.get(`/baseball/get-player-percentiles/${player.key_mlbam}`)
              .then(response => {
                  if (response.data) {
                    player.percentiles = response.data
                  player.isLoading = false;  // Loading done
                
                  return { player, status: 'fulfilled' };
                  }
              })
              .catch(error => {
                  console.error(`Error fetching valid percenitles for player ${player.key_mlbam}:`, error);
                  player.percentiles = {};
                  return { player, status: 'rejected', reason: error };
              });
      });


      const results = await Promise.allSettled(fetchPromises);

      results.forEach(result => {
          if (result.status === 'fulfilled') {
            console.log('Data fetched successfully for player', result.value.player.key_mlbam);
          } else {
              console.error(`Failed to fetch data for player ${result.reason.player.key_mlbam}:`, result.reason);
          }
      });


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
        this.fetchPercentilesAllPlayers()
        loadingPlayers.value = false;
      }
    }


    function setExpandedRow($event) {
      console.log('rowData', $event.data);
      
      if (typeof expandedRow.value !== 'object' || expandedRow.value === null) {
        console.log('expandedRow.value is not an object');
        expandedRow.value = {};
      }
     
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
      userTokenPresent,
      isLoggedIn,
      fetchMyPlayers,
      fetchUserTokens,
      syncMyPlayers, 
      expandedRow,
      setExpandedRow,
      setCollapsedRow,
      dynamicScrollHeight,
      updateScrollHeight,
      isDialogVisible,
      handleModalVisibilityChange,
      loadingPlayers,
      fetchPercentilesAllPlayers,
      getGradientColor,
      };
  },
  mounted() {
    this.fetchUserTokens();
    if (!this.isDialogVisible.value) {
      this.fetchMyPlayers();
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
.loading-spinner {
  display: inline-block;
  vertical-align: middle;
  margin-left: 5px;
}
</style>