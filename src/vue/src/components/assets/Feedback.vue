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

        <b-form-checkbox v-model="privacyAgreement">
            I agree to share my username, email, first name and feedback with eJournal's email provider Zoho.*
        </b-form-checkbox>

        <b-button class="add-button float-right" @click="$emit(sendFeedback())">
            <icon name="paper-plane"/>
            Send
        </b-button>
    </b-card>
</template>

<script>
import icon from 'vue-awesome/components/Icon'
import feedbackAPI from '@/api/feedback'

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

                feedbackAPI.sendFeedback(data, {responseSuccessToast: true})

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
