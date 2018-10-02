<!-- Loads a preview of a template. -->
<template>
    <b-card class="no-hover">
        <h2>{{ template.name }}</h2>
        <div v-for="(field, i) in template.field_set" :key="field.eID" class="multi-form">
            <h2 v-if="field.title" class="field-heading" :class="{ 'required': field.required }">{{ field.title }}</h2>
            <p v-if="field.description">{{ field.description }}</p>

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
            />
            <file-upload-input
                v-else-if="field.type == 'f'"
                class="input-disabled"
                :acceptedFiletype="'*/*'"
                :maxSizeBytes="$root.maxFileSizeBytes"
                :autoUpload="false"
                :aID="$route.params.aID"
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
        </div>
    </b-card>
</template>

<script>
import fileUploadInput from '@/components/assets/file_handling/FileUploadInput.vue'
import pdfDisplay from '@/components/assets/PdfDisplay.vue'
import textEditor from '@/components/assets/TextEditor.vue'
import icon from 'vue-awesome/components/Icon'
import urlInput from '@/components/assets/UrlInput.vue'

export default {
    props: ['template'],
    components: {
        'pdf-display': pdfDisplay,
        'file-upload-input': fileUploadInput,
        'text-editor': textEditor,
        'url-input': urlInput,
        icon
    }
}
</script>
