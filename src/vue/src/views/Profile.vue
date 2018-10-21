<template>
    <content-single-column>
        <bread-crumb>&nbsp;</bread-crumb>
        <b-card class="no-hover blue-border">
            <profile-data ref="profileData"/>
            <notification-card/>
            <password-card ref="passData"/>
        </b-card>
    </content-single-column>
</template>

<script>
import contentSingleColumn from '@/components/columns/ContentSingleColumn.vue'
import profileData from '@/components/profile/ProfileData.vue'
import notificationCard from '@/components/profile/NotificationCard.vue'
import passwordCard from '@/components/profile/PasswordCard.vue'
import breadCrumb from '@/components/assets/BreadCrumb.vue'

export default {
    name: 'Profile',
    components: {
        'content-single-column': contentSingleColumn,
        'bread-crumb': breadCrumb,
        'profile-data': profileData,
        'notification-card': notificationCard,
        'password-card': passwordCard
    },
    beforeRouteLeave (to, from, next) {
        if ((this.$refs.profileData.isChanged() || this.$refs.passData.isChanged()) &&
            !confirm('Unsaved changes will be lost if you leave. Do you wish to continue?')) {
            next(false)
            return
        }

        next()
    }
}
</script>
