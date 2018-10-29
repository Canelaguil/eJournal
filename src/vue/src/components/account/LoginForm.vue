<template>
    <div>
        <b-card class="blue-border no-hover card-last-elem-button">
            <b-form @submit.prevent="handleLogin()">
                <h2 class="field-heading">Username</h2>
                <b-input class="multi-form theme-input" v-model="username" autofocus required placeholder="Username"/>
                <h2 class="field-heading">Password</h2>
                <b-input class="multi-form theme-input" type="password" @keyup.enter="handleLogin()" v-model="password" required placeholder="Password"/>
                <b-button class="multi-form change-button" v-b-modal.forgotPasswordModal>
                    <icon name="question"/>
                    Forgot password
                </b-button>
                <b-button class="float-right multi-form" type="submit">
                    <icon name="sign-in"/>
                    Log in
                </b-button>
            </b-form>
        </b-card>

        <b-modal
            ref="forgotPasswordModalRef"
            id="forgotPasswordModal"
            size="lg"
            @shown="$refs.usernameEmailInput.focus(); usernameEmail=username"
            title="Password recovery"
            hide-footer>
            <b-card class="no-hover">
                <b-form @submit.prevent="handleForgotPassword">
                    <h2 class="field-heading">Username or email</h2>
                    <b-input
                        v-model="usernameEmail"
                        required
                        placeholder="Please enter your username or email"
                        ref="usernameEmailInput"
                        class="theme-input multi-form"
                    />
                    <b-button class="float-right change-button" type="submit">
                        <icon name="key"/>
                        Recover password
                    </b-button>
                    <b-button class="delete-button" @click="$refs.forgotPasswordModalRef.hide()">
                        <icon name="times"/>
                        Cancel
                    </b-button>
                </b-form>
            </b-card>
        </b-modal>
    </div>
</template>

<script>
import icon from 'vue-awesome/components/Icon'
import validation from '@/utils/validation.js'

import authAPI from '@/api/auth'

export default {
    name: 'LoginForm',
    data () {
        return {
            usernameEmail: null,
            username: null,
            password: null
        }
    },
    methods: {
        handleForgotPassword () {
            let username = ''
            let emailAdress = ''

            if (validation.validateEmail(this.usernameEmail, false)) {
                emailAdress = this.usernameEmail
            } else {
                username = this.usernameEmail
            }

            authAPI.forgotPassword(username, emailAdress, {responseSuccessToast: true})
                .then(response => { this.$refs.forgotPasswordModalRef.hide() })
        },
        handleLogin () {
            this.$store.dispatch('user/login', { username: this.username, password: this.password })
                .then(_ => { this.$emit('handleAction') })
                .catch(_ => { this.$toasted.error('Could not login') })
        }
    },
    mounted () {
        if (this.$root.previousPage && this.$root.previousPage.name === 'PasswordRecovery') {
            this.username = this.$root.previousPage.params.username
        }
    },
    components: {
        icon
    }
}
</script>
