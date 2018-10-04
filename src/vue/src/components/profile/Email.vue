<template>
    <div>
        <b-input-group class="multi-form">
            <b-input readonly class="input-disabled" :value="$store.getters['user/email']" type="text"/>
            <b-input-group-text slot="append" class="input-append-icon">
                <icon
                    v-if="!$store.getters['user/verifiedEmail']"
                    name="times"
                    v-b-tooltip.hover
                    :title="(showEmailValidationInput) ? 'Enter the email verification token below.' : 'Click to verify your email!'"
                    @click.native="requestEmailVerification"
                    class="crossed-icon"
                />
                <icon
                    v-if="$store.getters['user/verifiedEmail']"
                    name="check"
                    v-b-tooltip.hover
                    title="Your email is verified!"
                    class="checked-icon"
                />
            </b-input-group-text>
        </b-input-group>

        <b-form v-if="!$store.getters['user/verifiedEmail'] && showEmailValidationInput" >
            <b-input-group class="multi-form">
                <b-form-input
                class="theme-input"
                    v-b-tooltip.hover
                    :title="(emailVerificationTokenMessage) ? emailVerificationTokenMessage : 'Enter your token'"
                    required
                    v-model="emailVerificationToken"
                    placeholder="Enter the email verification token."
                />
                <b-input-group-text slot="append" class="input-append-icon">
                    <icon
                        name="check" class="validate-icon"
                        v-b-tooltip.hover title="Validate verification code."
                        @click.native="verifyEmail"
                    />
                </b-input-group-text>
            </b-input-group>
        </b-form>
    </div>
</template>

<script>
import userAPI from '@/api/user.js'
import icon from 'vue-awesome/components/Icon'

export default {
    components: {
        icon
    },
    data () {
        return {
            showEmailValidationInput: false,
            emailVerificationToken: null,
            emailVerificationTokenMessage: null
        }
    },
    methods: {
        requestEmailVerification () {
            if (!this.showEmailValidationInput) {
                userAPI.requestEmailVerification()
                    .then(response => {
                        this.showEmailValidationInput = true
                        this.$toasted.success(response.data.description)
                    })
                    .catch(error => { this.$toasted.error(error.response.data.description) })
            }
        },
        verifyEmail () {
            userAPI.verifyEmail(this.emailVerificationToken)
                .then(response => {
                    this.$toasted.success(response.data.description)
                    this.$store.commit('user/EMAIL_VERIFIED')
                    this.showEmailValidationInput = false
                })
                .catch(_ => {
                    this.emailVerificationTokenMessage = 'Invalid token'
                })
        }
    }
}
</script>
