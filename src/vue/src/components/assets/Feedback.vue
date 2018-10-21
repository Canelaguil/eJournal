<template>
    <b-card class="no-hover">
        <h2>Thank you for helping us improve eJournal</h2>
        Hi {{ $store.getters['user/firstName'] }}! If you have any suggestions for improvements or encountered
        any issues/bugs, please inform us by filling in the form below. We aim to get back to you as soon as possible.
        <hr/>
        <h2 class='field-heading'>Topic:*</h2>
        <b-input
            class="theme-input multi-form"
            v-model="topic"
            type="text"
            required
        />
        <h2 class='field-heading'>Type of feedback:*</h2>
        <b-form-select
            class="theme-input multi-form"
            :options="types"
            required
            v-model="type"/>

        <h2 class='field-heading'>Feedback:*</h2>
        <b-form-textarea
           class="theme-input multi-form"
           v-model="feedback"
           :rows="4"
           :max-rows="10"
           required
        />
        <h2 class='field-heading'>Attachments:</h2>
        <b-form-file
            v-model="files"
            :state="Boolean(files)"
            class="fileinput multi-form"
            multiple
            ref="fileinput"
            @change="filesHandler"
            placeholder="Choose a file...">
        </b-form-file>

        <pretty-checkbox v-model="privacyAgreement" class="p-svg" color="primary">
            <svg slot="extra" class="svg svg-icon" viewBox="0 0 20 20">
                <path d="M7.629,14.566c0.125,0.125,0.291,0.188,0.456,0.188c0.164,0,0.329-0.062,0.456-0.188l8.219-8.221c0.252-0.252,0.252-0.659,0-0.911c-0.252-0.252-0.659-0.252-0.911,0l-7.764,7.763L4.152,9.267c-0.252-0.251-0.66-0.251-0.911,0c-0.252,0.252-0.252,0.66,0,0.911L7.629,14.566z"
                      style="stroke: white;fill:white">
                </path>
            </svg>
            I agree to share my username, email, first name and feedback with eJournal's email provider Zoho.*
        </pretty-checkbox>

        <b-button class="add-button float-right" @click="$emit(sendFeedback())">
            <icon name="paper-plane"/>
            Send
        </b-button>

    </b-card>
</template>

<script>
import icon from 'vue-awesome/components/Icon'
import feedback from '@/api/feedback'
import prettyCheckbox from 'pretty-checkbox-vue/check'

export default {
    data () {
        return {
            topic: '',
            feedback: '',
            type: null,
            types: [
                {text: 'Select one', value: null},
                'Issue/Bug', 'Suggestion', 'Other'
            ],
            files: null,
            privacyAgreement: false
        }
    },
    components: {
        'pretty-checkbox': prettyCheckbox,
        icon
    },
    methods: {
        filesHandler (e) {
            let files = e.target.files
            if (files.length < 1) { return }

            var uploadSize = 0
            for (var i = 0; i < files.length; i++) {
                uploadSize += files[i].size
                if (uploadSize > this.$root.maxEmailFileSizeBytes) {
                    this.$toasted.error('The selected files exceed the total maximum file size of: 10 mb.')
                    this.$refs.fileinput.reset()
                    this.files = null
                    return
                }
            }

            this.files = files
        },
        sendFeedback () {
            if (this.topic === '') {
                this.$toasted.error('Please fill in a topic')
            } else if (this.type == null) {
                this.$toasted.error('Please choose a feedback type')
            } else if (this.feedback === '') {
                this.$toasted.error('Please describe your feedback')
            } else if (!this.privacyAgreement) {
                this.$toasted.error('You will have to agree to the privacy agreement in order for us to read your feedback!')
            } else {
                var data = new FormData()
                data.append('topic', this.topic)
                data.append('ftype', this.type)
                data.append('feedback', this.feedback)
                data.append('user_agent', navigator.userAgent)
                data.append('url', window.location.href)
                if (this.files != null) {
                    for (var i = 0; i < this.files.length; i++) {
                        data.append('files', this.files[i])
                    }
                }

                feedback.sendFeedback(data)
                    .then(response => {
                        this.$toasted.success(response.data.description)
                    })
                    .catch(error => { this.$toasted.error(error.response.data.description) })

                this.resetFeedback()
                return 'feedbackSent'
            }

            return 'feedbackNotSent'
        },
        resetFeedback () {
            this.topic = ''
            this.type = null
            this.feedback = ''
            this.files = null
            this.$refs.fileinput.reset()
        }
    }
}
</script>

<style lang="scss">
// This could be prevented by converting the scss to sass, then importing our colors to the pretty-checkbox settings
// followed by overwriting the defaults. (The variables have to be set before the import for this to work, same
// language scope.)
$pretty--color-primary: #252C39;
@import 'pretty-checkbox/src/pretty-checkbox.scss';
</style>
