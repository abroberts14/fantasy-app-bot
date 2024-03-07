


import { createApp } from 'vue'
import axios from 'axios'

import App from './App.vue'
import router from './router'
import useUsersStore from '@/store/users'; 
import { createPinia } from 'pinia'
import createPersistedState from 'pinia-plugin-persistedstate'
import Toast from "vue-toastification";
import PrimeVue from 'primevue/config';

import '@/assets/styles.scss';
import 'bootstrap';
import { useToast } from 'vue-toastification'

import Button from 'primevue/button';
import Card from 'primevue/card';
import Chip from 'primevue/chip';
import Dialog from 'primevue/dialog';
import SplitButton from 'primevue/splitbutton';
import ProgressSpinner from 'primevue/progressspinner';
import ConfirmDialog from 'primevue/confirmdialog';
import ConfirmationService from 'primevue/confirmationservice';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Stepper from 'primevue/stepper';
import StepperPanel from 'primevue/stepperpanel';
import TreeTable from 'primevue/treetable';
import InputText from 'primevue/inputtext';
const app = createApp(App)
app.use(PrimeVue, { ripple: true });
app.use(ConfirmationService);
app.component('Button', Button);
app.component('Chip', Chip);
app.component('Dialog', Dialog);
app.component('SplitButton', SplitButton);
app.component('ProgressSpinner', ProgressSpinner);
app.component('ConfirmDialog', ConfirmDialog);
app.component('DataTable', DataTable);
app.component('Column', Column);
app.component('Stepper', Stepper);
app.component('StepperPanel', StepperPanel);
app.component('TreeTable', TreeTable);
app.component('InputText', InputText);
app.component('Card', Card);
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
  newestOnTop: true,
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

    if ((error.response?.status === 400 || error.response?.status == 500 || error.response?.status == 404 ) && error.response?.data?.detail) {
      errorMessage = error.response.data.detail;
    }
    if (error.response?.status === 403) {
      errorMessage = "You are not authorized to perform this action."
    }

    // Special handling for 401 errors
    if (error.response?.status === 401 && !error.config._retry) {
      error.config._retry = true;
      const usersStore = useUsersStore(); 
      console.log('error.config.url', error.config.url)
      // Check if the error was caused by a request to the login endpoint
      if (error.config.url === 'login') {
        // The 401 error is likely due to invalid login credentials
        errorMessage = error.response.data.detail;
      }  else {
        // The 401 error is likely due to an expired token
        usersStore.logout(null); 
        router.push('/login');
        toast.info("Your login session has expired. Please log in again.");
        return Promise.reject({ ...error, formattedMessage: errorMessage });

      }
    } 
    toast.error(errorMessage);
    
    // reject the promise so the error is passed back to the caller (they can then handle if wanted/needed)
    return Promise.reject({ ...error, formattedMessage: errorMessage });
  }
);

app.use(router)

//app.use(createPinia())
app.mount("#app");


