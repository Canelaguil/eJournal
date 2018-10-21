<!--
    Editor for the currently selected preset in the format editor.
    Edits the preset prop directly.
    Various (many!) elements emit a changed event to track whether unsaved changes exist.
-->

<template>
    <b-card class="no-hover overflow-x-hidden" :class="$root.getBorderClass($route.params.cID)">
        <h2 class="d-inline multi-form">Preset</h2>
        <b-button @click.prevent="emitDeletePreset" class="delete-button float-right multi-form">
            <icon name="trash"/>
            Remove
        </b-button>

        <h2 class="field-heading">Preset Type</h2>
        <b-row>
            <b-col md="6">
                <b-card
                    @click="changePresetType('d')"
                    :class="{'unselected': currentPreset.type !== 'd'}">
                    <b-button
                        class="change-button preset-type-button float-left mr-3 mt-2 no-hover"
                        :class="{'selected': currentPreset.type === 'd'}">
                        <icon name="calendar" scale="1.8"/>
                    </b-button>
                    <div>
                        <b>Entry</b><br/>
                        A preset that has to be filled in before a set deadline.
                    </div>
                </b-card>
            </b-col>
            <b-col md="6">
                <b-card
                    @click="changePresetType('p')"
                    :class="{'unselected': currentPreset.type !== 'p'}">
                    <b-button
                        class="change-button preset-type-button float-left mr-3 mt-2 no-hover"
                        :class="{'selected': currentPreset.type === 'p'}">
                        <icon name="flag-checkered" scale="1.8"/>
                    </b-button>
                    <div>
                        <b>Progress</b><br/>
                        A point target that has to be met before a set deadline.
                    </div>
                </b-card>
            </b-col>
        </b-row>

        <h2 class="field-heading">Deadline</h2>
        <flat-pickr class="theme-input multi-form full-width" v-model="currentPreset.deadline" :config="$root.flatPickrTimeConfig"/>

        <h2 class="field-heading">Description</h2>
        <b-textarea class="multi-form theme-input" v-model="currentPreset.description" placeholder="Description"/>

        <div v-if="currentPreset.type === 'd'">
            <h2 class="field-heading">Preset Template</h2>
            <b-form-select v-model="currentPreset.template" class="multi-form">
                <option disabled value="">Please select a template</option>
                <option v-for="template in templates" :key="template.t.tID" :value="template.t">
                    {{ template.t.name }}
                </option>
            </b-form-select>
            <div v-if="currentPreset !== null">
                <h2 class="field-heading">Preview of the {{ currentPreset.template.name }} template</h2>
                <template-preview :template="currentPreset.template"/>
            </div>
        </div>
        <div v-else-if="currentPreset.type === 'p'">
            <h2 class="field-heading">Point Target</h2>
            <b-input type="number" class="theme-input" v-model="currentPreset.target" placeholder="Amount of points"/>
        </div>
    </b-card>
</template>

<script>
import templatePreview from '@/components/template/TemplatePreview.vue'
import icon from 'vue-awesome/components/Icon'

export default {
    props: ['currentPreset', 'templates'],
    data () {
        return {
            templateNames: [],
            prevID: this.currentPreset.id
        }
    },
    watch: {
        currentPreset: {
            handler: function (newPreset) {
                if (newPreset.id === this.prevID) {
                    this.$emit('changed')
                }

                this.prevID = newPreset.id
            },
            deep: true
        }
    },
    methods: {
        emitDeletePreset () {
            this.$emit('changed')
            if (confirm('Are you sure you want to remove this preset from this format?')) {
                this.$emit('delete-preset')
            }
        },
        // Type-specific fields should be set or deleted
        changePresetType (type) {
            this.currentPreset.type = type
            if (type !== 'p') {
                this.currentPreset.target = ''
            }
            if (type === 'd') {
                if (this.templates[0]) {
                    this.$set(this.currentPreset, 'template', this.templates[0].t)
                } else {
                    this.$set(this.currentPreset, 'template', {})
                }
            }
        }
    },
    components: {
        'template-preview': templatePreview,
        icon
    }
}
</script>
