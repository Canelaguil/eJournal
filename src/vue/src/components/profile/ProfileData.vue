<template>
    <b-row>
        <b-col md="5" sm="12" class="text-center">
            <b-modal
                ref="cropperModal"
                title="Edit profile picture"
                hide-footer>
                    <cropper v-if="this.profileImageDataURL" ref="cropperRef" :pictureUrl="this.profileImageDataURL" @newPicture="fileHandler"/>
            </b-modal>
            <div class="profile-picture-lg">
                <img :src="storeProfilePic">
                <b-button @click="showCropperModal()">
                    <icon name="edit"/>
                    Edit
                </b-button>
            </div>
        </b-col>
        <b-col md="7" sm="12">
            <h2 class="mb-2">User details</h2>
            <b-form-input :readonly="true" class="theme-input multi-form input-disabled" :value="storeUsername" type="text"/>
            <b-form-input :readonly="(storeLtiID) ? true : false"
                :class="{'input-disabled': (storeLtiID) ? true : false}"
                class="theme-input multi-form"
                v-model="firstName"
                type="text"
                placeholder="First name"/>
            <b-form-input :readonly="(storeLtiID) ? true : false"
                :class="{'input-disabled': (storeLtiID) ? true : false}"
                class="theme-input multi-form"
                v-model="lastName"
                type="text"
                placeholder="Last name"/>
            <email/>

            <b-button v-if="!storeLtiID" class="add-button multi-form float-right" @click="saveUserdata">
                <icon name="save"/>
                Save
            </b-button>
            <b-button class="multi-form" @click="downloadUserData">
                <icon name="download"/>
                Download Data
            </b-button>
        </b-col>
    </b-row>
</template>

<script>
import email from '@/components/profile/Email.vue'
import userAPI from '@/api/user'
import icon from 'vue-awesome/components/Icon'
import cropper from '@/components/assets/ImageCropper'
import { mapGetters } from 'vuex'

export default {
    components: {
        icon,
        email,
        cropper
    },
    data () {
        return {
            file: null,
            profileImageDataURL: null,
            showEmailValidationInput: true,
            emailVerificationToken: null,
            emailVerificationTokenMessage: null,
            firstName: null,
            lastName: null,
            updateCropper: false
        }
    },
    computed: {
        ...mapGetters({
            storeUsername: 'user/username',
            storeLtiID: 'user/ltiID',
            storeProfilePic: 'user/profilePicture',
            storeFirstName: 'user/firstName',
            storeLastName: 'user/lastName'
        })
    },
    methods: {
        showCropperModal () {
            this.$refs.cropperRef.refreshPicture()
            this.$refs['cropperModal'].show()
        },
        saveUserdata () {
            userAPI.update(0, {first_name: this.firstName, last_name: this.lastName}, {customSuccessToast: 'Saved profile data.'})
                .then(_ => {
                    this.$store.commit('user/SET_FULL_USER_NAME', {firstName: this.firstName, lastName: this.lastName})
                })
        },
        fileHandler (dataURL) {
            userAPI.updateProfilePictureBase64(dataURL, {customSuccessToast: 'Profile picture updated.'})
                .then(_ => {
                    this.$store.commit('user/SET_PROFILE_PICTURE', dataURL)
                    this.profileImageDataURL = dataURL
                    this.$refs['cropperModal'].hide()
                })
        },
        downloadUserData () {
            userAPI.GDPR(0)
                .then(response => {
                    try {
                        let blob = new Blob([response.data], { type: response.headers['content-type'] })
                        let link = document.createElement('a')
                        link.href = window.URL.createObjectURL(blob)
                        link.download = this.storeUsername + '_all_user_data.zip'
                        document.body.appendChild(link)
                        link.click()
                        link.remove()
                    } catch (_) {
                        this.$toasted.error('Error creating file locally.')
                    }
                })
        },
        isChanged () {
            return (this.firstName !== this.storeFirstName || this.lastName !== this.storeLastName)
        }
    },
    mounted () {
        this.profileImageDataURL = this.storeProfilePic
        this.firstName = this.storeFirstName
        this.lastName = this.storeLastName
    }
}
</script>
