<template>

       <LoadingSpinner v-if="isLoading" />

            <div class="flex flex-column  justify-center  h-12rem">
              <div class="mb-3 ">
                <label for="bot_name" >Bot Name:</label>
                <InputText  class="flex lg:w-25rem md:w-20rem sm:w-18rem   w-18rem"  type="text" id="bot_name" v-model="bot.name"  :disabled="!oauthTokens || oauthTokens.length == 0"   />
              </div>
              <div class="mb-3">
                <label for="league_id"  >Yahoo League ID:</label>
                <InputText   class="flex lg:w-25rem md:w-20rem sm:w-18rem   w-18rem"  type="text" id="league_id" v-model="bot.league_id"  :disabled="!oauthTokens || oauthTokens.length == 0"   />
                
              </div>
              
            </div>

            <div class="flex flex-column h-16rem">
              <div class="mb-3 d-flex align-items-center">
                <label for="personal" class="   mr-2">Personal:</label>
                <Checkbox id="personal" v-model="personalRef" :binary="true" @change="filterFeatures"/>
              </div>
              <div class="mb-3 ">
                  <label for="timezone" class="   ">Timezone:</label>
                  <Dropdown v-model="selectedTimezone" :options="timezones"   optionLabel="label" placeholder="Select a timezone"   class="flex lg:w-25rem md:w-20rem sm:w-18rem   w-18rem"/>
                </div>
              <div class="mb-3">
                <label for="chat_type"  >Message Platform:</label>
                <Dropdown v-model="selectedPlatform" :options="platforms"  optionLabel="Platform" placeholder="Select a message platform"  :highlightOnSelect="true"       @change="onPlatformChange"  class="flex lg:w-25rem md:w-20rem w-18rem 	" />
              </div>
           
              <div class="mb-3">
                <div v-if="selectedPlatform.Platform === 'GroupMe'" >
                  <label for="groupme_bot_id"  >GroupMe Bot ID:</label>
                  <InputText class="flex lg:w-25rem md:w-20rem sm:w-18rem   w-18rem" type="text" id="groupme_bot_id" v-model="bot.groupme_bot_id"  :disabled="!oauthTokens || oauthTokens.length == 0"   />
                </div>
                <div v-else-if="selectedPlatform.Platform === 'Discord'" >
                  <label for="discord_webhook_url"  >Discord Webhook URL:</label>
                  <InputText  class="flex lg:w-25rem md:w-20rem sm:w-18rem   w-18rem"  type="text" id="discord_webhook_url" v-model="bot.discord_webhook_url"  :disabled="!oauthTokens || oauthTokens.length == 0"   />
                </div>
              </div>
          </div>

            
      <div class="flex flex-column">
          <DataTable :value="filteredFeatures" stripedRows>
            <Column header="Name">
              <template #body="slotProps">
                <div>{{ formatFeatureName(slotProps.data.name) }}</div>
              </template>
            </Column>
              <Column field="description" header="Description" />
              <Column header="When">
                  <template #body="slotProps">
                      <div v-if="slotProps.data.live">
                          Every 10 minutes (live)
                      </div>
                      <div v-else>
                        <span v-if="slotProps.data.day === 'all'">
                          Daily
                        </span>
                        <span v-else>
                          {{ formatDays(slotProps.data.day) }}
                        </span>
                        - {{ formatTime(slotProps.data.hour, slotProps.data.minute) }} {{ selectedTimezone.label }}
                      </div>
                  </template>
              </Column>
              <Column header="Enabled">
                  <template #body="slotProps">
                      <input type="checkbox" v-model="slotProps.data.enabled" />
                  </template>
              </Column>
          </DataTable>

          <div class="flex justify-content-start py-4 gap-2">
              <button type="submit" class="btn btn-primary"  :disabled="!oauthTokens || oauthTokens.length == 0" @click="submit">Submit</button>
          </div>
      </div>
   

</template>

<script>
import { defineComponent, ref, onMounted, computed } from 'vue';
import { utcToZonedTime, zonedTimeToUtc } from 'date-fns-tz';
import { format as fnsFormat } from 'date-fns';
import useBotsStore from '@/store/bots';
import useUsersStore from '@/store/users';

import { useToast } from 'vue-toastification';
import LoadingSpinner from '@/components/LoadingSpinner.vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import useFormatting from '@/composables/useFormatting'; 
import  ModalOverlay from '@/components/ModalOverlay.vue';
export default defineComponent({
  name: 'RegisterBotComponent',

  components: { LoadingSpinner, ModalOverlay },

  setup() {
    const bot = ref({
      name: '',
      league_id: '',
      groupme_bot_id: '',
    });
    const personalRef = ref(false);
    const oauthTokens = ref(null);
    const selectedPlatform = ref({Platform: ''});
    const platforms = ref([
      { Platform: 'GroupMe' },
      { Platform: 'Discord' }
    ]);
    const selectedTimezone = ref('America/New_York'); // Default timezone
    const timezones = ref([
      { label: 'Eastern', value: 'America/New_York' },
      { label: 'Central', value: 'America/Chicago' },
      { label: 'Mountain', value: 'America/Denver' },
      { label: 'Pacific', value: 'America/Los_Angeles' },
      // Add other US timezones as needed
    ]);


    const items = ref([
        {
            label: 'Bot Information'
        },
        {
            label: 'Bot Features'
        },
        {
            label: 'Review'
        }
    ]);
    const isDialogVisible = ref(false);

    const isLoading = ref(false);
    const features = ref([]);
    const toast = useToast();
    const active = ref(0);
    const router = useRouter();
    const { formatFeatureName } = useFormatting(); // Use the composable
    const usersStore = useUsersStore(); 
    const user = computed(() => usersStore.stateUser); 

    const formatDays = (days) => {
      if (days.includes(',')) {
        return days.split(',')
                   .map(day => day.charAt(0).toUpperCase() + day.slice(1).toLowerCase())
                   .join(', ');
      }
      return days.charAt(0).toUpperCase() + days.slice(1);
    };
    const formatTime = (hour, minute) => {
      if (!hour || !minute) {
        return '';
      }

      const timezone = selectedTimezone.value.value;
      const default_date = new Date().setHours(hour, minute, 0, 0);
      if (hour == 18) {
        console.log("selectedTimezone: ", selectedTimezone.value.value);
      }

      return fnsFormat(utcToZonedTime(default_date, timezone), 'h:mm a');
    };
    const filteredFeatures = computed(() => {
      console.log("personalRef: ", personalRef.value);
      console.log("features: ", features.value);
      if (personalRef.value) {
        return features.value.filter(feature => feature.private_feature);
      } else {
        return features.value.filter(feature => !feature.private_feature);
      }
    });
        // Method to call when the checkbox is clicked
    const filterFeatures = () => {
      // No need to do anything here as the computed property handles the filtering
    };
    function onPlatformChange(event) {
      console.log("Selected platform:", selectedPlatform.value);
      selectedPlatform.value = event.value;  
      // Additional logic for the selected platform change
    }   
    async function fetchUserTokens() {
      try {
        isLoading.value = true;

        const response = await axios.get(`/oauth/yahoo/tokens`, {
          params: {
            user_id: user.value.id
          }
        });        
        oauthTokens.value = response.data;
      } catch (error) {
        console.error('Failed to fetch Yahoo integration:', error);
      }
      finally {
        isLoading.value = false;
        isDialogVisible.value = !oauthTokens.value || oauthTokens.value.length === 0;
        console.log("isDialogVisible: ", isDialogVisible.value);
      }
    }
    const handleModalVisibilityChange = (newValue) => {
      console.log("eventvalue: ", newValue);
      isDialogVisible.value = newValue;
      if (!newValue) { // if newValue is false, indicating the modal is closed
        router.push('/profile'); // navigate to /profile
      }
    }
    const fetchFeatures = async () => {
      console.log('Fetching features');
      try {
        const response = await axios.get('/global-features');
        const updatedFeatures = response.data.map(feature => ({
          ...feature,
          enabled: false // Initialize an 'enabled' property for the checkbox
        }));

        features.value = updatedFeatures;
      } catch (error) {
        console.error('Error fetching features:', error);
        toast.error('Error fetching features');
      }
    };
   
    onMounted(() => {
        fetchFeatures();
        fetchUserTokens();
        });
    const submit = async () => {
      const errorMessages = [];
      const namePattern = /^[A-Za-z0-9]+$/; // Regex for letters and digits
      let redirect_page = 0
          // Check if at least one feature is enabled
      const isAnyFeatureEnabled = features.value.some(feature => feature.enabled);
      if (!isAnyFeatureEnabled) {
          errorMessages.push('At least one feature must be enabled');
          redirect_page = 1
      }

      if (!bot.value.name) {
        errorMessages.push('Bot Name cannot be empty');
      } else if (!namePattern.test(bot.value.name)) {
        errorMessages.push('Bot Name should contain only letters and numbers, no spaces or special characters');
        redirect_page = 0
      }
      if (bot.value.name.length > 20) {
        errorMessages.push('Bot Name must be 20 characters or less');
        redirect_page = 0
      }
      if (!bot.value.league_id) {
        errorMessages.push('Yahoo League ID cannot be empty');
        redirect_page = 0
      }

      if ((!bot.value.groupme_bot_id) && (!bot.value.discord_webhook_url)) {
        errorMessages.push('GroupMe ID or Discord Webhook must be given');
        redirect_page = 0
      }


      if (errorMessages.length > 0) {
        errorMessages.forEach(message => toast.error(message));
        active.value = redirect_page; // Set active panel to the first one if there are errors

        return;
      }

      try {
        isLoading.value = true;

        console.log("Original features:", features.value);

        const botData = {
            ...bot.value,
            features: features.value.map(feature => ({
                global_feature_id: feature.id,
                enabled: feature.enabled
            })),
            timezone: selectedTimezone.value.value,
            private: personalRef.value,
        };

        console.log("Mapped features for botData:", botData.features);
        console.log("Bot data:", botData);
        const botsStore = useBotsStore();
        const response = await botsStore.createBot(botData);

        toast.success('Bot created successfully');
        router.push(`/bot/${response.id}`); // Navigate to the specific bot's page
        
      } catch (error) {
        console.error('Error creating bot', error);
        toast.error('Error creating bot: ' + error);
      } finally {
        isLoading.value = false;
      }
    };


   
    return {
      bot,
      isLoading,
      features,
      submit,
      active,
      formatFeatureName,
      oauthTokens,
      handleModalVisibilityChange,
      isDialogVisible,
      selectedPlatform,
      platforms,
      onPlatformChange,
      timezones,
      selectedTimezone,
      formatTime,
      formatDays,
      personalRef,
      filteredFeatures,
      filterFeatures
      
    };
  },
});
</script>
