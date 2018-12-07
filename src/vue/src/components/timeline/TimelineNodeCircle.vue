<!--
    Mini component representing the circle for a node in the Timeline.
    Handles its own style depending on a state given by parent.
-->

<template>
    <div class="timeline-node-circle-border">
        <div class="timeline-node-circle unselectable" data-toggle="tooltip" :title="nodeTitle" :class="nodeClass">
            <icon v-if="this.type !== 'p'" :name="iconName" :class="iconClass" :scale="iconScale"/>
            <div v-else class="timeline-node-circle-text">{{ text }}</div>
        </div>
    </div>
</template>

<script>
import icon from 'vue-awesome/components/Icon'

export default {
    props: ['type', 'text', 'selected', 'nodeState'],
    computed: {
        nodeClass () {
            return {
                'enc-start': this.type === 's',
                'enc-end': this.type === 'n',
                'enc-entry': this.type === 'e',
                'enc-deadline': this.type === 'd',
                'enc-progress': this.type === 'p',
                'enc-add': this.type === 'a',
                'enc-selected': this.selected
            }
        },
        iconName () {
            switch (this.nodeState) {
            case 'graded':
                return 'check'
            case 'failed':
                return 'clock-o'
            case 'awaiting_grade':
                return 'hourglass-half'
            case 'needs_grading':
                return 'exclamation'
            case 'needs_publishing':
                return 'eye'
            case 'add':
                return 'plus'
            case 'start':
                return 'flag'
            case 'end':
                return 'flag-checkered'
            }

            return 'calendar'
        },
        nodeTitle () {
            switch (this.nodeState) {
            case 'graded':
                return 'Graded'
            case 'failed':
                return 'Missed deadline'
            case 'awaiting_grade':
                return 'Awaiting grade'
            case 'needs_grading':
                return 'Needs grading'
            case 'needs_publishing':
                return 'Awaiting publishment'
            case 'add':
                return 'Add new entry'
            case 'start':
            case 'end':
                return 'Assignment details'
            }

            return 'Deadline'
        },
        iconClass () {
            switch (this.nodeState) {
            case 'graded':
                return 'fill-green'
            case 'failed':
                return 'fill-red'
            }

            return 'fill-white'
        },
        iconScale () {
            if (this.type === 'a') {
                if (this.selected) {
                    return '1.5'
                } else {
                    return '1'
                }
            }
            if (this.selected) {
                return '2'
            } else {
                return '1.5'
            }
        }
    },
    components: {
        icon
    }
}
</script>

<style lang="sass">
@import '~sass/modules/colors.sass'
@import '~sass/partials/shadows.sass'

.timeline-node-circle-border
    border-radius: 50% !important
    background-color: white
    padding: 5px

.timeline-node-circle
    @extend .small-shadow
    width: 55px
    height: 55px
    border-radius: 50% !important
    display: flex
    align-items: center
    justify-content: center
    transition: all 0.6s cubic-bezier(.25,.8,.25,1)
    &:not(.enc-selected)
        cursor: pointer
    &.enc-selected
        width: 75px
        height: 75px
    &.enc-add
        width: 45px
        height: 45px
    &.enc-selected.enc-add
        width: 55px
        height: 55px
    &.enc-entry, &.enc-deadline
        background-color: $theme-medium-grey
    &.enc-start
        background-color: $theme-green
    &.enc-end
        background-color: $theme-green
    &.enc-add
        background-color: $theme-blue
    &.enc-progress
        background-color: $theme-orange
    &.enc-selected
        background-color: $theme-dark-blue
    svg
        transition: all 0.6s cubic-bezier(.25,.8,.25,1)
    .timeline-node-circle-text
        color: white
        font-family: 'Roboto Condensed', sans-serif
        font-weight: bold
        font-size: 1.5em
</style>
