import Vue from 'vue'
import App from './App'
import router from './router'
import store from './store'
import axios from 'axios'
import BootstrapVue from 'bootstrap-vue'
import '../node_modules/bootstrap/dist/css/bootstrap.css'
import '../node_modules/bootstrap-vue/dist/bootstrap-vue.css'
import '../node_modules/flatpickr/dist/flatpickr.css'

import 'vue-awesome/icons/eye'
import 'vue-awesome/icons/caret-up'
import 'vue-awesome/icons/caret-down'
import 'vue-awesome/icons/arrows'
import 'vue-awesome/icons/trash'
import 'vue-awesome/icons/plus-square'
import 'vue-awesome/icons/hourglass-half'
import 'vue-awesome/icons/check'
import 'vue-awesome/icons/asterisk'
import 'vue-awesome/icons/times'
import 'vue-awesome/icons/exclamation'
import 'vue-awesome/icons/plus'
import 'vue-awesome/icons/list-ul'
import 'vue-awesome/icons/paper-plane'
import 'vue-awesome/icons/paperclip'
import 'vue-awesome/icons/image'
import 'vue-awesome/icons/save'
import 'vue-awesome/icons/upload'
import 'vue-awesome/icons/download'
import 'vue-awesome/icons/arrow-right'
import 'vue-awesome/icons/arrow-left'
import 'vue-awesome/icons/user'
import 'vue-awesome/icons/users'
import 'vue-awesome/icons/shield'
import 'vue-awesome/icons/user-times'
import 'vue-awesome/icons/user-plus'
import 'vue-awesome/icons/edit'
import 'vue-awesome/icons/undo'
import 'vue-awesome/icons/sign-in'
import 'vue-awesome/icons/sign-out'
import 'vue-awesome/icons/ban'
import 'vue-awesome/icons/link'
import 'vue-awesome/icons/envelope'
import 'vue-awesome/icons/flag'
import 'vue-awesome/icons/flag-checkered'
import 'vue-awesome/icons/home'
import 'vue-awesome/icons/calendar'
import 'vue-awesome/icons/key'
import 'vue-awesome/icons/question'
import 'vue-awesome/icons/circle-o-notch'
import 'vue-awesome/icons/sort'
import 'vue-awesome/icons/align-left'
import 'vue-awesome/icons/long-arrow-up'
import 'vue-awesome/icons/long-arrow-down'
import 'vue-awesome/icons/comments'
import 'vue-awesome/icons/cog'
import 'vue-awesome/icons/clock-o'
import 'vue-awesome/icons/print'
import 'vue-awesome/icons/github'
import 'vue-awesome/icons/linkedin'
import 'vue-awesome/icons/file'

import Toasted from 'vue-toasted'
import flatPickr from 'vue-flatpickr-component'

Vue.config.productionTip = false
Vue.use(Toasted, { position: 'top-center', duration: 4000 })
Vue.use(BootstrapVue)
Vue.use(flatPickr)

/* Checks the store for for permissions according to the current route cID or aID. */
Vue.prototype.$hasPermission = store.getters['permissions/hasPermission']

/* Sets the default authorization token needed to for authenticated requests. */
axios.defaults.transformRequest.push((data, headers) => {
    if (store.getters['user/jwtAccess']) {
        headers.Authorization = 'Bearer ' + store.getters['user/jwtAccess']
    }
    return data
})

/* eslint-disable no-new */
new Vue({
    el: '#app',
    router,
    store,
    components: { App },
    data: {
        colors: ['pink-border', 'purple-border', 'yellow-border', 'blue-border'],
        previousPage: null,
        windowWidth: 0,
        maxFileSizeBytes: 2097152,
        maxEmailFileSizeBytes: 10485760,
        flatPickrTimeConfig: {
            enableTime: true,
            time_24hr: true
        }
    },
    mounted () {
        this.$nextTick(function () {
            window.addEventListener('resize', this.getWindowWidth)

            this.getWindowWidth()
        })
    },
    beforeDestroy () {
        window.removeEventListener('resize', this.getWindowWidth)
    },
    methods: {
        getWindowWidth () {
            this.windowWidth = window.innerWidth
        },
        /* Bootstrap breakpoints for custom events. */
        // TODO Figure out how to get these from the dedicated sass file (more webpack fun)
        sm () { return this.windowWidth > 575 },
        md () { return this.windowWidth > 767 },
        lg () { return this.windowWidth > 991 },
        xl () { return this.windowWidth > 1199 },
        xsMax () { return this.windowWidth < 576 },
        smMax () { return this.windowWidth < 769 },
        mdMax () { return this.windowWidth < 992 },
        lgMax () { return this.windowWidth < 1200 },
        getBorderClass (cID) {
            return this.colors[cID % this.colors.length]
        },
        beautifyDate (date, displayDate = true, displayTime = true) {
            if (!date) {
                return ''
            }
            var year = date.substring(0, 4)
            var month = date.substring(5, 7)
            var day = date.substring(8, 10)
            var time = date.substring(11, 16)
            var s = ''
            if (displayDate) {
                s += day + '-' + month + '-' + year
            }
            if (displayDate && displayTime) {
                s += ' '
            }
            if (displayTime) {
                s += time
            }
            return s
        }
    },
    template: '<App/>'
})
