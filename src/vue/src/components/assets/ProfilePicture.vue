<template>
    <div>
        <img v-if="user.lti_image" :src="user.lti_image">
        <img v-else :src="profilePicture">
    </div>
</template>

<script>
import userAPI from '@/api/user'

export default {
    props: ['user'],
    data () {
        return {
            profilePicture: null
        }
    },
    mounted () {
        if (!this.user.lti_image) {
            userAPI.downloadProfilePicture(this.user.id, { redirect: false })
                .then(response => {
                    try {
                        var reader = new FileReader()
                        reader.onload = () => {
                            this.profilePicture = reader.result
                        }
                        reader.readAsDataURL(new Blob([response.data], { type: response.headers['content-type'] }))
                    } catch (_) {
                        this.$toasted.error('Failed to read profile picture data.')
                    }
                })
        }
    }
}
</script>
