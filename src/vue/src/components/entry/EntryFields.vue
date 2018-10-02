<template>
    <div v-if="!displayMode">
        <div v-for="(field, i) in template.field_set" :key="'node-' + nodeID + '-field-' + field.id" class="multi-form">
            <h2 v-if="field.title" class="field-heading" :class="{ 'required': field.required }">
                {{ field.title }}
            </h2>
            <p v-if="field.description">{{ field.description }}</p>

            <b-textarea v-if="field.type == 't'" class="theme-input" v-model="completeContent[i].data"/>
            <flat-pickr v-if="field.type == 'd'" class="theme-input full-width" v-model="completeContent[i].data"/>

            <file-upload-input
                v-else-if="field.type == 'i'"
                :placeholder="completeContent[i].data"
                :acceptedFiletype="'image/*'"
                :maxSizeBytes="$root.maxFileSizeBytes"
                :autoUpload="true"
                @fileUploadSuccess="completeContent[i].data = $event"
                :aID="$route.params.aID"
            />
            <file-upload-input
                v-else-if="field.type == 'f'"
                :placeholder="completeContent[i].data"
                :acceptedFiletype="'*/*'"
                :maxSizeBytes="$root.maxFileSizeBytes"
                :autoUpload="true"
                @fileUploadSuccess="completeContent[i].data = $event"
                :aID="$route.params.aID"
            />
            <b-input v-else-if="field.type == 'v'"
                class="theme-input"
                @input="completeContent[i].data = youtubeEmbedFromURL($event)"
                :placeholder="completeContent[i].data ? completeContent[i].data : 'Enter YouTube URL...'"
            />
            <file-upload-input
                v-else-if="field.type == 'p'"
                :placeholder="completeContent[i].data"
                :acceptedFiletype="'application/pdf'"
                :maxSizeBytes="$root.maxFileSizeBytes"
                :autoUpload="true"
                @fileUploadSuccess="completeContent[i].data = $event"
                :aID="$route.params.aID"
            />
            <text-editor
                v-else-if="field.type == 'rt'"
                :id="'rich-text-editor-field-' + i"
                :givenContent="completeContent[i].data ? completeContent[i].data : ''"
                @content-update="completeContent[i].data = $event"
            />
            <url-input
                v-else-if="field.type == 'u'"
                :placeholder="completeContent[i].data"
                @correctUrlInput="completeContent[i].data = $event"
            />
        </div>
    </div>
    <!-- Display section -->
    <div v-else>
        <div v-for="(field, i) in template.field_set" v-if="field.required || completeContent[i].data" :key="'node-' + nodeID + '-field-' + field.id" class="multi-form">
            <h2 v-if="field.title" class="field-heading" :class="{ 'required': field.required }">
                {{ field.title }}
            </h2>
            <span v-if="field.type == 't'" class="show-enters">{{ completeContent[i].data }}</span>
            <span v-if="field.type == 'd'" class="show-enters">{{ $root.beautifyDate(completeContent[i].data) }}</span>
            <image-file-display
                v-else-if="field.type == 'i'"
                :id="'image-display-field-' + i"
                :fileName="completeContent[i].data"
                :authorUID="authorUID"
            />
            <file-download-button
                v-else-if="field.type == 'f'"
                :fileName="completeContent[i].data"
                :authorUID="authorUID"
            />
            <b-embed
                v-else-if="field.type == 'v'"
                type="iframe"
                aspect="16by9"
                :src="completeContent[i].data"
                allowfullscreen
            />
            <pdf-display
                v-else-if="field.type == 'p'"
                :fileName="completeContent[i].data"
                :authorUID="authorUID"
            />
            <div v-else-if="field.type == 'rt'" v-html="completeContent[i].data"/>
            <a v-else-if="field.type == 'u'" :href="completeContent[i].data">{{ completeContent[i].data }}</a>
        </div>
    </div>
</template>

<script>
import fileUploadInput from '@/components/assets/file_handling/FileUploadInput.vue'
import textEditor from '@/components/assets/TextEditor.vue'
import urlInput from '@/components/assets/UrlInput.vue'
import fileDownloadButton from '@/components/assets/file_handling/FileDownloadButton.vue'
import imageFileDisplay from '@/components/assets/file_handling/ImageFileDisplay.vue'
import pdfDisplay from '@/components/assets/PdfDisplay.vue'

export default {
    props: {
        template: {
            required: true
        },
        completeContent: {
            default: false
        },
        displayMode: {
            type: Boolean,
            required: true
        },
        nodeID: {
            required: true
        },
        authorUID: {
            required: false
        }
    },
    components: {
        'file-upload-input': fileUploadInput,
        'text-editor': textEditor,
        'url-input': urlInput,
        'pdf-display': pdfDisplay,
        'file-download-button': fileDownloadButton,
        'image-file-display': imageFileDisplay
    },
    methods: {
        // from https://stackoverflow.com/a/9102270
        youtubeEmbedFromURL (url) {
            var regExp = /^.*(youtu\.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/
            var match = url.match(regExp)
            if (match && match[2].length === 11) {
                return 'https://www.youtube.com/embed/' + match[2] + '?rel=0&amp;showinfo=0'
            } else {
                return null
            }
        },
        checkChanges () {
            for (var i = 0; i < this.completeContent.length; i++) {
                if (this.completeContent[i].data !== null && this.completeContent[i].data !== '') {
                    return true
                }
            }
            return false
        }
    }
}
</script>
