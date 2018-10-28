<template>
    <content-single-column>
        <h1>Welcome{{ this.name ? ' to ' + this.name : '' }}!</h1>
        <b-card class="no-hover blue-border">
            <h2 class="multi-form">Let's get started</h2>
            <b-row>
                <b-col md="6">
                    <b-card class="no-hover full-height">
                        <b-button class="add-button full-width" :to="{ name: 'Register' }">
                            <h2 class="lti-button-text">
                                <icon name="user-plus" scale="1.5"/>
                                Register
                            </h2>
                        </b-button>
                        <hr/>
                        Click the button above to register a new account.
                        In the beginning you will not be linked to any course however. Contact a teacher or connect your account with Canvas to connect to a course.
                    </b-card>
                </b-col>
                <b-col md="6">
                    <b-card class="no-hover full-height">
                        <b-button class="default-button full-width" :to="{ name: 'Login' }">
                            <h2 class="lti-button-text">
                                <icon name="sign-in" scale="1.5"/>
                                Login
                            </h2>
                        </b-button>
                        <hr/>
                        If you already have an account on eJournal, click the button above to login.
                    </b-card>
                </b-col>
            </b-row>
        </b-card>
        <b-card class="no-hover blue-border">
            <h2 class="multi-form">Want to use eJournal for your organisation?</h2>
            <b-row>
                <b-col md="6">
                    <b-card class="no-hover full-height">
                        <b-button class="change-button full-width" href="mailto:contact@ejourn.al">
                            <h2 class="lti-button-text">
                                <icon name="comments" scale="1.5"/>
                                Contact
                            </h2>
                        </b-button>
                        <hr/>
                        If you want to use eJournal for an organisation, or just want to get some information first, contact us!
                    </b-card>
                </b-col>
                <b-col md="6">
                    <b-card class="no-hover full-height">
                        <b-button class="black-button full-width" href="https://github.com/eJourn-al/eJournal/">
                            <h2 class="lti-button-text">
                                <icon name="github" scale="1.5"/>
                                GitHub
                            </h2>
                        </b-button>
                        <hr/>
                        This is an open source project. This means you can also deploy it yourself to try it out.
                        The button above will bring you to the GitHub repository where there are further instructions on how to deploy.
                    </b-card>
                </b-col>
            </b-row>
        </b-card>
        <b-card class="no-hover">
            <h2 class="multi-form">Made By <a href="https://www.linkedin.com/company/ejourn-al/">eJournal</a></h2>
            <b-button class="black-button full-width" href="/static/eJournal-privacy-notice.pdf">
                <h2 class="lti-button-text">
                    <icon name="file" scale="1.5"/>
                    Privacy Notice
                </h2>
            </b-button>
            <hr/>
            We reserve the right to change this privacy policy as we may deem necessary from time to time or as may be required by law. Any changes will be immediately posted on the website and you are deemed to have accepted the terms of the privacy policy on your first use of the website following the alterations.
        </b-card>
        <b-row>
            <span class="copy">
                &copy; 2018 - eJourn.al
            </span>
        </b-row>
    </content-single-column>
</template>
<style lang="sass">
.copy
    text-align: center
    width: 100%
    margin-bottom: 10px
</style>
<script>
import contentSingleColumn from '@/components/columns/ContentSingleColumn.vue'
import icon from 'vue-awesome/components/Icon'

import instanceAPI from '@/api/instance'

export default {
    name: 'Guest',
    components: {
        icon,
        'content-single-column': contentSingleColumn
    },
    data () {
        return {
            name: null
        }
    },
    created () {
        instanceAPI.get()
            .then(instance => { this.name = instance.name })
    }
}
</script>
