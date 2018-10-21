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
            userAPI.getProfilePicture(this.user.id)
                .then(response => {
                    var reader = new FileReader()
                    var vm = this
                    reader.onload = () => {
                        vm.profilePicture = reader.result
                    }
                    reader.readAsDataURL(new Blob([response.data], { type: response.headers['content-type'] }))
                })
                .catch(error => {
                    this.$toasted.error(error.response.data.description)
                })
        }
    }
}
</script>
