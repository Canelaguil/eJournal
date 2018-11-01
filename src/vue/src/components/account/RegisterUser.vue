<template>
    <b-card class="no-hover">
        <h2 v-if="lti" class="field-heading">Username</h2>
        <b-input v-if="lti" class="multi-form theme-input" :value="this.lti.username" disabled/>
        <b-form @submit.prevent="onSubmit" @reset.prevent="onReset">
            <h2 v-if="!lti" class="field-heading">Username</h2>
            <b-input v-if="!lti" class="multi-form theme-input" v-model="form.username" placeholder="Username" required/>
            <h2 v-if="!lti" class="field-heading">First name</h2>
            <b-input v-if="!lti" class="multi-form theme-input" v-model="form.firstname" placeholder="First name" required/>
            <h2 v-if="!lti" class="field-heading">Last name</h2>
            <b-input v-if="!lti" class="multi-form theme-input" v-model="form.lastname" placeholder="Last name" required/>
            <h2 class="field-heading">Password</h2>
            <b-input class="multi-form theme-input" v-model="form.password" type="password" placeholder="Password" required/>
            <h2 class="field-heading">Repeat password</h2>
            <b-input class="multi-form theme-input" v-model="form.password2" type="password" placeholder="Repeat password" required/>
            <h2 v-if="!lti" class="field-heading">Email</h2>
            <b-input v-if="!lti" class="multi-form theme-input" v-model="form.email" placeholder="Email" required/>
            <b-button class="float-left change-button multi-form" type="reset">
                <icon name="undo"/>
                Reset
            </b-button>
            <b-button class="float-right multi-form" type="submit">
                <icon name="user-plus"/>
                Create account
            </b-button>
        </b-form>
    </b-card>
</template>

<script>
import icon from 'vue-awesome/components/Icon'

import authAPI from '@/api/auth'
import validation from '@/utils/validation.js'
import statuses from '@/utils/constants/status_codes.js'

export default {
    name: 'RegisterUser',
    props: ['lti'],
    data () {
        return {
            form: {
                username: '',
                password: '',
                password2: '',
                firstname: '',
                lastname: '',
                email: '',
                ltiJWT: ''
            }
        }
    },
    methods: {
        onSubmit () {
            if (this.lti) {
                this.form.username = this.lti.username
                this.form.firstname = this.lti.firstname
                this.form.lastname = this.lti.lastname
                this.form.email = this.lti.email
                this.form.ltiJWT = this.lti.ltiJWT
            }

            if (validation.validatePassword(this.form.password, this.form.password2) && validation.validateEmail(this.form.email)) {
                authAPI.register(this.form.username, this.form.password, this.form.firstname, this.form.lastname,
                    this.form.email, this.form.ltiJWT, {
                        customSuccessToast: this.lti ? '' : 'Registration successful! Please follow the instructions sent to ' + this.form.email +
                                                            ' to confirm your email address.'
                    })
                    .then(_ => {
                        this.$store.dispatch('user/login', { username: this.form.username, password: this.form.password })
                            .then(_ => { this.$emit('handleAction') })
                            .catch(_ => { this.$toasted.error('Error logging in with your newly created account, please contact a system administrator or try registering again.') })
                    })
                    .catch(error => {
                        if (error.response.status === statuses.FORBIDDEN) {
                            this.$router.push({
                                name: 'ErrorPage',
                                params: {
                                    code: error.response.status,
                                    reasonPhrase: error.response.statusText,
                                    description: error.response.data.description
                                }
                            })
                        }
                    })
            }
        },
        onReset (evt) {
            this.form.username = ''
            this.form.password = ''
            this.form.password2 = ''
            this.form.firstname = ''
            this.form.lastname = ''
            this.form.email = ''
        }
    },
    components: {
        icon
    }
}
</script>
