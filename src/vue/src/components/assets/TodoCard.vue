<template>
    <b-card :class="$root.getBorderClass(course.id)">
        <todo-square
            v-if="deadline.stats && deadline.stats.unpublished"
            :num="deadline.stats.needs_marking + deadline.stats.unpublished"
            class="float-right" />

        <h5>{{ deadline.name }}</h5>
        <b-badge
            v-if="!deadline.is_published"
            class="ml-2 mt-2">
            Unpublished
        </b-badge>
        <br />
        {{ course.abbreviation }}

        <h6 v-if="this.deadline.deadline && (this.deadline.stats.needs_marking + deadline.stats.unpublished) ">
            <template>{{ timeLeft[1] }} ago</template>
            <span class="right">{{ $root.beautifyDate(deadline.deadline) }}</span>
        </h6>
        <h6 v-else-if="this.deadline.deadline">
            <template v-if="timeLeft[0] < 0">Due in {{ timeLeft[1] }}</template>
            <span class="red" v-else>{{ timeLeft[1] }} late</span>
            <span class="right">{{ $root.beautifyDate(deadline.deadline) }}</span>
        </h6>
    </b-card>
</template>

<script>
import todoSquare from '@/components/assets/TodoSquare.vue'

export default {
    props: ['deadline', 'course'],
    components: {
        'todo-square': todoSquare
    },
    computed: {
        timeLeft: function () {
            if (!this.deadline.deadline) { return '' }
            let dateNow = new Date()
            let dateFuture = new Date(this.deadline.deadline)

            // get total seconds between the times
            let delta = Math.abs(dateFuture - dateNow) / 1000
            let dir = dateNow - dateFuture

            // calculate (and subtract) whole days
            let days = Math.floor(delta / 86400)
            delta -= days * 86400

            // calculate (and subtract) whole hours
            let hours = Math.floor(delta / 3600) % 24
            delta -= hours * 3600

            // calculate (and subtract) whole minutes
            let minutes = Math.floor(delta / 60) % 60
            delta -= minutes * 60

            if (days) {
                return [dir, days > 1 ? days + ' days' : '1 day']
            }

            if (hours) {
                return [dir, hours > 1 ? hours + ' hours' : '1 hour']
            }

            return [dir, minutes > 1 ? minutes + ' minutes' : '1 minute']
        }
    }
}
// 2019-07-16T04:29:18
// 2018-11-15T10:04:52.543
</script>

<style lang="sass" scoped>
@import "~sass/modules/colors.sass"

.right
    float: right
.red
    color: $theme-red

h5
    display: inline-block

p
    text-align: right
    font-size: 20px
    color: $theme-blue
    margin-bottom: 0px
</style>
