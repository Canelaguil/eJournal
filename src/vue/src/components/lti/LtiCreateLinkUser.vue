<template>
    <b-row>
        <b-col md="6">
            <b-card class="no-hover full-height">
                <b-button class="add-button full-width" @click="showModal('createUserRef')">
                    <icon name="user-plus" class="mr-3" scale="1.8"/>
                    <h2 class="lti-button-text">Register new<br/>eJournal account</h2>
                </b-button>
                <hr/>
                If this is the first time you are here, click the button above to register a new account.
                This will be linked to your learning environment, allowing you to automatically
                log in next time around.
            </b-card>
        </b-col>
        <b-col md="6">
            <b-card class="no-hover full-height">
                <b-button class="change-button full-width" @click="showModal('linkUserRef')">
                    <icon name="link" class="mr-3" scale="1.8"/>
                    <h2 class="lti-button-text">Link to existing<br/>eJournal account</h2>
                </b-button>
                <hr/>
                If you already have an account on eJournal, you can link it to your learning environment
                by clicking the button above. Existing courses and assignments you participate in remain available.
            </b-card>
        </b-col>

        <b-modal
            ref="createUserRef"
            title="Register new eJournal account"
            size="lg"
            hide-footer
            no-enforce-focus>
                <register-user @handleAction="handleRegistered" :lti="lti"/>
        </b-modal>

        <b-modal
            ref="linkUserRef"
            title="Link to existing eJournal account"
            size="lg"
            hide-footer>
                <login-form @handleAction="handleLinked"/>
        </b-modal>
    </b-row>
</template>

<script>
import registerUser from '@/components/account/RegisterUser.vue'
import loginForm from '@/components/account/LoginForm.vue'

import userAPI from '@/api/user'
import icon from 'vue-awesome/components/Icon'

export default {
    name: 'LtiCreateLinkUser',
    props: ['lti'],
    components: {
        'register-user': registerUser,
        'login-form': loginForm,
        icon
    },
    methods: {
        signal (msg) {
            this.$emit('handleAction', msg)
        },
        showModal (ref) {
            this.$refs[ref].show()
        },
        hideModal (ref) {
            this.$refs[ref].hide()
        },
        handleRegistered () {
            this.hideModal('createUserRef')
            this.signal(['userIntegrated'])
        },
        handleLinked () {
            userAPI.update(0, {jwt_params: this.lti.ltiJWT})
                .then(_ => {
                    /* This is required because between the login and the connect of lti user to our user data can change. */
                    this.$store.dispatch('user/populateStore').then(_ => {
                        this.hideModal('linkUserRef')
                        this.signal(['userIntegrated'])
                    })
                })
        }
    }
}
</script>
