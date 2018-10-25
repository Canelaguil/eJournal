<!--
    Loads a preview of an Entry-Template and returns the filled in data to
    the parent once it's saved.
-->
<template>
    <div>
        <b-card class="no-hover" :class="$root.getBorderClass($route.params.cID)">
            <h2 class="mb-2">{{ template.name }}</h2>
            <div v-if="description" v-html="description"/>
            <entry-fields :template="template" :completeContent="completeContent" :displayMode="false" :nodeID="nodeID"/>

            <b-alert :show="dismissCountDown" dismissible variant="secondary"
                @dismissed="dismissCountDown=0">
                Some fields are empty or incorrectly formatted.
            </b-alert>
            <b-button class="add-button float-right" @click="save">
                <icon name="paper-plane"/>
                Post Entry
            </b-button>
        </b-card>
    </div>
</template>

<script>
import icon from 'vue-awesome/components/Icon'
import entryFields from '@/components/entry/EntryFields.vue'

export default {
    props: ['template', 'nodeID', 'description'],
    data () {
        return {
            completeContent: [],
            dismissSecs: 3,
            dismissCountDown: 0,
            showDismissibleAlert: false
        }
    },
    watch: {
        template: function () {
            this.completeContent = []
            this.setContent()
        }
    },
    created () {
        this.setContent()
    },
    methods: {
        setContent: function () {
            for (var field of this.template.field_set) {
                this.completeContent.push({
                    data: null,
                    id: field.id
                })
            }
        },
        checkFilled: function () {
            for (var i = 0; i < this.completeContent.length; i++) {
                var content = this.completeContent[i]
                var field = this.template.field_set[i]
                if (field.required && !content.data) {
                    return false
                }
            }

            return true
        },
        checkChanges () {
            for (var i = 0; i < this.completeContent.length; i++) {
                if (this.completeContent[i].data !== null && this.completeContent[i].data !== '') {
                    return true
                }
            }
            return false
        },
        save: function () {
            if (this.checkFilled()) {
                this.$emit('content-template', this.completeContent)
            } else {
                this.dismissCountDown = this.dismissSecs
            }
        }
    },
    components: {
        icon,
        'entry-fields': entryFields
    }
}
</script>
