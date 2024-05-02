<template>
  <LoadingSpinner v-if="isLoading" />
  <ModalOverlay :isVisible="isDialogVisible" @update:isVisible="handleModalVisibilityChange">
  <h3 v-if="modalContent">{{ modalContent.name }}</h3>
  <p>Description: </p><p v-html="modalContent.description"></p>
 

</ModalOverlay>
  <div v-if="bot && (isAdmin || userOwnsBot)">
    <div class="surface-section">
      <div class="font-medium text-3xl text-900 mb-3">{{ bot.name }}</div>
      <div class="text-500 mb-5">Created: {{ bot.created_at }}</div>
      <ul class="list-none p-0 m-0">
        <li class="flex align-items-center py-3 px-2 border-top-1 surface-border flex-wrap">
          <div class="text-500 w-6 md:w-2 font-medium">Name</div>
          <div class="text-900 w-full md:w-8 md:flex-order-0 flex-order-1">{{ bot.name }}</div>
        </li>
        <li class="flex align-items-center py-3 px-2 border-top-1 surface-border flex-wrap">
          <div class="text-500 w-6 md:w-2 font-medium">Personal</div>
          <div class="text-900 w-full md:w-8 md:flex-order-0 flex-order-1">{{ bot.private }}</div>
        </li>

        <li v-if="bot.app" class="flex align-items-center py-3 px-2 border-top-1 surface-border flex-wrap">
          <div class="text-500 w-6 md:w-2 font-medium">Status</div>
          <div class="text-900 w-full md:w-8 md:flex-order-0 flex-order-1">
            
            <Button v-if="bot.app.running" label="Running" severity="success" />
            <Button v-else :label="bot.app.status" severity="info" />
          </div>
        </li>

        <li v-if="bot.app" class="flex align-items-center py-3 px-2 border-top-1 surface-border flex-wrap">
          <div class="text-500 w-6 md:w-2 font-medium">Commands</div>
          <div class="text-900 w-full md:w-8 md:flex-order-0 flex-order-1">
            <Button v-if="bot.app.running" @click="stopBot" label="Stop Bot" severity="info" style="margin-right: 10px;" />

            <Button v-if="bot.app.running" @click="restartBot" label="Restart Bot" severity="info" style="margin-right: 10px;"/>
            <Button v-else label="Start Bot"  @click="startBot" severity="info" />
          </div>
        </li>

        <li v-else class="flex align-items-center py-3 px-2 border-top-1 surface-border flex-wrap">
          <div class="text-500 w-6 md:w-2 font-medium">Commands</div>
          <div class="text-900 w-full md:w-8 md:flex-order-0 flex-order-1">
            <ConfirmDialog></ConfirmDialog>

            <Button :disabled="featuresChanged" label="Initiate Bot" @click="initiateBot" severity="info" />
          </div>
        </li>

        <li class="flex align-items-center py-3 px-2 border-top-1 surface-border flex-wrap">
          <div class="text-500 w-6 md:w-2 font-medium">League ID</div>
          <div class="text-900 w-full md:w-8 md:flex-order-0 flex-order-1">{{bot.league_id}}</div>
        </li>


          <div v-if="bot.groupme_bot_id ">
   
            <li class="flex align-items-center py-3 px-2 border-top-1 surface-border flex-wrap">
              <div class="text-500 w-6 md:w-2 font-medium">GroupMe Bot ID</div>
              <div class="text-900 w-full md:w-8 md:flex-order-0 flex-order-1">{{bot.groupme_bot_id}}</div>
            </li>

          </div>
          <div v-else >
         
            <li class="flex align-items-center py-3 px-2 border-top-1 surface-border flex-wrap">
              <div class="text-500 w-6 md:w-2 font-medium">Discord Webhook</div>
              <div class="text-900 w-full md:w-8 md:flex-order-0 flex-order-1">{{bot.discord_webhook_url}}</div>
            </li>
          </div>
        
        <li class="flex align-items-center py-3 px-2 border-top-1 border-bottom-1 surface-border flex-wrap">


          <DataTable class="data-table-center" :value="bot.features"  selectionMode="single" dataKey="id" 
          :metaKeySelection="false"    @rowSelect="onRowSelect" @rowUnselect="onRowUnselect"   stripedRows>

            <Column header="Name">
              <template #body="slotProps">
                <div>{{ formatFeatureName( slotProps.data.global_feature.name) }}</div>
              </template>
            </Column>
              <Column field="global_feature.description" header="Description"  />
              <Column header="When">
                  <template #body="slotProps">
                      <div v-if="slotProps.data.global_feature.live">
                          Every 10 minutes
                      </div>
                      <div v-else>
                        <span v-if="slotProps.data.global_feature.day === 'all'">
                          Daily
                        </span>
                        <span v-else>
                          {{ formatDays(slotProps.data.global_feature.day) }}
                        </span>
                        - {{ formatTime( slotProps.data.global_feature.hour , slotProps.data.global_feature.minute, bot.timezone) }}  {{timezoneValue}}
                      </div>
                  </template>
              </Column>
              <Column header="Enabled">
                  <template #body="slotProps">
                    <input type="checkbox" :disabled="bot.app && bot.app.running || ((slotProps.data.global_feature.private_feature && !bot.private) || (!slotProps.data.global_feature.private_feature && bot.private))" :checked="slotProps.data.enabled" @change="() => handleCheckboxChange(slotProps.data)" />
                  </template>
                  <!-- @change="handleCheckboxChange(slotProps.data) -->
              </Column>
          </DataTable>
          
        </li>

        <li v-if="isAdmin || userOwnsBot" class="flex align-items-center py-3 px-2 border-top-1 surface-border flex-wrap">
          <div class="text-500 w-6 md:w-2 font-medium">Actions</div>
          <div class="text-900 w-full md:w-8 md:flex-order-0 flex-order-1">
            <Button :disabled="!featuresChanged" @click="updateBot" label="Update Bot" severity="info" style="margin-right: 10px;" />

            <SplitButton v-if="isAdmin" label="Visit" icon="pi pi-cog" :model="adminItems" raised rounded @click="visit" severity="secondary"></SplitButton>

          </div>

        </li>


      </ul>
    </div>

    <p>
      <ConfirmDialog></ConfirmDialog>
      <Button label="Delete" severity="danger" @click="confirmDelete" />
    </p>
  </div>
</template>
<script>
import { defineComponent, onMounted, computed, ref } from 'vue';
import useBotsStore from '@/store/bots'; 
import useUsersStore from '@/store/users'; 
import axios from 'axios';
import LoadingSpinner from '@/components/LoadingSpinner.vue';
import { useRouter } from 'vue-router';
import { useToast } from 'vue-toastification';
import { useConfirm } from "primevue/useconfirm";
import useFormatting from '@/composables/useFormatting'; 
import  ModalOverlay from '@/components/ModalOverlay.vue';
import { utcToZonedTime, zonedTimeToUtc } from 'date-fns-tz';
import { format as fnsFormat } from 'date-fns';

export default defineComponent({
    name: 'BotComponent',
    props: ['id'],
    components: { LoadingSpinner, ModalOverlay },
    
    setup(props) {
      const isLoading = ref(true);
      const isDialogVisible = ref(false);
      const checkedFeatures = ref([]); // This should be bound to your checkbox component
      const modalContent = ref(null); 
      const adminItems = ref([
            {
                label: 'Refresh',
                icon: 'pi pi-refresh'
            },
            {
                label: 'Visit',
                icon: 'pi pi-bookmark'
            },
            {
                separator: true
            },
            {
                label: 'Kill',
                icon: 'pi pi-times'
            }
        ]);
      const timezones = ref([
        { label: 'America/New_York', value: 'Eastern' },
        { label: 'America/Chicago', value: 'Central' },
        { label: 'America/Denver', value: 'Mountain' },
        { label: 'America/Los_Angeles', value: 'Pacific' },
      // Add other US timezones as needed
     ]);

      const fetchData = async () => {
            try {
                await botsStore.viewBot(props.id);
                await usersStore.viewMe();
              
                checkedFeatures.value = bot.value.features.map(f => ({ ...f }));

            } catch (error) {
                console.error('Error fetching data:', error);
                if (error.response && error.response.status === 404) {
                    router.push('/dashboard');
                }
            } finally {
                isLoading.value = false;
            }
        }
        const formatDays = (days) => {
          if (!days ) {
            return 'Daily';
          } else {
            console.log("days: ", days);
            if (days.includes(',')) {
              return days.split(',')
                        .map(day => day.charAt(0).toUpperCase() + day.slice(1).toLowerCase())
                        .join(', ');
            }
            return days.charAt(0).toUpperCase() + days.slice(1);
          }
        
        };
        const formatTime = (hour, minute, tz) => {
          if (!hour || !minute) {
            return '';
          }

          const timezone = tz
          const default_date = new Date().setHours(hour, minute, 0, 0);
          if (hour == 18) {
            console.log("selectedTimezone: ", tz);
          }

          return fnsFormat(utcToZonedTime(default_date, timezone), 'h:mm a');
        };

        onMounted(() => {
          fetchData().catch(error => {
            console.error("Error in onMounted fetchData:", error);
          });
        });
        const timezoneValue = computed(() => {
          if (bot.value) {
            const timezone = timezones.value.find(tz => tz.label === bot.value.timezone);
            return timezone ? timezone.value : 'Unknown';
          }
          return 'Not Set'; // Default text or handling when timezone is not set
        });   
        const botsStore = useBotsStore();
        const usersStore = useUsersStore();
        const router = useRouter();
        const toast = useToast();
        const confirm = useConfirm();


        const { formatFeatureName } = useFormatting(); // Use the composable
      
        
        const confirmDelete = () => {
          confirm.require({
            message: "Are you sure you want to delete this bot?",
            header: "Delete Confirmation",
            icon: "pi pi-exclamation-triangle",
            accept: () => {removeBot()},
            reject: () => {
              console.log("Bot deletion cancelled.");
              this.toast.warn('Whew. That was a close one');
            
            }
          });
        };



        const featuresChanged = computed(() => {
          if (isLoading.value || !bot.value || !bot.value.features) {
                return false; // Return a default value if bot or bot.features is not defined
            }
            return bot.value.features.some((feature, index) => {
                return feature.enabled !== checkedFeatures.value[index].enabled;
            });
        });



        const handleModalVisibilityChange = (newValue) => {

            isDialogVisible.value = newValue;
        }
        const handleCheckboxChange = (feature) => {
            feature.enabled = !feature.enabled;
        };

        





        const onRowSelect = (event) => {
          console.log(event.data.global_feature.description)
          modalContent.value = event.data.global_feature // Set the content
          isDialogVisible.value = true; // Show the modal
        }
        
        
        const onRowUnselect = (event) => {
          console.log(event.data.global_feature.description)
          isDialogVisible.value = false

        }
        

        const bot = computed(() => botsStore.stateBot);
        const user = computed(() => usersStore.stateUser);
        const isAdmin = computed(() => usersStore.isAdmin);
        const userOwnsBot = computed(() => user.value.id === bot.user.id);
       
        async function initiateBot() {
            try {
                isLoading.value = true;
                await axios.post(`/apps/start-app/${props.id}`);
                await fetchData();
            } catch (error) {
                console.error('Error initiating bot:', error);
                toast.error('Error initiating bot: ' + error.message);            
            } finally {
                isLoading.value = false;
                toast.success('Bot initiated successfully');

            }
        }
        const startBot = async () => {
          try {
                console.log('Starting bot...');
                isLoading.value = true;
                await axios.post(`/apps/startup-app/${props.id}`);
                await fetchData();
            } catch (error) {
                console.error('Error starting bot:', error);
                toast.error('Error starting bot: ' + error.message);            
            } finally {
                isLoading.value = false;
                toast.success('Bot starting successfully');

            }
        };

        const stopBot = async () => {
          try {
                console.log('Stopping bot...');
                isLoading.value = true;
                await axios.post(`/apps/stop-app/${props.id}`);
                await fetchData();
            } catch (error) {
                console.error('Error stopping bot:', error);
                toast.error('Error stopping bot: ' + error.message);            
            } finally {
                isLoading.value = false;
                toast.success('Bot stopped successfully');
                router.push(`/bot/${props.id}`);

            }
        };

        const restartBot = async () => {
          try {
                console.log('Restarting bot...');
                isLoading.value = true;
                await axios.post(`/apps/restart-app/${props.id}`);
                await fetchData();
            } catch (error) {
                console.error('Error restarting bot:', error);
                toast.error('Error restarting bot: ' + error.message);            
            } finally {
                isLoading.value = false;
                toast.success('Bot restarted successfully');

            }
        };

        async function removeBot() {
            try {
                if (bot.value) {
                    isLoading.value = true;
                    await botsStore.deleteBot(props.id);
                    router.push('/dashboard');
                    toast.success('Bot killed and deleted successfully');
                }
            } catch (error) {
                console.error('Error removing bot:', error);
                if (error.response && error.response.status === 404) {
                    toast.error('The requested bot was not found.');
                    router.push('/dashboard');
                } else {
                  if (error.response) {
                    toast.error('Error removing bot: ' + error.message);
                  }
                }
            } finally {
                isLoading.value = false;
            }
        }
        async function updateBot() {
        try {
          console.log('updating bot...');
          isLoading.value = true;
          const updatedFeatures = bot.value.features.map(feature => ({
              global_feature_id: feature.global_feature.id,
              enabled: feature.enabled
          }));
          console.log("Updated features:", updatedFeatures);


          await axios.patch(`/bot/${props.id}`, updatedFeatures);
          await fetchData();
        } catch (error) {
          console.error('Error updating bot:', error);
          toast.error('Error updating bot: ' + error.message);
        } finally {
          isLoading.value = false;
          toast.success('Bot updated successfully');
          router.push(`/bot/${props.id}`); 
        }
      }
        const visit = () => {
            window.open(`http://167.99.4.120:8000/#/apps/${bot.value.app.name}`, '_blank');
        };

        return { timezoneValue, formatDays, formatTime, bot, user, modalContent, isAdmin, onRowSelect, onRowUnselect, handleModalVisibilityChange, isDialogVisible, isLoading, userOwnsBot, removeBot, adminItems, visit, initiateBot, stopBot, startBot, restartBot, updateBot, confirmDelete, confirm, formatFeatureName, featuresChanged, checkedFeatures, handleCheckboxChange };
    },

  

});
</script>
