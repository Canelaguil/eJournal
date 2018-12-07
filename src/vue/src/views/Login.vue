<template>
    <content-single-column>
        <h1>Login</h1>
        <login-form @handleAction="handleLoginSucces"/>
    </content-single-column>
</template>

<script>
import contentSingleColumn from '@/components/columns/ContentSingleColumn.vue'
import loginForm from '@/components/account/LoginForm.vue'
import routerConstraints from '@/utils/constants/router_constraints.js'

export default {
    name: 'Login',
    data () {
        return {
            username: '',
            password: ''
        }
    },
    methods: {
        handleLoginSucces () {
            if (this.$root.previousPage === null || this.$root.previousPage.name === null ||
                routerConstraints.PERMISSIONLESS_CONTENT.has(this.$root.previousPage.name)) {
                this.$router.push({name: 'Home'})
            }

            this.$router.push({name: this.$root.previousPage.name, params: this.$root.previousPage.params})
        }
    },
    components: {
        'content-single-column': contentSingleColumn,
        'login-form': loginForm
    }
}
</script>
