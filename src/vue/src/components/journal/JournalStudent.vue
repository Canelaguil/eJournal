<template>
    <b-row class="outer-container-timeline-page" no-gutters>
        <b-col md="12" lg="8" xl="9" class="inner-container-timeline-page">
            <b-col md="12" lg="auto" xl="4" class="left-content-timeline-page">
                <bread-crumb v-if="$root.lgMax()">&nbsp;</bread-crumb>
                <timeline @select-node="selectNode" :selected="currentNode" :nodes="nodes"/>
            </b-col>

            <b-col md="12" lg="auto" xl="8" class="main-content-timeline-page">
                <bread-crumb v-if="$root.xl()">&nbsp;</bread-crumb>
                <div v-if="nodes.length > currentNode && currentNode !== -1">
                    <div v-if="nodes[currentNode].type == 'e'">
                        <entry-node
                            ref="entry-template-card"
                            @edit-node="adaptData"
                            @delete-node="deleteNode"
                            :cID="cID"
                            :entryNode="nodes[currentNode]"/>
                    </div>
                    <div v-else-if="nodes[currentNode].type == 'd'">
                        <div v-if="nodes[currentNode].entry !== null">
                            <entry-node :cID="cID" ref="entry-template-card" @edit-node="adaptData"
                            @delete-node="deleteNode" :entryNode="nodes[currentNode]"/>
                        </div>
                        <div v-else>
                            <entry-preview v-if="checkDeadline()" ref="entry-prev" @content-template="fillDeadline" :template="nodes[currentNode].template" :nodeID="nodes[currentNode].nID" :description="nodes[currentNode].description"/>
                            <b-card v-else class="no-hover" :class="$root.getBorderClass($route.params.cID)">
                                <h2 class="mb-2">{{nodes[currentNode].template.name}}</h2>
                                <b>The deadline has passed. You can not submit an entry anymore.</b>
                            </b-card>
                        </div>
                    </div>
                    <div v-else-if="nodes[currentNode].type == 'a'">
                        <add-card @info-entry="addNode" ref="add-card-ref" :addNode="nodes[currentNode]"/>
                    </div>
                    <div v-else-if="nodes[currentNode].type == 'p'">
                        <b-card class="no-hover" :class="getProgressBorderClass()">
                            <h2 class="mb-2">Progress: {{ nodes[currentNode].target }} points</h2>
                            <span v-if="progressPointsLeft > 0">
                                <b>{{ progressNodes[nodes[currentNode].nID] }}</b> out of <b>{{ nodes[currentNode].target }}</b> points.<br/>
                                <b>{{ progressPointsLeft }}</b> more required before <b>{{ $root.beautifyDate(nodes[currentNode].deadline) }}</b>.
                            </span>
                            <div v-if="nodes[currentNode].description !== null">
                                <h2 class="mb-2">Description</h2>
                                <div v-html="nodes[currentNode].description"/>
                            </div>
                        </b-card>
                    </div>
                </div>
                <journal-start-card v-else-if="currentNode === -1" :assignment="assignment" :student="true"/>
                <journal-end-card v-else :assignment="assignment" :student="true"/>
            </b-col>
        </b-col>

        <b-col md="12" lg="4" xl="3" class="right-content-timeline-page right-content">
            <h3>Journal progress</h3>
            <b-card class="no-hover" :class="$root.getBorderClass($route.params.cID)">
                <progress-bar v-if="journal.stats"
                              :currentPoints="journal.stats.acquired_points"
                              :totalPoints="journal.stats.total_points"
                              :comparePoints="assignment.stats ? assignment.stats.average_points : -1" />
            </b-card>

            <transition name="fade">
                <b-button
                    v-if="$root.lgMax() && addIndex > -1 && currentNode !== addIndex"
                    @click="currentNode = addIndex"
                    class="fab">
                    <icon name="plus" scale="1.5"/>
                </b-button>
            </transition>
        </b-col>
    </b-row>
</template>

<script>
import contentColumns from '@/components/columns/ContentColumns.vue'
import entryNode from '@/components/entry/EntryNode.vue'
import entryPreview from '@/components/entry/EntryPreview.vue'
import addCard from '@/components/journal/AddCard.vue'
import timeline from '@/components/timeline/Timeline.vue'
import breadCrumb from '@/components/assets/BreadCrumb.vue'
import progressBar from '@/components/assets/ProgressBar.vue'
import journalStartCard from '@/components/journal/JournalStartCard.vue'
import journalEndCard from '@/components/journal/JournalEndCard.vue'
import icon from 'vue-awesome/components/Icon'

import journalAPI from '@/api/journal'
import assignmentAPI from '@/api/assignment'
import entryAPI from '@/api/entry'

export default {
    props: ['cID', 'aID', 'jID'],
    data () {
        return {
            currentNode: -1,
            editedData: ['', ''],
            nodes: [],
            journal: {},
            progressNodes: {},
            progressPointsLeft: 0,
            assignment: ''
        }
    },
    created () {
        assignmentAPI.get(this.aID, this.cID)
            .then(assignment => {
                this.assignment = assignment

                if ((!this.assignment.unlock_date || new Date(this.assignment.unlock_date) < new Date()) &&
                    (!this.assignment.lock_date || new Date(this.assignment.lock_date) > new Date())) {
                    journalAPI.getNodes(this.jID)
                        .then(nodes => {
                            this.nodes = nodes
                            if (this.$route.query.nID !== undefined) {
                                this.currentNode = this.findEntryNode(parseInt(this.$route.query.nID))
                            }

                            for (var node of this.nodes) {
                                if (node.type === 'p') {
                                    this.progressPoints(node)
                                }
                            }
                        })
                        .catch(error => { this.$toasted.error(error.response.data.description) })
                }
            })
            .catch(_ => this.$toasted.error('Error while loading assignment data.'))

        journalAPI.get(this.jID)
            .then(journal => { this.journal = journal })
            .catch(_ => this.$toasted.error('Error while loading journal data.'))
    },
    watch: {
        currentNode: function () {
            if (this.currentNode !== -1 && this.currentNode !== this.nodes.length && this.nodes[this.currentNode].type === 'p') {
                this.progressPoints(this.nodes[this.currentNode])
                this.progressPointsLeft = this.nodes[this.currentNode].target - this.progressNodes[this.nodes[this.currentNode].nID]
            }
        }
    },
    methods: {
        adaptData (editedData) {
            this.nodes[this.currentNode] = editedData
            entryAPI.update(this.nodes[this.currentNode].entry.id, { content: editedData.entry.content })
                .then(entry => { this.nodes[this.currentNode].entry = entry })
                .catch(error => { this.$toasted.error(error.response.data.description) })
        },
        deleteNode () {
            entryAPI.delete(this.nodes[this.currentNode].entry.id)
                .then(data => {
                    this.$toasted.success(data.description)
                    if (this.nodes[this.currentNode].type === 'd') {
                        this.nodes[this.currentNode].entry = null
                        this.currentNode = 0
                    } else {
                        this.nodes.splice(this.currentNode, 1)
                    }
                })
                .catch(error => { this.$toasted.error(error.response.data.description) })
        },
        discardChanges () {
            /*  Checks the node and depending of the type of node
             *  it will look for possible unsaved changes.
             *  If there are unsaved changes a confirmation will be asked.
             */
            if (this.currentNode !== -1 && this.currentNode !== this.nodes.length && this.nodes[this.currentNode].type === 'd' && this.nodes[this.currentNode].entry === null && this.checkDeadline()) {
                if (this.$refs['entry-prev'].checkChanges() && !confirm('Progress will not be saved if you leave. Do you wish to continue?')) {
                    return false
                }
            }

            if (this.currentNode !== -1 && this.currentNode !== this.nodes.length && this.nodes[this.currentNode].type === 'd' && this.nodes[this.currentNode].entry !== null) {
                if (this.$refs['entry-template-card'].saveEditMode === 'Save' && !confirm('Progress will not be saved if you leave. Do you wish to continue?')) {
                    return false
                }
            }

            if (this.currentNode !== -1 && this.currentNode !== this.nodes.length && this.nodes[this.currentNode].type === 'a') {
                if (this.$refs['add-card-ref'].checkChanges() && !confirm('Progress will not be saved if you leave. Do you wish to continue?')) {
                    return false
                }
            }

            if (this.currentNode !== -1 && this.currentNode !== this.nodes.length && this.nodes[this.currentNode].type === 'e') {
                if (this.$refs['entry-template-card'].saveEditMode === 'Save' && !confirm('Progress will not be saved if you leave. Do you wish to continue?')) {
                    return false
                }
            }

            return true
        },
        selectNode ($event) {
            /* Function that prevents you from instant leaving an EntryNode
             * or a DeadlineNode when clicking on a different node in the
             * timeline. */
            if ($event === this.currentNode) {
                return this.currentNode
            }

            if (this.discardChanges()) {
                this.currentNode = $event
            }
        },
        addNode (infoEntry) {
            entryAPI.create({
                journal_id: this.jID,
                template_id: infoEntry[0].id,
                content: infoEntry[1]
            })
                .then(data => {
                    this.nodes = data.nodes
                    this.currentNode = data.added
                })
                .catch(error => { this.$toasted.error(error.response.data.description) })
        },
        fillDeadline (data) {
            entryAPI.create({
                journal_id: this.jID,
                template_id: this.nodes[this.currentNode].template.id,
                content: data,
                node_id: this.nodes[this.currentNode].nID
            })
                .then(data => {
                    this.nodes = data.nodes
                    this.currentNode = data.added
                })
                .catch(error => { this.$toasted.error(error.response.data.description) })
        },
        progressPoints (progressNode) {
            /* The function will update a given progressNode by
             * going through all the nodes and count the published grades
             * so far. */
            var tempProgress = 0
            for (var node of this.nodes) {
                if (node.nID === progressNode.nID) {
                    break
                }

                if (node.type === 'e' || node.type === 'd') {
                    if (node.entry && node.entry.grade && node.entry.grade !== '0') {
                        tempProgress += parseInt(node.entry.grade)
                    }
                }
            }

            this.progressNodes[progressNode.nID] = tempProgress
        },
        getProgressBorderClass () {
            return this.progressPointsLeft > 0 ? 'red-border' : 'green-border'
        },
        findEntryNode (nodeID) {
            for (var i = 0; i < this.nodes.length; i++) {
                if (this.nodes[i].nID === nodeID) {
                    return i
                }
            }
            return 0
        },
        checkDeadline () {
            var currentDate = new Date()
            var deadline = new Date(this.nodes[this.currentNode].deadline)

            return currentDate <= deadline
        }
    },
    computed: {
        addIndex () {
            return this.nodes.findIndex(function (node) {
                return node.type === 'a'
            })
        }
    },
    components: {
        'content-columns': contentColumns,
        'bread-crumb': breadCrumb,
        'add-card': addCard,
        timeline,
        icon,
        'entry-node': entryNode,
        'entry-preview': entryPreview,
        'progress-bar': progressBar,
        'journal-start-card': journalStartCard,
        'journal-end-card': journalEndCard
    }
}
</script>
