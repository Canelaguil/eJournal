<template>
    <div>
        <h4 class="progress-percentage float-right">{{ progressPercentage }}%</h4>
        <h5 class="progress-percentage"><b>{{ currentPoints }}</b> Points</h5><br/>
        <span v-if="comparePoints">{{ message }}</span>
        <b-progress class="shadow progress-bar-box" color="white" :max="totalPoints">
            <b-progress-bar class="own-bar"
                            :value="zeroIfNull(comparePoints === -1 ? currentPoints : Math.min(currentPoints, comparePoints))"/>
            <b-progress-bar class="compare-bar"
                            :value="Math.abs(comparePoints - currentPoints)"
                            v-if="comparePoints !== -1 && comparePoints > currentPoints"/>
            <b-progress-bar class="compare-bar ahead"
                            :value="Math.abs(comparePoints - currentPoints)"
                            v-else-if="comparePoints !== -1"/>
        </b-progress>
    </div>
</template>

<script>
export default {
    props: {
        'currentPoints': {
            required: true
        },
        'totalPoints': {
            required: true
        },
        'comparePoints': {
            default: -1
        }
    },
    methods: {
        zeroIfNull (val) {
            return (val === null) ? 0 : val
        }
    },
    computed: {
        progressPercentage () {
            return this.zeroIfNull(this.currentPoints / this.totalPoints * 100).toFixed(0)
        },
        difference () {
            return Math.round(Math.abs((this.comparePoints - this.currentPoints) * 100)) / 100
        },
        message () {
            if (this.comparePoints === -1) {
                return null
            }
            var message = ''

            // On average
            if (this.difference === 0) {
                message += 'Same as average'
            } else {
                if (this.difference === 1) {
                    message += '1 point '
                } else {
                    message += this.difference + ' points '
                }
                // Ahead or behind
                if (this.comparePoints <= this.currentPoints) {
                    message += 'above average'
                } else {
                    message += 'below average'
                }
            }
            return message
        }
    }
}
</script>

<style lang="sass">
@import '~sass/modules/colors.sass'

.progress-percentage
    display: inline
    border: none
    padding: 0px !important
    text-align: right

.progress-bar-box
    margin-top: 10px
    height: 20px
    background-color: white

.own-bar
    background-color: $theme-blue !important
.compare-bar
    background-color: $theme-orange !important
    &.ahead
        background-color: $theme-green !important
</style>
