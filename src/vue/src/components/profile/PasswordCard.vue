<template>
    <div>
        <h2 class="mb-2">Change password</h2>
        <h2 class="field-heading">Old password</h2>
        <b-input class="theme-input multi-form" v-model="oldPass" type="password" placeholder="Old password"/>
        <h2 class="field-heading">New password</h2>
        <b-input class="theme-input multi-form" v-model="newPass" type="password" placeholder="New password"/>
        <h2 class="field-heading">Repeat new password</h2>
        <b-input class="theme-input multi-form" v-model="newPassRepeat" type="password" placeholder="Repeat new password"/>
        <b-button @click="changePassword" class="add-button float-right">
            <icon name="save"/>
            Save
        </b-button>
    </div>
</template>

<script>
import icon from 'vue-awesome/components/Icon'
import validation from '@/utils/validation.js'

import authAPI from '@/api/auth'

export default {
    data () {
        return {
            checkbox: false,
            oldPass: '',
            newPass: '',
            newPassRepeat: ''
        }
    },
    methods: {
        changePassword () {
            if (validation.validatePassword(this.newPass, this.newPassRepeat)) {
                authAPI.changePassword(this.newPass, this.oldPass, {responseSuccessToast: true})
            }
        },
        isChanged () {
            return (this.oldPass !== '' || this.newPass !== '' || this.newPassRepeat !== '')
        }
    },
    components: {
        icon
    }
}
</script>
