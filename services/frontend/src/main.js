import 'bootstrap/dist/css/bootstrap.css'
import { createApp } from 'vue'
import axios from 'axios'

import App from './App.vue'
import router from './router'
import store from './store'

const app = createApp(App)

axios.defaults.withCredentials = true
//backend temp : http://example-lb-1192907999.us-east-1.elb.amazonaws.com/
// remove the env file to use local
//TODO : make this automatic based on the env
const backendURL = import.meta.env.VITE_APP_BACKEND_URL || 'http://localhost:5000'
const frontendURL = import.meta.env.VITE_APP_FRONTEND_URL || 'http://localhost:5173'

axios.defaults.baseURL = backendURL
axios.defaults.headers.common['Access-Control-Allow-Origin'] = frontendURL
console.log('backendURL', backendURL)
console.log('frontendURL', frontendURL)
axios.interceptors.response.use(undefined, function (error) {
  if (error) {
    const originalRequest = error.config
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      console.log('error 401')
      store.dispatch('logOut')
      return router.push('/login')
    }
  }
})


app.use(router)
app.use(store)
app.mount("#app");