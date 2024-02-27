<template>
  <!-- <section>
    <LoadingSpinner v-if="isLoading" />
    <form @submit.prevent="submit">
      <div class="mb-3">
        <label for="bot_name" class="form-label">Bot Name:</label>
        <input type="text" id="bot_name" v-model="bot.name" class="form-control" />
      </div>
      <div class="mb-3">
        <label for="league_id" class="form-label">Yahoo League ID:</label>
        <input type="text" id="league_id" v-model="bot.league_id" class="form-control" />
      </div>
      <div class="mb-3">
        <label for="groupme_bot_id" class="form-label">GroupMe Bot ID:</label>
        <input type="text" id="groupme_bot_id" v-model="bot.groupme_bot_id" class="form-control" />
      </div>
      <DataTable :value="features" stripedRows>
      <Column field="name" header="Feature Name" />
      <Column field="description" header="Description" />
      <Column header="Time (00:00 -> 23:59)">
        <template #body="slotProps">
          {{ slotProps.data.hour }}:{{ slotProps.data.minute.toString().padStart(2, '0') }} 
        </template>
      </Column>
      <Column header="Enabled">
        <template #body="slotProps">
          <input type="checkbox" v-model="slotProps.data.enabled" />
        </template>
      </Column>
    </DataTable>

      <button type="submit" class="btn btn-primary">Submit</button>
    </form>
  </section>

 -->
 <LoadingSpinner v-if="isLoading" />

 <Stepper v-model:activeStep="active" orientation="vertical">
    <StepperPanel header="Bot Information">

      <template #content="{ nextCallback }">

            <div class="flex flex-column h-12rem">
              <div class="mb-3">
                <label for="bot_name" class="form-label">Bot Name:</label>
                <input type="text" id="bot_name" v-model="bot.name" class="form-control" />
              </div>
              <div class="mb-3">
                <label for="league_id" class="form-label">Yahoo League ID:</label>
                <input type="text" id="league_id" v-model="bot.league_id" class="form-control" />
              </div>
            </div>
            <div class="mb-3">
              <label for="groupme_bot_id" class="form-label">GroupMe Bot ID:</label>
              <input type="text" id="groupme_bot_id" v-model="bot.groupme_bot_id" class="form-control" />
            </div>
            <div class="flex py-4">
                <Button label="Next"  icon="pi pi-arrow-down" iconPos="right" :disabled="!bot.name || !bot.league_id || !bot.groupme_bot_id" @click="nextCallback" />
            </div>

        </template>
    </StepperPanel>
    <StepperPanel header="Bot Features">
      <template #content="{ prevCallback, nextCallback }">
      <div class="flex flex-column">
          <DataTable :value="features" stripedRows>
            <Column header="Name">
              <template #body="slotProps">
                <div>{{ formatFeatureName(slotProps.data.name) }}</div>
              </template>
            </Column>
              <Column field="description" header="Description" />
              <Column header="When">
                  <template #body="slotProps">
                      <div v-if="slotProps.data.live">
                          Every 30 minutes
                      </div>
                      <div v-else>
                          {{ slotProps.data.day === 'all' ? 'Daily' : slotProps.data.day.charAt(0).toUpperCase() + slotProps.data.day.slice(1) }} - 
                          {{ slotProps.data.hour }}:{{ slotProps.data.minute.toString().padStart(2, '0') }}
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
              <Button label="Back" icon="pi pi-arrow-up" iconPos="right" severity="secondary" @click="prevCallback" />
              <Button label="Next" icon="pi pi-arrow-down" iconPos="right" @click="nextCallback" />
          </div>
      </div>
</template>
    </StepperPanel>
    <StepperPanel header="Payment (not complete)">
        <template #content="{ prevCallback }">
            <div class="flex flex-column  h-12rem">
              <div class="mb-3">
                <label for="card_number" class="form-label">Card Number:</label>
                <input type="text" id="card_number" class="form-control" />
              </div>
              <div class="mb-3">
                <label for="expiry_date" class="form-label">Expiry Date:</label>
                <input type="text" id="expiry_date" class="form-control" />
              </div>
              <div class="mb-3">
                <label for="cvv" class="form-label">CVV:</label>
                <input type="text" id="cvv" class="form-control" />
              </div>
            </div>
            <div class="flex py-8 gap-2">
                <Button label="Back" severity="secondary" icon="pi pi-arrow-up" iconPos="right" @click="prevCallback" />
                <button type="submit" class="btn btn-primary" @click="submit">Submit</button>

            </div>
        </template>
    </StepperPanel>
</Stepper>

</template>

<script>
import { defineComponent, ref, onMounted } from 'vue';
import useBotsStore from '@/store/bots';
import { useToast } from 'vue-toastification';
import LoadingSpinner from '@/components/LoadingSpinner.vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import useFormatting from '@/composables/useFormatting'; 

export default defineComponent({
  name: 'RegisterBotComponent',

  components: { LoadingSpinner, },
  setup() {
    const bot = ref({
      name: '',
      league_id: '',
      groupme_bot_id: '',
    });
    const isLoading = ref(false);
    const features = ref([]);
    const toast = useToast();
    const active = ref(0);
    const router = useRouter();
    const { formatFeatureName } = useFormatting(); // Use the composable

    const fetchFeatures = async () => {
      console.log('Fetching features');
      try {
        const response = await axios.get('/global-features');
        features.value = response.data.map(feature => ({
          ...feature,
        
          enabled: false // Initialize an 'enabled' property for the checkbox
        }));
      } catch (error) {
        console.error('Error fetching features:', error);
        toast.error('Error fetching features');
      }
    };


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

      if (!bot.value.groupme_bot_id) {
        errorMessages.push('GroupMe Bot ID cannot be empty');
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
            }))
        };

        console.log("Mapped features for botData:", botData.features);
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

    onMounted(fetchFeatures);

    onMounted(() => {
        fetchFeatures();
        });
    return {
      bot,
      isLoading,
      features,
      submit,
      active,
      formatFeatureName 
    };
  },
});
</script>
