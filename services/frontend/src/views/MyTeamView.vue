<template>
  <div class="card">
    <TabView lazy>
      <TabPanel header="Stat Percentiles">
        <TeamPercentiles  />
      </TabPanel>
      <TabPanel header="Recent Video Replays">
        <TeamVideos  />
      </TabPanel>
      <TabPanel header="Statistics" ">
        <TeamStats  />
      </TabPanel>
    </TabView>
  </div>
</template>

<script>
import { ref } from 'vue';
import TeamPercentiles from '@/components/TeamPercentiles.vue';
import TeamVideos from '@/components/TeamVideos.vue';
import TeamStats from '@/components/TeamStats.vue';

export default {
  name: 'MyTeam',
  components: {
    TeamPercentiles,
    TeamVideos,
    TeamStats
  },
  setup() {
    const activeTab = ref('percentiles'); // Default active tab

    // Function to change tab
    function changeTab(tab) {
      console.log("Change tab", tab);
      activeTab.value = tab;
    }

    return {
      activeTab,
      changeTab
    };
  }
}
</script>