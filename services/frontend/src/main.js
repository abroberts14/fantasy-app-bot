


import { createApp } from 'vue'
import axios from 'axios'

import App from './App.vue'
import router from './router'
import useUsersStore from '@/store/users'; 
import { createPinia } from 'pinia'
import createPersistedState from 'pinia-plugin-persistedstate'
import Toast from "vue-toastification";
import PrimeVue from 'primevue/config';
import 'primeflex/primeflex.css';
import '@/assets/main.css'
import '@/assets/styles.scss';
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
import Dropdown from 'primevue/dropdown';
import Tooltip from 'primevue/tooltip';
import Checkbox from 'primevue/checkbox';
import AutoComplete from 'primevue/autocomplete';
import Calendar from 'primevue/calendar';
import FloatLabel from 'primevue/floatlabel';
import Menubar from 'primevue/menubar';
import AnimateOnScroll from 'primevue/animateonscroll';
import InlineMessage from 'primevue/inlinemessage';
import Message from 'primevue/message';
import ProgressBar from 'primevue/progressbar';
import TabView from 'primevue/tabview';
import Image from 'primevue/image';
import Chart from 'primevue/chart';
import Skeleton from 'primevue/skeleton';
import Inplace from 'primevue/inplace';
import Popover from 'primevue/popover';
import Aura from '@primevue/themes/aura';
import Steps from 'primevue/steps';


import Tabs from 'primevue/tabs';
import TabList from 'primevue/tablist';
import Tab from 'primevue/tab';
import TabPanels from 'primevue/tabpanels';
import TabPanel from 'primevue/tabpanel';

const app = createApp(App)
app.use(PrimeVue, {
  theme: {
    preset: Aura,
    options: {
      prefix: 'p',
      darkModeSelector: 'light',
      cssLayer: false
    }
  },
  ripple: true
  // pt: {
  //     floatlabel: {
  //         root: {
  //             class: ' text-900'
  //         }
  //     },
  //     stepperpanel: { 
  //       header: {
  //         class: ' text-900 '
        
  //       }
  //     }
  // }
});
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
app.component('Dropdown', Dropdown);
app.component('Checkbox', Checkbox);
app.component('AutoComplete', AutoComplete);
app.component('Calendar', Calendar);
app.component('FloatLabel', FloatLabel);
app.component('Menubar', Menubar);
app.directive('tooltip', Tooltip);
app.directive('animateonscroll', AnimateOnScroll);
app.component('InlineMessage', InlineMessage);
app.component('Message', Message);
app.component('ProgressBar', ProgressBar);
app.component('TabView', TabView);
app.component('TabPanel', TabPanel);
app.component('Image', Image);
app.component('Chart', Chart);
app.component('Skeleton', Skeleton);
app.component('Inplace', Inplace);
app.component('Popover', Popover);
app.component('Tabs', Tabs);
app.component('TabList', TabList);
app.component('Tab', Tab);
app.component('TabPanels', TabPanels);
app.component('Steps', Steps);
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
        router.push('/');
        toast.info("Your login session has expired. Please log in again.");
        return Promise.reject({ ...error, formattedMessage: errorMessage });

      }
    } 
    if ((error.response?.status == 500 ) && error.response?.data?.detail) {
      console.error(errorMessage)
    } else {
      toast.error(errorMessage);
    }
    // reject the promise so the error is passed back to the caller (they can then handle if wanted/needed)
    return Promise.reject({ ...error, formattedMessage: errorMessage });
  }
);

app.use(router)

//app.use(createPinia())
app.mount("#app");


