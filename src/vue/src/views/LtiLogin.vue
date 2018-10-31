<template>
    <content-single-column>
        <h1 class="mb-2">Welcome to eJournal!</h1>
        <b-card class="no-hover blue-border">
            <h2 class="multi-form">Let's get started</h2>
            <span class="d-block mb-2">
                Good to see you, <i>{{ lti.fullname }}</i>. In order to link your learning environment
                to eJournal, please choose one of the options below.
            </span>
            <lti-create-link-user v-if="handleUserIntegration" @handleAction="userIntegrated" :lti="lti"/>
        </b-card>
    </content-single-column>
</template>

<script>
import contentSingleColumn from '@/components/columns/ContentSingleColumn.vue'
import ltiCreateLinkUser from '@/components/lti/LtiCreateLinkUser.vue'

export default {
    name: 'LtiLogin',
    components: {
        'content-single-column': contentSingleColumn,
        'lti-create-link-user': ltiCreateLinkUser
    },
    data () {
        return {
            /* Variables for loading the right component. */
            handleUserIntegration: false,

            /* Possible states for the control flow */
            states: {
                state: '',
                key_error: '-2',
                bad_auth: '-1',
                no_user: '0',
                logged_in: '1'
            },

            lti: {
                ltiJWT: '',
                fullname: '',
                username: '',
                email: ''
            }
        }
    },
    methods: {
        userIntegrated () {
            this.$router.push({
                name: 'LtiLaunch',
                query: {
                    ltiJWT: this.lti.ltiJWT
                }
            })
        }
    },
    mounted () {
        if (this.$route.query.state === this.states.bad_auth) {
            this.$router.push({
                name: 'ErrorPage',
                params: {
                    code: '511',
                    reasonPhrase: 'Network authorization required',
                    description: `Invalid credentials from the LTI environment.
                                  Please contact the system administrator.`
                }
            })
        } else if (this.$route.query.state === this.states.key_error) {
            this.$router.push({
                name: 'ErrorPage',
                params: {
                    code: '400',
                    reasonPhrase: 'Missing parameter in LTI request',
                    description: this.$route.query.description + `
                    Please contact the system administrator.`
                }
            })
        } else {
            this.lti.ltiJWT = this.$route.query.lti_params

            /* The LTI parameters are verified in our backend, and the corresponding user is logged in. */
            if (this.$route.query.state === this.states.logged_in) {
                this.$store.commit('user/SET_JWT', { access: this.$route.query.jwt_access, refresh: this.$route.query.jwt_refresh })
                this.$store.dispatch('user/populateStore').then(_ => {
                    this.userIntegrated()
                }, error => {
                    this.$router.push({
                        name: 'ErrorPage',
                        params: {
                            code: error.response.status,
                            reasonPhrase: error.response.statusText,
                            description: 'Could not fetch all user data, please try again.'
                        }
                    })
                })

            /* The LTI parameters are verified in our backend, however there is no corresponding user yet. We must create/connect one. */
            } else if (this.$route.query.state === this.states.no_user) {
                this.$store.commit('user/LOGOUT') // Ensures no old user is loaded from local storage.
                if (this.$route.query.fullname !== undefined) {
                    this.lti.fullname = this.$route.query.fullname
                }
                if (this.$route.query.username !== undefined) {
                    this.lti.username = this.$route.query.username
                }
                if (this.$route.query.email !== undefined) {
                    this.lti.email = this.$route.query.email
                }

                this.handleUserIntegration = true
            } else {
                this.$router.push({
                    name: 'ErrorPage',
                    params: {
                        code: '500',
                        reasonPhrase: 'Internal Server Error',
                        description: `Received invalid state from the server
                                      when trying to integrate the new user.
                                      Please contact the system administrator
                                      for more information. Further integration
                                      is not possible.`
                    }
                })
            }
        }
    }
}
</script>
