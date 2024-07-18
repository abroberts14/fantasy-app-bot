import { ref, computed } from 'vue';
import axios from 'axios';
import useUsersStore from '@/store/users';

export function fetchUserToken() {
  const userTokenPresent = ref(null);
  const usersStore = useUsersStore();
  const user = computed(() => usersStore.user);

  const fetchData = async () => {
    try {
      // Await the axios call to resolve the Promise
      const response = await axios.get(`/oauth/yahoo/tokens`, {
        params: {
          user_id: user.value.id
        }
      });
      // Assuming the response structure, access `.data` after awaiting the call
      userTokenPresent.value = response.data;
    } catch (error) {
      console.error('Failed to fetch Yahoo integration:', error);
      userTokenPresent.value = false; // Explicitly setting false on error
    }
  };

  return {
    userTokenPresent,
    fetchData // Returning fetchData so it can be invoked from the component
  };
}
