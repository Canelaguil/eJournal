<template>
    <content-single-column>
        <h1>Password Recovery</h1>
        <b-card class="blue-border no-hover">
            <b-form @submit.prevent="recoverPassword()">
                <h2 class="field-heading">New password</h2>
                <b-input class="multi-form theme-input" type="password" v-model="password" required placeholder="New password"/>
                <h2 class="field-heading">Repeat new password</h2>
                <b-input class="multi-form theme-input" type="password" v-model="passwordRepeated" @keyup.enter="handleLogin()" required placeholder="Repeat new password"/>
                <b-button class="float-right multi-form add-button" type="submit">
                    <icon name="save"/>
                    Save
                </b-button>
            </b-form>
        </b-card>
    </content-single-column>
</template>

<script>
import contentSingleColumn from '@/components/columns/ContentSingleColumn.vue'
import icon from 'vue-awesome/components/Icon'

import authAPI from '@/api/auth'
import validation from '@/utils/validation.js'

export default {
    name: 'PasswordRecovery',
    props: ['username', 'recoveryToken'],
    data () {
        return {
            password: '',
            passwordRepeated: ''
        }
    },
    methods: {
        recoverPassword () {
            if (validation.validatePassword(this.password, this.passwordRepeated)) {
                authAPI.recoverPassword(this.username, this.recoveryToken, this.password, {responseSuccessToast: true})
                    .then(response => { this.$router.push({ name: 'Login' }) })
                    .catch(error => {
                        this.$router.push({
                            name: 'ErrorPage',
                            params: {
                                code: error.response.status,
                                reasonPhrase: error.response.statusText,
                                description: error.response.data.description
                            }
                        })
                    })
            }
        }
    },
    components: {
        'content-single-column': contentSingleColumn,
        icon
    }
}
</script>
