<!--
    Component representing a node in the Timeline.
    Handles the compositing of circle and date subcomponents, its own style
    depending on state given by parent, and passes relevant parts of the state
    to the subcomponents.
-->

<template>
    <b-row class="node-container" @click="$emit('select-node', index)">
        <b-col cols="4" sm="1"/>
        <b-col cols="4" sm="5" class="d-flex h-100 align-items-center">
            <timeline-node-date :date="nodeDate" :selected="selected" :isDeadline="node.deadline != null"/>
        </b-col>
        <b-col cols="4" sm="5" class="d-flex h-100 align-items-center justify-content-center">
            <div class="time-line" :class="timeLineClass"></div>
            <timeline-node-circle class="position-absolute" :type="node.type" :text="node.target" :selected="selected" :nodeState="nodeState()"/>
        </b-col>
        <b-col cols="4" sm="1"/>
    </b-row>
</template>

<script>
import timelineNodeCircle from '@/components/timeline/TimelineNodeCircle.vue'
import timelineNodeDate from '@/components/timeline/TimelineNodeDate.vue'

export default {
    props: ['node', 'selected', 'index', 'last', 'edit'],
    components: {
        'timeline-node-date': timelineNodeDate,
        'timeline-node-circle': timelineNodeCircle
    },
    computed: {
        deadlineHasPassed () {
            var currentDate = new Date()
            var deadline = new Date(this.node.deadline)

            return currentDate > deadline
        },
        timeLineClass () {
            return {
                'top': this.index === -1,
                'bottom': this.last
            }
        },
        nodeDate () {
            if (this.node.deadline) {
                return this.node.deadline
            } else if (this.node.entry) {
                return this.node.entry.creation_date
            } else {
                return null
            }
        }
    },
    methods: {
        nodeState () {
            if (this.node.type === 's') {
                return 'start'
            } else if (this.node.type === 'n') {
                return 'end'
            } else if (this.node.type === 'a') {
                return 'add'
            } else if (this.edit || this.node.type === 'p') {
                return ''
            }

            var entry = this.node.entry
            var isGrader = this.$hasPermission('can_grade')

            if (entry && entry.published) {
                return 'graded'
            } else if (!entry && this.deadlineHasPassed) {
                return 'failed'
            } else if (!entry && !this.deadlineHasPassed) {
                return 'empty'
            } else if (!isGrader && entry && !entry.published) {
                return 'awaiting_grade'
            } else if (isGrader && entry && !entry.grade) {
                return 'needs_grading'
            } else if (isGrader && entry && !entry.published) {
                return 'needs_publishing'
            }

            return ''
        }
    }
}
</script>

<style lang="sass">
@import '~sass/modules/colors.sass'

.node-container
    height: 100px
    .time-line
        position: absolute
        width: 5px
        background-color: $theme-medium-grey
        height: 100px
        &.top
            height: 50px
            top: 50px
        &.bottom
            height: 50px
            bottom: 50px
</style>
