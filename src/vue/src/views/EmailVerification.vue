<template>
    <content-single-column>
        <h1>Email Verification</h1>
        <b-card class="blue-border no-hover">
            <div class="center-content">
                <h2 class="center-content">Verifying</h2><br/>
                <icon name="circle-o-notch" pulse scale="1.5"/>
            </div>
        </b-card>
    </content-single-column>
</template>

<script>
import contentSingleColumn from '@/components/columns/ContentSingleColumn.vue'
import icon from 'vue-awesome/components/Icon'
import userAPI from '@/api/user'

export default {
    name: 'EmailVerification',
    props: ['token'],
    mounted () {
        userAPI.verifyEmail(this.token, {responseSuccessToast: true})
            .then(response => {
                this.$store.commit('user/EMAIL_VERIFIED')
                this.$router.push({ name: 'Home' })
            })
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
    },
    components: {
        'content-single-column': contentSingleColumn,
        icon
    }
}
</script>
