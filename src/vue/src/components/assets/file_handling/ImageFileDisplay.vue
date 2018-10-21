<template>
    <div class="image-field">
        <div class="image-controls mb-2 unselectable" @click="handleDownload">
            <icon name="image"/>
            <i><span>{{ fileName }}</span></i>
        </div>
        <transition name="fade">
            <img :class="showImage" v-if="fileURL && show" :src="fileURL">
        </transition>
    </div>
</template>

<script>
import userAPI from '@/api/user.js'
import icon from 'vue-awesome/components/Icon'
import genericUtils from '@/utils/generic_utils.js'

export default {
    props: {
        fileName: {
            required: true,
            String
        },
        authorUID: {
            required: true,
            String
        },
        display: {
            default: false
        },
        entryID: {
            required: true,
            String
        },
        nodeID: {
            required: true,
            String
        },
        contentID: {
            required: true,
            String
        }
    },
    components: {
        icon
    },
    data () {
        return {
            show: false,
            fileURL: null
        }
    },
    computed: {
        showImage () {
            return this.show ? 'open' : 'closed'
        }
    },
    methods: {
        handleDownload () {
            this.show = !this.show

            if (!this.fileURL && this.show) {
                this.fileDownload()
            }
        },
        fileDownload () {
            userAPI.download(this.authorUID, this.fileName, this.entryID, this.nodeID, this.contentID)
                .then(response => {
                    let blob = new Blob([response.data], { type: response.headers['content-type'] })
                    this.fileURL = window.URL.createObjectURL(blob)
                }, error => {
                    genericUtils.displayArrayBufferRequestError(this, error)
                })
                .catch(_ => {
                    this.$toasted.error('Error creating file.')
                })
        }
    },
    created () {
        this.show = this.display

        if (this.show) { this.fileDownload() }
    },
    destroy () { this.downloadLink.remove() }
}
</script>

<style lang="sass">
@import '~sass/modules/colors.sass'

.closed
    -webkit-transition: height, .6s linear

.open
    max-height: 100vh
    -webkit-transition: height, .6s linear

.image-field
    img
        display: inline
    .image-controls
        &:hover
            cursor: pointer
        span
            text-decoration: underline !important
        svg
            margin-bottom: -2px
</style>
