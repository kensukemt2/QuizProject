import { createApp } from 'vue'
import App from './App.vue'
import store from './store'
import router from './router'
import Toast from 'vue-toastification'
import 'vue-toastification/dist/index.css'

const app = createApp(App)

// トースト設定
const toastOptions = {
  position: 'top-right',
  timeout: 3000,
  closeOnClick: true,
  pauseOnHover: true
}

app.use(store)
app.use(router)
app.use(Toast, toastOptions)
app.mount('#app')