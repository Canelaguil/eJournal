<!--
    Format Editor view.
    Lists all templates used within the assignment.
    Template availability for adding by the student can be toggled on a per-template basis.
    Presets are given in a list format, same as the journal view.
-->

<template>
    <b-row class="outer-container-timeline-page" no-gutters>
        <b-col md="12" lg="8" xl="9" class="inner-container-timeline-page">
            <b-col md="12" lg="auto" xl="4" class="left-content-timeline-page">
                <bread-crumb v-if="$root.lgMax()" class="main-content">&nbsp;</bread-crumb>
                <timeline @select-node="selectNode" @add-node="addNode" :selected="currentNode" :nodes="nodes" :edit="true"/>
            </b-col>

            <b-col md="12" lg="auto" xl="8" class="main-content-timeline-page">
                <bread-crumb v-if="$root.xl()">&nbsp;</bread-crumb>
                <!--
                    Fill in the template using the corresponding data
                    of the entry
                . -->
                <selected-node-card
                    :class="{ 'input-disabled' : saveRequestInFlight }"
                    v-if="nodes.length > 0 && currentNode !== -1 && currentNode !== nodes.length"
                    ref="entry-template-card"
                    :currentPreset="nodes[currentNode]"
                    :templates="templatePool"
                    @deadline-changed="sortList"
                    @delete-preset="deletePreset"
                    @changed="isChanged = true"/>

                <assignment-details-card
                    :class="{ 'input-disabled' : saveRequestInFlight }"
                    v-else-if="currentNode === -1"
                    :assignmentDetails="assignmentDetails"
                    @changed="isChanged = true"/>

                <b-card v-else-if="currentNode === nodes.length" class="no-hover" :class="$root.getBorderClass($route.params.cID)">
                    <h2>End of assignment</h2>
                    <p>This is the end of the assignment.</p>
                </b-card>

                <main-card v-else class="no-hover" :line1="'No presets in format'" :class="'grey-border'"/>

                <b-modal
                    ref="templateModal"
                    size="lg"
                    title="Edit template"
                    hide-footer>
                        <template-editor :template="templateBeingEdited"/>
                </b-modal>
            </b-col>
        </b-col>

        <b-col md="12" lg="4" xl="3" class="right-content-timeline-page right-content">
            <h3>Entry Templates</h3>
            <div :class="{ 'input-disabled' : saveRequestInFlight }">
                <available-template-card
                    v-for="template in templatePool"
                    :key="template.t.id"
                    @click.native="showTemplateModal(template)"
                    :template="template"
                    @delete-template="deleteTemplate"/>
                <b-button class="add-button grey-background full-width multi-form" @click="showTemplateModal(newTemplate())">
                    <icon name="plus"/>
                    Create New Template
                </b-button>
            </div>
        </b-col>

        <transition name="fade">
            <b-button
                v-if="isChanged"
                @click.prevent.stop="saveFormat"
                :class="{ 'input-disabled' : saveRequestInFlight }"
                class="add-button fab">
                <icon name="save" scale="1.5"/>
            </b-button>
        </transition>
    </b-row>
</template>

<script>
import contentColumns from '@/components/columns/ContentColumns.vue'
import mainCard from '@/components/assets/MainCard.vue'
import timeline from '@/components/timeline/Timeline.vue'
import breadCrumb from '@/components/assets/BreadCrumb.vue'
import FormatEditAssignmentDetailsCard from '@/components/format/FormatEditAssignmentDetailsCard.vue'
import formatEditAvailableTemplateCard from '@/components/format/FormatEditAvailableTemplateCard.vue'
import formatEditSelectTemplateCard from '@/components/format/FormatEditSelectTemplateCard.vue'
import templateEdit from '@/components/template/TemplateEdit.vue'
import icon from 'vue-awesome/components/Icon'
import formatAPI from '@/api/format.js'

export default {
    name: 'FormatEdit',
    props: ['cID', 'aID'],
    /* Main data representations:
       templates, presets, unused templates: as received.
       templatePool: the list of used templates. Elements are meta objects with a t field storing the template,
            available field storing student availability, boolean updated field.
       nodes: processed copy of presets.
       deletedTemplates, deletedPresets: stores deleted objects for db communication
       isChanged: stores whether the user has made any changes
       saveRequestInFlight: stores whether a request to save is in flight, should not allow changes as that would
            create desync between server and local (format is reloaded after save response, local changes lost)
    */
    data () {
        return {
            currentNode: -1,

            assignmentDetails: {},

            templates: [],
            presets: [],
            unusedTemplates: [],

            templatePool: [],
            nodes: [],

            isChanged: false,
            saveRequestInFlight: false,

            templateBeingEdited: {
                'field_set': [],
                'name': '',
                'id': -1
            },
            wipTemplateId: -1,

            deletedTemplates: [],
            deletedPresets: []
        }
    },
    created () {
        formatAPI.get(this.aID)
            .then(data => {
                this.saveFromDB(data)
                this.convertFromDB()
            })
            .then(_ => { this.isChanged = false })
            .catch(error => { this.$toasted.error(error.response.data.description) })

        window.addEventListener('beforeunload', e => {
            if (this.$route.name === 'FormatEdit' && this.isChanged) {
                var dialogText = 'Unsaved changes will be lost if you leave. Do you wish to continue?'
                e.returnValue = dialogText
                return dialogText
            }
        })
    },
    watch: {
        templatePool: {
            handler: function () {
                if (!this.saveRequestInFlight) {
                    this.isChanged = true
                }
            },
            deep: true
        }
    },
    methods: {
        deletePreset () {
            if (typeof this.nodes[this.currentNode].id !== 'undefined') {
                this.deletedPresets.push(this.nodes[this.currentNode])
            }
            this.nodes.splice(this.currentNode, 1)
            this.currentNode = Math.min(this.currentNode, this.nodes.length - 1)
        },
        deleteTemplate (template) {
            if (typeof template.t.id !== 'undefined') {
                this.deletedTemplates.push(template.t)
            }
            this.templatePool.splice(this.templatePool.indexOf(template), 1)
        },
        // Used to sort the list when dates are changed. Updates the currentNode index accordingly
        sortList () {
            var temp = this.nodes[this.currentNode]
            this.nodes.sort((a, b) => { return new Date(a.deadline) - new Date(b.deadline) })
            this.currentNode = this.nodes.indexOf(temp)
        },
        newTemplate () {
            return {
                t: {
                    'field_set': [{
                        'type': 'rt',
                        'title': 'Entry',
                        'description': '',
                        'location': 0,
                        'required': true
                    }],
                    'name': 'Untitled Template',
                    'id': this.wipTemplateId--
                },
                available: true
            }
        },
        // Shows the modal and sets updated flag on template
        showTemplateModal (template) {
            template.updated = true
            if (!this.templatePool.includes(template)) {
                this.templatePool.push(template)
            }
            this.templateBeingEdited = template.t
            this.$refs['templateModal'].show()
        },
        hideModal (ref) {
            this.$refs[ref].hide()
        },
        selectNode ($event) {
            if ($event === this.currentNode) {
                return
            }

            this.currentNode = $event
        },
        newDate () {
            return new Date().toISOString().split('T')[0].slice(0, 10) + ' ' + new Date().toISOString().split('T')[1].slice(0, 5)
        },
        addNode () {
            var deadline = this.assignmentDetails.due_date

            if (!deadline) {
                deadline = this.newDate()
            }

            var newNode = {
                'type': 'p',
                'deadline': deadline,
                'target': this.assignmentDetails.points_possible
            }

            this.nodes.push(newNode)
            this.currentNode = this.nodes.indexOf(newNode)
            this.sortList()
            this.isChanged = true

            this.$toasted.success('Added new node to format.')
        },
        // Do client side validation and save to DB
        saveFormat () {
            var missingAssignmentName = false
            var missingPointMax = false

            var deadlineAfterDueDate = false
            var invalidDate = false
            var invalidTemplate = false
            var invalidTarget = false

            var lastTarget
            var targetsOutOfOrder = false

            var templatePoolIds = []
            for (var template of this.templatePool) {
                templatePoolIds.push(template.t.id)
            }

            if (!/\S/.test(this.assignmentDetails.name)) {
                missingAssignmentName = true
                this.$toasted.error('Assignment name is missing. Please check the format and try again.')
            }

            if (!missingPointMax && isNaN(parseInt(this.assignmentDetails.points_possible))) {
                missingPointMax = true
                this.$toasted.error('Points possible is missing. Please check the format and try again.')
            }

            for (var node of this.nodes) {
                if (!targetsOutOfOrder && node.type === 'p') {
                    if (lastTarget && node.target < lastTarget) {
                        targetsOutOfOrder = true
                        this.$toasted.error('Some preset targets are out of order. Please check the format and try again.')
                    }
                    lastTarget = node.target
                }

                if (!invalidDate && isNaN(Date.parse(node.deadline))) {
                    invalidDate = true
                    this.$toasted.error('One or more presets have an invalid deadline. Please check the format and try again.')
                }
                if (!invalidTemplate && node.type === 'd' && typeof node.template.id === 'undefined') {
                    invalidTemplate = true
                    this.$toasted.error('One or more presets have an invalid template. Please check the format and try again.')
                }
                if (!invalidTemplate && node.type === 'd' && node.template.id && !templatePoolIds.includes(node.template.id)) {
                    invalidTemplate = true
                    this.$toasted.error('One or more presets have an invalid template. Please check the format and try again.')
                }
                if (!invalidTarget && node.type === 'p' && isNaN(parseInt(node.target))) {
                    invalidTarget = true
                    this.$toasted.error('One or more presets have an invalid target. Please check the format and try again.')
                }
                if (!deadlineAfterDueDate && this.assignmentDetails.due_date &&
                    Date.parse(node.deadline) > Date.parse(this.assignmentDetails.due_date)) {
                    deadlineAfterDueDate = true
                    this.$toasted.error('One or more presets have a deadline after the assignment due date. Please check the format and try again.')
                }
            }

            if (missingAssignmentName | missingPointMax | invalidDate | invalidTemplate | invalidTarget | targetsOutOfOrder |
                deadlineAfterDueDate) {
                return
            }
            this.saveRequestInFlight = true
            this.convertToDB()
            formatAPI.update(this.aID, {
                'assignment_details': this.assignmentDetails,
                'templates': this.templates,
                'presets': this.presets,
                'unused_templates': this.unusedTemplates,
                'removed_templates': this.deletedTemplates,
                'removed_presets': this.deletedPresets
            })
                .then(data => {
                    this.saveFromDB(data)
                    this.convertFromDB()
                    this.saveRequestInFlight = false
                    this.$toasted.success('New format saved')
                    this.$nextTick(function () {
                        this.isChanged = false
                    })
                })
                .catch(error => { this.$toasted.error(error.response.data.description) })
        },
        customisePage () {
            this.$toasted.info('Wishlist: Customise page')
        },
        saveFromDB (data) {
            this.assignmentDetails = data.assignment_details
            this.templates = data.format.templates
            this.presets = data.format.presets
            this.unusedTemplates = data.format.unused_templates
            this.deletedTemplates = []
            this.deletedPresets = []
        },
        // Utility func to translate from db format to internal
        convertFromDB () {
            var idInPool = []
            var tempTemplatePool = {}

            for (var template of this.templates) {
                idInPool.push(template.id)
                tempTemplatePool[template.id] = { t: template, available: true }
            }
            for (var preset of this.presets) {
                if (preset.type === 'd') {
                    if (!idInPool.includes(preset.template.id)) {
                        idInPool.push(preset.template.id)
                        tempTemplatePool[preset.template.id] = { t: preset.template, available: false }
                    } else {
                        preset.template = tempTemplatePool[preset.template.id].t
                    }
                }
            }
            for (var unusedTemplate of this.unusedTemplates) {
                idInPool.push(unusedTemplate.id)
                tempTemplatePool[unusedTemplate.id] = { t: unusedTemplate, available: false }
            }

            this.templatePool = Object.values(tempTemplatePool).sort((a, b) => { return a.t.id - b.t.id })

            this.nodes = this.presets.slice()
            this.nodes.sort((a, b) => { return new Date(a.deadline) - new Date(b.deadline) })
        },
        // Utility func to translate from internal format to db
        convertToDB () {
            this.presets = this.nodes.slice()

            this.templates = []
            this.unusedTemplates = []

            for (var template of this.templatePool) {
                template.t.updated = template.updated
                if (template.available) {
                    this.templates.push(template.t)
                } else {
                    this.unusedTemplates.push(template.t)
                }
            }
        }
    },
    components: {
        'content-columns': contentColumns,
        'bread-crumb': breadCrumb,
        'assignment-details-card': FormatEditAssignmentDetailsCard,
        'available-template-card': formatEditAvailableTemplateCard,
        'selected-node-card': formatEditSelectTemplateCard,
        'template-editor': templateEdit,
        'main-card': mainCard,
        timeline,
        icon
    },

    // Prompts user
    beforeRouteLeave (to, from, next) {
        if (this.isChanged && !confirm('Unsaved changes will be lost if you leave. Do you wish to continue?')) {
            next(false)
            return
        }

        next()
    }
}
</script>

<style lang="sass">
@import '~sass/partials/timeline-page-layout.sass'
</style>
