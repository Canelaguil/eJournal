<template>
    <b-row>
        <b-col cols="12">
            <h2 class="mb-2">Email notifications</h2>
        </b-col>
        <b-col cols="4">
            Grade updates
        </b-col>
        <b-col cols="8">
            <toggle-switch :isActive="$store.getters['user/gradeNotifications']"
                           @parentActive="getGradeNotification">
            </toggle-switch>
        </b-col>
        <b-col cols="4">
            Comments
        </b-col>
        <b-col cols="8">
            <toggle-switch :isActive="$store.getters['user/commentNotifications']"
                           @parentActive="getCommentNotification">
            </toggle-switch>
        </b-col>
    </b-row>
</template>

<script>
import Switch from '@/components/assets/SwitchComponent.vue'
import userAPI from '@/api/user.js'

export default {
    props: ['userData'],
    components: {
        'toggle-switch': Switch
    },
    methods: {
        getGradeNotification (isActive) {
            userAPI.update(0, {grade_notifications: isActive})
                .then(user => {
                    this.$store.commit('user/SET_GRADE_NOTIFICATION', user.grade_notifications)
                    this.$toasted.success('Grade notification setting updated successfully.')
                })
                .catch(error => { this.$toasted.error(error.response.data.description) })
        },
        getCommentNotification (isActive) {
            userAPI.update(0, {comment_notifications: isActive})
                .then(user => {
                    this.$store.commit('user/SET_COMMENT_NOTIFICATION', user.comment_notifications)
                    this.$toasted.success('Comment notification setting updated successfully.')
                })
                .catch(error => { this.$toasted.error(error.response.data.description) })
        }
    }
}
</script>
