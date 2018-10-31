<template>
    <b-card :class="$root.getBorderClass($route.params.cID)">
        <b-row no-gutters class="multi-form">
            <b-col order="1" cols="3" class="d-flex align-items-center">
                <img class="student-card-portrait" :src="student.profile_picture">
            </b-col>
            <b-col order="2" cols="9" class="pl-3">
                <todo-square v-if="numMarkingNeeded > 0 && !hideTodo" class="float-right" :num="numMarkingNeeded"/>
                <b>{{ student.full_name }}</b> <span v-if="student.group">({{ student.group }})</span> <br/>
                {{ student.username }}
                <progress-bar v-if="!fullWidthProgress || $root.mdMax()" :currentPoints="this.stats.acquired_points" :totalPoints="this.stats.total_points"/>
            </b-col>
        </b-row>
        <progress-bar v-if="fullWidthProgress && $root.lg()"
                      :currentPoints="this.stats.acquired_points"
                      :totalPoints="this.stats.total_points"
                      :comparePoints="this.assignment && this.assignment.stats ? this.assignment.stats.average_points : -1"/>
    </b-card>
</template>

<script>
import progressBar from '@/components/assets/ProgressBar.vue'
import todoSquare from '@/components/assets/TodoSquare.vue'

export default {
    props: {
        'student': {
            required: true
        },
        'stats': {
            required: true
        },
        'hideTodo': {
            type: Boolean,
            default: false
        },
        'fullWidthProgress': {
            type: Boolean,
            default: false
        },
        'assignment': {
            required: false
        }
    },
    components: {
        'progress-bar': progressBar,
        'todo-square': todoSquare
    },
    computed: {
        numMarkingNeeded () {
            return this.stats.submitted - this.stats.graded
        }
    }
}
</script>

<style lang="sass">
@import '~sass/partials/shadows.sass'

.student-card-portrait
    @extend .shadow
    border-radius: 50% !important
    display: block
    margin: auto
    max-height: 100px
</style>
