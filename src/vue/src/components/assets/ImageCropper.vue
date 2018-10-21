<template>
    <b-card class="no-hover">
        <div class="profile-picture-lg profile-picture-cropper">
            <croppa v-model="croppa"
                disable-click-to-choose
                :width="250"
                :height="250"
                canvas-color="transparent"
                :show-remove-button="false"
                :show-loading="true"
                :loading-size="50"
                accept="image/*"
                :file-size-limit="this.$root.maxFileSizeBytes"
                @file-type-mismatch="onFileTypeMismatch"
                @file-size-exceed="onFileSizeExceed"
                :initial-image="pictureUrl"
                initial-size="natural"
                initial-position="center"/>
        </div>
        <b-button @click="croppa.chooseFile()">
            <icon name="upload"/>
            Upload
        </b-button>
        <b-button class="change-button" @click="refreshPicture()">
            <icon name="undo"/>
            Reset
        </b-button>
        <b-button class="add-button float-right" @click="savePicture()">
            <icon name="save"/>
            Save
        </b-button>
    </b-card>
</template>

<script>
import icon from 'vue-awesome/components/Icon'
import Croppa from 'vue-croppa'

export default {
    name: 'ImageCropper',
    props: ['pictureUrl'],
    components: {
        icon,
        'croppa': Croppa.component
    },
    data () {
        return {
            croppa: {}
        }
    },
    methods: {
        onFileTypeMismatch (file) {
            this.$toasted.error('Invalid file type. Please choose an image.')
        },
        onFileSizeExceed (file) {
            this.$toasted.error('The profile picture exceeds the maximum file size of ' + this.$root.maxFileSizeBytes + ' bytes.')
        },
        savePicture () {
            this.croppa.generateBlob(blob => {
                this.$emit('newPicture', blob)
            }, 'image/jpeg')
        },
        refreshPicture () {
            this.croppa.refresh()
        }
    }
}
</script>

<style lang="sass">
@import '~sass/modules/colors.sass'

.croppa-container
    background-color: $theme-dark-blue
    height: 100%
    width: 100%

.croppa-container:hover
    opacity: 1
    background-color: $theme-dark-blue
</style>
