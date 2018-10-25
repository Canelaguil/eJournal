<!-- Loads a preview of a template. nID are required but unused as autoupload is disabled. -->
<template>
    <b-card class="no-hover">
        <h2>{{ template.name }}</h2>
        <div v-for="(field, i) in template.field_set" :key="field.eID" class="multi-form">
            <h2 v-if="field.title" class="field-heading" :class="{ 'required': field.required }">{{ field.title }}</h2>
            <div v-if="field.description" v-html="field.description"/>

            <b-textarea
                v-if="field.type == 't'"
                class="theme-input input-disabled"
            />
            <file-upload-input
                v-else-if="field.type == 'i'"
                class="input-disabled"
                :acceptedFiletype="'image/*'"
                :maxSizeBytes="$root.maxFileSizeBytes"
                :autoUpload="false"
                :aID="$route.params.aID"
                :nID="'1'"
            />
            <file-upload-input
                v-else-if="field.type == 'f'"
                class="input-disabled"
                :acceptedFiletype="'*/*'"
                :maxSizeBytes="$root.maxFileSizeBytes"
                :autoUpload="false"
                :aID="$route.params.aID"
                :nID="'1'"
            />
            <b-input
                v-else-if="field.type == 'v'"
                class="theme-input input-disabled"
                placeholder="Enter YouTube URL..."
            />
            <file-upload-input
                v-else-if="field.type == 'p'"
                class="input-disabled"
                :acceptedFiletype="'application/pdf'"
                :maxSizeBytes="$root.maxFileSizeBytes"
                :autoUpload="false"
                :aID="$route.params.aID"
                :nID="'1'"
            />
            <text-editor
                v-else-if="field.type == 'rt'"
                class="input-disabled"
                :id="'rich-text-editor-preview-field-' + i"
            />
            <url-input
                v-else-if="field.type == 'u'"
                class="input-disabled"
            />
            <flat-pickr
                v-else-if="field.type == 'd'"
                class="input-disabled theme-input full-width"
            />
            <b-form-select
                v-else-if="field.type == 's'"
                class="input-disabled"
                :value="null"
                :options="parseSelectionOptions(field.options)"
            />
        </div>
    </b-card>
</template>

<script>
import fileUploadInput from '@/components/assets/file_handling/FileUploadInput.vue'
import textEditor from '@/components/assets/TextEditor.vue'
import icon from 'vue-awesome/components/Icon'
import urlInput from '@/components/assets/UrlInput.vue'

export default {
    props: ['template'],
    components: {
        'file-upload-input': fileUploadInput,
        'text-editor': textEditor,
        'url-input': urlInput,
        icon
    },
    methods: {
        parseSelectionOptions (fieldOptions) {
            if (!fieldOptions) {
                return [{ value: null, text: 'Please select an option' }]
            }
            var options = JSON.parse(fieldOptions).filter(e => e).map(x => { return { value: x, text: x } })
            options.unshift({ value: null, text: 'Please select an option' })
            return options
        }
    }
}
</script>
