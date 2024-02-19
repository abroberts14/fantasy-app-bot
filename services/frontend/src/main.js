import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap';

import { createApp } from 'vue'
import axios from 'axios'

import App from './App.vue'
import router from './router'
import useUsersStore from '@/store/users'; 
import { createPinia } from 'pinia'
import createPersistedState from 'pinia-plugin-persistedstate'
import Toast from "vue-toastification";
import "vue-toastification/dist/index.css";
import './styles.css'; // Move this line after the default styles
import PrimeVue from 'primevue/config';
import 'primevue/resources/themes/saga-blue/theme.css';
import 'primevue/resources/primevue.min.css';
import 'primeflex/primeflex.scss';

import 'primeicons/primeicons.css';

import { useToast } from 'vue-toastification'


const app = createApp(App)

app.use(Toast, {
  position: "top-right",
  timeout: 3000,
  closeOnClick: true,
  pauseOnFocusLoss: true,
  pauseOnHover: true,
  draggable: true,
  draggablePercent: 0.6,
  showCloseButtonOnHover: false,
  hideProgressBar: false,
  closeButton: "button",
  icon: true,
  rtl: false,
  maxToasts: 20,
  transition: "Vue-Toastification__fade",
  newestOnTop: false,
  toastClassName: 'custom-toast', //styles.css but this is not working

  filterBeforeCreate: (toast, toasts) => { // gpt ty, determines if the toast should be created. 
    // If the toast is already displayed, don't create it otherwise create it
    if (toasts.filter(
      t => t.content === toast.content
    ).length !== 0) {
      return false;
    }
    return toast;
  }
})

const pinia = createPinia();
pinia.use(createPersistedState)

app.use(pinia);

app.use(PrimeVue);




axios.defaults.withCredentials = true

const backendURL = import.meta.env.VITE_APP_BACKEND_URL || 'http://localhost:5000'
const frontendURL = import.meta.env.VITE_APP_FRONTEND_URL || 'http://localhost:5173'

axios.defaults.baseURL = backendURL
// axios.defaults.headers.common['Access-Control-Allow-Origin'] = frontendURL
console.log('backendURL', backendURL)
console.log('frontendURL', frontendURL)



const toast = useToast()


// error handling
axios.interceptors.response.use(
  response => response, // simply return the response if it's successful, no error handinling
  error => {
    // handle the error
    let errorMessage = 'A system error has occurred. Please try again later.';

    // Check if the error format matches FastAPI's validation errors
    if (error.response?.status === 422 && error.response?.data?.detail) {
      // Extract error messages and concatenate them
      const errors = error.response.data.detail.map(err => {
        const field = err.loc[err.loc.length - 1]; // get the last item from the location array
        return `${field.charAt(0).toUpperCase() + field.slice(1)}: ${err.msg}`;
      });
      errorMessage = errors.join('. '); // Concatenate all error messages with a period and space
    }

    if ((error.response?.status === 400 || error.response?.status == 500) && error.response?.data?.detail) {
      errorMessage = error.response.data.detail;
    }
    if (error.response?.status === 403) {
      errorMessage = "You are not authorized to perform this action."
    }

    toast.error(errorMessage);
    // Special handling for 401 errors
    if (error.response?.status === 401 && !error.config._retry) {
      error.config._retry = true;
      const usersStore = useUsersStore(); 
      usersStore.logout(null); 
      router.push('/login');
    }

    // reject the promise so the error is passed back to the caller (they can then handle if wanted/needed)
    return Promise.reject({ ...error, formattedMessage: errorMessage });
  }
);

app.use(router)

//app.use(createPinia())
app.mount("#app");


