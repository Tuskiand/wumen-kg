import { createApp } from 'vue';
import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';
import App from './App.vue';
import router from './router';
import './styles.css';
import './styles/tcm-theme.css';
import './styles/element-plus-tcm.css';

createApp(App).use(router).use(ElementPlus).mount('#app');
